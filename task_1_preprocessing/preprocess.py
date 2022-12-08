from hotlib import preprocess

preprocess(
    input_path="../data/inputs_v2/4",
    output_path="../data/4_zlata",
    rasterize=True,
    rasterize_options=["grayscale", "binary"],
    georeference_images=True,
)
