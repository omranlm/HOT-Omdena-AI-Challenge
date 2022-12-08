from inference import predict

suffix = "5-20"
predict(
    checkpoint_path="checkpoints/model_5_checkpt.tf",
    image_path=f"../../data/prediction-dataset/5x5/{suffix}",
    pred_path=f"../../data/predictions_ramp_v2/{suffix}",
)
