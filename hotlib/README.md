# Library for AI-Assisted Mapping Tool developed for Humanitarian OpenStreetMap Team

A small team from Omdena worked on a disaster management project. This package was created in order to simplify the integration of the data processing steps with the model training one.

## `data` Directory Structure

```console
.
├───images
│   ├───1
│   ├───2
│   ├───3
│   ├───4
│   └───5
├───inputs
│   ├───1
│   ├───2
│   ├───3
│   ├───4
│   └───5
├───masks
│   ├───1
│   ├───2
│   ├───3
│   ├───4
│   └───5
└───predictions
    ├───1
    ├───2
    ├───3
    ├───4
    └───5
```

- `inputs`: GeoJSON labels and image files given to us.
- `images`: Georeferenced images with the fourth band removed (if any).
- `masks`: Rasterized labels.
- `predictions`: Masks predicted by some ML model.

## API Reference

1. `preprocess(data_path, input_dir, image_dir, mask_dir)`

   Function for fully preprocessing the input data.

   - `data_path`: Path of the directory where all the data are stored.
   - `input_dir`: Name of the directory where the input data are stored.
   - `image_dir`: Name of the directory where the images are stored.
   - `mask_dir`: Name of the directory where the masks are stored.

2. `predict(checkpoint_path, data_path, image_dir, pred_dir)`

   Function for predicting masks for all the input images.

   - `checkpoint_path`: Path where the architecture and weights of the model can be found.
   - `data_path`: Path of the directory where all the data are stored.
   - `image_dir`: Name of the directory where the images are stored.
   - `pred_dir`: Name of the directory where the predicted images will go.

## Example Usages

Preprocessing:

```py
from hotlib import preprocess

preprocess("/content/gdrive/MyDrive/Omdena/data", "inputs", "images", "masks")
```

Prediction:

```py
from hotlib import predict

predict(
    "/content/gdrive/MyDrive/Omdena/checkpoints",
    "/content/gdrive/MyDrive/Omdena/data",
    "images",
    "predictions",
)
```
