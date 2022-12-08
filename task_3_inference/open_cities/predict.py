import os
from glob import glob

import addict
import segmentation_models_pytorch as smp
import torch
import ttach

from training.config import parse_config
from training.predictor import TorchTifPredictor
from training.runner import GPUNormRunner


def get_model(architecture, init_params):
    model_class = smp.__dict__[architecture]
    return model_class(**init_params)


class EnsembleModel(torch.nn.Module):
    """Ensemble of torch models, pass tensor through all models and average results"""

    def __init__(self, models: list):
        super().__init__()
        self.models = torch.nn.ModuleList(models)

    def forward(self, x):
        result = None
        for model in self.models:
            y = model(x)
            if result is None:
                result = y
            else:
                result += y
        result /= torch.tensor(len(self.models)).to(result.device)
        return result


def model_from_config(path: str):
    """Create model from configuration specified in config file and load checkpoint weights"""
    cfg = addict.Dict(parse_config(config=path))  # read and parse config file
    init_params = cfg.model.init_params  # extract model initialization parameters
    init_params[
        "encoder_weights"
    ] = None  # because we will load pretrained weights for whole model
    model = get_model(architecture=cfg.model.architecture, init_params=init_params)
    checkpoint_path = os.path.join(cfg.logdir, "checkpoints", "best.pth")
    state_dict = torch.load(checkpoint_path)["state_dict"]
    model.load_state_dict(state_dict)
    return model


if __name__ == "__main__":
    configs = [
        "configs/stage3-effb1-f0.yaml",
        "configs/stage3-effb4-f0.yaml",
        "configs/stage3-inrv2-f0.yaml",
        "configs/stage3-srx50-2-f0.yaml",
        "configs/stage3-srx50-f0.yaml",
    ]
    batch_size = 8
    gpu = "0"
    tta = True

    os.environ["CUDA_VISIBLE_DEVICES"] = gpu

    # --------------------------------------------------
    # define model
    # --------------------------------------------------

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Available devices:", device)

    # loading trained models
    models = [model_from_config(config_path) for config_path in configs]

    # create ensemble
    model = EnsembleModel(models)

    # add test time augmentations (flipping and rotating input image)
    if tta:
        model = ttach.SegmentationTTAWrapper(
            model, ttach.aliases.d4_transform(), merge_mode="mean"
        )

    # create Multi GPU model if number of GPUs is more than one
    n_gpus = len(gpu.split(","))
    if n_gpus > 1:
        gpus = list(range(n_gpus))
        model = torch.nn.DataParallel(model, gpus)

    print("Done loading...")
    model.to(device)

    # --------------------------------------------------
    # start evaluation
    # --------------------------------------------------
    runner = GPUNormRunner(model, model_device=device)
    model.eval()

    # predict big tif files
    predictor = TorchTifPredictor(
        runner=runner,
        sample_size=1024,
        cut_edge=256,
        batch_size=batch_size,
        count=1,
        NBITS=1,
        compress=None,
        driver="GTiff",
        blockxsize=256,
        blockysize=256,
        tiled=True,
        BIGTIFF="IF_NEEDED",
    )

    for sub_dir in os.listdir("../../data/images"):
        if sub_dir == "5":
            os.makedirs(f"../../data/predictions_open_cities/{sub_dir}", exist_ok=True)
            image_paths = glob(f"../../data/images/{sub_dir}/*.tif")

            for path in image_paths:
                dst_path = os.path.join(
                    "../../data/predictions_open_cities",
                    sub_dir,
                    os.path.basename(path),
                )
                predictor(path, dst_path)
