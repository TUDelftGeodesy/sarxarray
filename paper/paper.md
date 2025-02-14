---
title: 'SARXarray: Xarray extension for Synthetic Aperture Radar data'
tags:
  - Python
  - Synthetic Aperture Radar
  - SAR
  - InSAR
  - Dask
  - Xarray
authors:
  - name: Ou Ku
    orcid: 0000-0002-5373-5209
    affiliation: 1 
  - name: Fakhereh Alidoost
    orcid: 0000-0001-8407-6472
    affiliation: 1
  - name: Freek van Leijen
    orcid: 0000-0002-2582-9267
    affiliation: 2
affiliations:
 - name: Netherlands eScience Center, Netherlands
   index: 1
 - name: Delft University of Technology, Netherlands
   index: 2
date: 22 Dec 2024
bibliography: paper.bib
---

## Summary

Satellite-based Synthetic Aperture Radar (SAR) provides invaluable image data for Earth observation. The Interferometric SAR (InSAR) technique, which utilizes a stack of SAR images in Single Look Complex (SLC) format, plays a significant role in various surface motion monitoring applications, e.g. civil-infrastructure stability [@chang2014detection; @chang2017railway], and hydrocarbons extraction [@fokker2016application; @ZHANG2022102847]. To facilitate advanced data processing for InSAR communities, we developed `SARXarray`, a Xarray extension for handling SLC SAR stacks. 

## Statement of Need

Satellite-based SAR generates data stacks with long temporal coverage, broad spatial coverage, and high spatio-temporal resolution. [@moreira2013tutorial] Handling SAR data stacks in an efficient way is a common challenge within InSAR communities. To address this challenge, High-Performance Computing (HPC) is often used to process data in a parallel and distributed manner. However, to fully leverage HPC capabilities, data processing workflows need to be customized for each specific use-case.

To facilitate efficient processing of SLC SAR stacks and minimize code customization, we developed `SARXarray` for SLC SAR stack. 

`SARXarray` leverages two well-established Python libraries `Xarray` and `Dask` from the [Pangeo community](https://www.pangeo.io/). It utilizes Xarray’s support on labeled multi-dimensional datasets to stress the space-time character of an SLC SAR stack. `Dask` is used to perform lazy evaluation of operations and block-wise computations. SARXarray can be integrated into existing Python workflows of InSAR processing and deployed on a variety of computational infrastructures. 

## Tutorial

We provided a tutorial as a Jupyter notebook to demonstrate the functionalities of `SARXarray`:

[Tutorial Jupyter notebook](https://tudelftgeodesy.github.io/sarxarray/notebooks/demo_sarxarray/)

The tutorial includes the following steps:

- Installation and data preparation
- Lazy loading a SAR data stack in binary format as an Xarray Dataset
- Attaching attributes to the loaded stack
- Applying common SAR operations on the loaded stack such as Multi-Looking and Mean-Reflection-Map

## Acknowledgements

The authors express sincere gratitude to the Dutch Research Council (Nederlandse Organisatie voor Wetenschappelijk Onderzoek, NWO) for their generous funding of the `SARXarray` development through the Collaboration in Innovative Technologies (CIT 2021) Call, grant NLESC.CIT.2021.006. Special thanks to SURF for providing valuable computational resources for `SARXarray` testing via grant EINF-2051, EINF-4287 and EINF-6883.

We would also like to thank Dr. Francesco Nattino and Dr. Meiert Willem Grootes for the insightful discussions, which are important contributions to this work.

## References
