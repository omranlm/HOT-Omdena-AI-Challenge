from hotlib import predict

predict(
    checkpoint_path=f"model_5_scaled_checkpt.tf",
    input_path="../data/prediction-dataset/5x5/5-19",
    prediction_path=f"../data/ramp_predictions_scaled",
)


