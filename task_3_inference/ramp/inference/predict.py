import os
from glob import glob
from pathlib import Path

import numpy as np
from tensorflow import keras

from .georeference import georeference
from .utils import open_images, save_mask, remove_files

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"
BATCH_SIZE = 8
IMAGE_SIZE = 256


def predict(
    checkpoint_path: str, image_path: str, pred_path: str
) -> None:
    """Predict masks for all images.

    Args:
        checkpoint_path: Path where the weights of the model can be found.
        image_path: Path of the directory where the images are stored.
        pred_path: Path of the directory where the predicted images will go.
    """
    model = keras.models.load_model(checkpoint_path)

    os.makedirs(pred_path, exist_ok=True)
    image_paths = glob(f"{image_path}/*.png")

    for i in range(len(image_paths) // BATCH_SIZE + 1):
        image_batch = image_paths[BATCH_SIZE * i : BATCH_SIZE * (i + 1)]
        if len(image_batch) == 0:
            continue

        images = open_images(image_batch)
        images = images.reshape(-1, IMAGE_SIZE, IMAGE_SIZE, 3)

        preds = model.predict(images)
        preds = np.argmax(preds, axis=-1)
        preds = np.expand_dims(preds, axis=-1)
        preds = np.where(preds > 0.5, 1, 0)

        for idx, path in enumerate(image_batch):
            save_mask(
                preds[idx],
                str(f"{pred_path}/{Path(path).stem}.png"),
            )

    georeference(pred_path, is_mask=True)
    remove_files(f"{pred_path}/*.xml")
    remove_files(f"{pred_path}/*.png")
