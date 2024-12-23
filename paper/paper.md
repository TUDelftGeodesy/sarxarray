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

Satellite-based Synthetic Aperture Radar (SAR) provides invaluable image data for Earth Observation. The Interferometric SAR (InSAR) technique, which leverages a stack of SAR images in Single Look Complex (SLC) format, plays a significant role for various surface motion monitoring applications, e.g. civil-infrastructure stability [@chang2014detection; @chang2017railway], hydrocarbons extraction [@fokker2016application; @ZHANG2022102847], etc. To enable advanced data processing for the InSAR community, we present `SARXarray`, an Xarray extension for handling SLC SAR stacks for InSAR data processing. 

## Statement of Need

Satellite-based SAR generates data stacks with long temporal coverage, broad spatial coverage and high spatio-temporal resolution. [@moreira2013tutorial] Handling it in an efficient way is a common challenge within the InSAR community. The High Performance Computing (HPC) infrastructures provide an opportunity to process these data stacks in a parallel and distributed manner. However, to fully utilize the HPC infrastructures, the data processing workflows often need to be customized case by case.

Aiming to meet the need for efficient processing of SLC SAR stacks with minimum effort on code customization, we developed `SARXarray` for SLC SAR stack processing. 

`SARXarray` is developed based on two established Python libraries `Xarray` and `Dask` from the [Pangeo community](https://www.pangeo.io/). Implemented as an Xarray extension, it utilizes Xarray’s support on labeled multi-dimensional datasets to stress the space-time character of an SLC SAR stack. It also leverages `Dask` to perform lazy evaluation of the operations and block-wise computation. It can be integrated to existing Python workflows of InSAR processing and deployed on various computational infrastructures. 

## Tutorial

We provide a tutorial as a Jupyter notebook to demonstrate the basic functionalities of `SARXarray`:

[Tutorial Jupyter notebook](https://tudelftgeodesy.github.io/sarxarray/notebooks/demo_sarxarray/)

The tutorial demonstrates the following steps:

- Installation and data preparation
- Lazy loading a SAR data stack in binary format as an Xarray Dataset
- Attaching attributes to the loaded stack
- Applying a simple SAR operation on the loaded stack

## Acknowledgements

The authors express sincere gratitude to the Dutch Research Council (Nederlandse Organisatie voor Wetenschappelijk Onderzoek, NWO) for their generous funding of the `SARXarray` development through the Collaboration in Innovative Technologies (CIT 2021) Call, grant NLESC.CIT.2021.006. Special thanks to SURF for providing valuable computational resources for `SARXarray` testing.

We would also like to thank Dr. Francesco Nattino and Dr. Meiert Willem Grootes for the insightful discussions, which are important contributions to this work.

## References
