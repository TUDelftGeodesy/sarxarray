# sarxarray

`SarXarray` is an `Xarray` extension to process coregistered Single Look Complex (SLC) image stacks acquired by Synthetic Aperture Radar (SAR). It utilizes `Xarray`’s support on labeled multi-dimensional datasets to stress the space-time character of the SLC SAR stack. It also takes the benefits from `Dask` to perform lazy evaluations of the operations.

## Installation

First, clone this repository to your local file system:

```bash
git clone git@github.com:MotionbyLearning/sarxarray.git
```

We strongly recommend you install `sarxarray` under an independent Python environment, e.g. an independent [conda](https://docs.conda.io/en/latest/miniconda.html) environment. 

After creating a new environment, you can install `SarXarray` using `pip`:

```bash
cd sarxarray
pip install .
```

## Usage example

An [example Jupyter Notebook](examples/demo_sarxarray.ipynb) is available to demonstrate the usage of `SarXarray`.
