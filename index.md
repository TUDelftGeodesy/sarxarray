# SARXarray

SARXarray is an open-source Xarray extension for Synthetic Aperture Radar (SAR) data.

SARXarray is especially designed to work with complex data, that is, containing both the phase and amplitude of the data. The extension can handle coregistered stacks of Single Look Complex (SLC) data, as well as derived products such as interferogram stacks.
It utilizes Xarray’s support on labeled multi-dimensional datasets to stress the space-time character of the image stacks. Dask Array is implemented to support parallel computation.

SARXarry supports the following functionalities:

1. Chunk-wise reading/writing of coregistered SLC or interferogram stacks;

2. Basic operations on complex data, e.g., averaging along axis and complex conjugate multiplication;

3. Specific SAR data operations, e.g., multi-looking and coherence estimation.

All the above functionalities can be scaled up to a Hyper-Performance Computation (HPC) system.

