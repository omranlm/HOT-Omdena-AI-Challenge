# Mapping Tool for HOT

The directory `data` needs to be downloaded from Google Drive for testing.

[Download `data`](https://drive.google.com/drive/folders/1WwZr3-MWLcwHuaNukwnlP8AZerSMOdn9?usp=sharing)

## `data` Directory Structure

```console
.
├───images_v2
│   ├───1
│   ├───2
│   ├───3
│   ├───4
│   └───5
├───inputs_v2
│   ├───1
│   ├───2
│   ├───3
│   ├───4
│   └───5
└───masks_v2
    ├───1
    ├───2
    ├───3
    ├───4
    └───5
```

## `hotlib` Installation

1. Set up a Conda virtual environment for installing `hotlib` using `environment.yml`:

    ```console
    conda env create -f environment.yml
    ```

2. Activate the virtual environment.

    ```console
    conda activate hot
    ```

3. Install `hotlib` from PyPI:

    ```console
    pip install hotlib
    ```

## Making Edits to Preprocessing/Inference

Edit in `hotlib`. In order to test your edit, take the following steps:

1. Install `hotlib` package in editable mode:

    ```console
    python -m pip install -e hotlib
    ```

2. Test it by running:

    ```console
    pip list | grep hotlib
    ```

    You'll find a path after the version of `hotlib`:

    ```console
    hotlib                       1.0.33    C:\Users\Tasin\Documents\repos\hot\hotlib
    ```

3. Make an edit to `hotlib`.
4. Try running `task_1_preprocessing/preprocess.py` now. The updated code will be executed.

## Custom Virtual Environment

```console
conda create -n hot python=3.8
conda activate hot
conda install -c conda-forge geopandas
pip install pyogrio rasterio tensorflow
pip install -e hotlib
```

## Sort Imports

```console
isort . --profile black -s env
```
