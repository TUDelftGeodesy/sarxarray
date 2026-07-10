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
  - name: Simon van Diepen
    orcid: 0000-0002-9350-3779
    affiliation: 2
  - name: Freek van Leijen
    orcid: 0000-0002-2582-9267
    affiliation: 2
affiliations:
 - name: Netherlands eScience Center, Netherlands
   index: 1
 - name: Department of Geoscience and Remote Sensing, Delft University of Technology, Netherlands
   index: 2
date: 22 Dec 2024
bibliography: paper.bib
---

## Summary

Satellite-based Synthetic Aperture Radar (SAR) provides invaluable data for Earth Observation. The Interferometric SAR (InSAR) technique [@hanssen01], which utilizes a stack of SAR images in Single Look Complex (SLC) format, plays a significant role in various surface motion monitoring applications, e.g. civil-infrastructure stability [@chang2014detection; @chang2017railway; @ozer2018applicability], and hydrocarbon extraction [@fokker2016application; @ZHANG2022102847]. To facilitate advanced data processing for InSAR communities, we developed `SARXarray`, a Xarray extension for handling co-registered SLC SAR stacks. 

## Statement of Need

Satellite-based SAR generates data stacks with long temporal coverage, wide spatial coverage, and high spatio-temporal resolution [@moreira2013tutorial]. Handling SAR data stacks in an efficient way is a common challenge within the InSAR community. To address this challenge, High-Performance Computing (HPC) is often used to process data in a parallel and distributed manner. However, to fully leverage HPC capabilities, data processing workflows need to be customized for each specific use-case.

To facilitate efficient processing of SLC SAR stacks and minimize code customization, we developed `SARXarray`. 

`SARXarray` leverages two well-established Python libraries `Xarray` [@hoyer2017xarray] and `Dask` [@rocklin2015] from the [Pangeo community](https://www.pangeo.io/). It utilizes Xarray’s support on labeled multi-dimensional datasets to stress the space-time character of an SLC SAR stack. `Dask` is used to perform lazy evaluation of operations and block-wise computations. SARXarray can be integrated into existing Python workflows of InSAR processing and deployed on a variety of compute infrastructures. 

## State of the field

A similar open-source library `xarray-sentinel`[@xarray-sentinel] exists for handling raw Sentinel-1 GRD and SLC data as lazy-loaded Xarray Datasets. Despite the similar goals of digesting SAR data into lazy-loaded Xarray Datasets, `SARXarray` and `xarray-sentinel` are designed for different applications:

- `SARXarray` is designed to handle co-registered SLC stacks, instead of raw Sentinel-1 data products from European Space Agency (ESA). It is able to lazily read the output of two common SLC co-registration tools: [`DORIS`](https://doris.tudelft.nl/) and [`SNAP`](https://step.esa.int/main/download/snap-download/) into Xarray objects. The two tools perform the necessary coregistration step, which aligns the SLCs in a stack to a common reference frame. The generated outputs can be further used in Time-Series InSAR (TS-InSAR) processing.
- `SARXarray` supports interferometric stacks from other sensors than Sentinel-1, as long as they can be co-registered by SNAP or DORIS. It reads the output from the two co-registration tools, and relies on them to handle the specificities of different sensors.

## Software design

`SARXarray` is designed as an extension of Xarray using accessors. This design is motivated by [Xarray community’s recommendation](https://docs.xarray.dev/en/stable/internals/extending-xarray.html), in order to isolate the extension from API changes of the core Xarray library. 

The software has three main components: 

- an I/O module that lazily loads/writes binary SLCs and related metadata
- a Stack accessor that provides basic SAR-specific operations (amplitude/phase extraction and Mean-Reflection-Map generation)
- a utility module that provides functions for multi-Looking and coherence calculation. 

## Research impact statement

`SARXarray` is a dependency of [CAROLINE](https://github.com/TUDelftGeodesy/caroline) (Contextual and Autonomous processing of satellite Radar Observations for Learning and Interpreting the Natural and built Environment), which is an InSAR processing framework developed by the InSAR group of Delft University of Technology. It has facilitated the data processing of multiple InSAR research projects [@LUMBANGAOL2025117551; @brouwer11131159; @conroy10642504].  

`SARXarray` is a recognized related project of the Xarray ecosystem, see the [Xarray user-guide page](https://docs.xarray.dev/en/stable/user-guide/ecosystem.html#geosciences).

## Tutorial

We provide a tutorial as a Jupyter notebook to demonstrate the functionalities of `SARXarray`:

[Tutorial Jupyter notebook](https://tudelftgeodesy.github.io/sarxarray/notebooks/demo_sarxarray/)

The tutorial includes the following steps:

- Installation and data preparation
- Lazy loading a SAR data stack in binary format as an Xarray Dataset
- Attaching attributes to the loaded stack
- Applying common SAR operations on the loaded stack such as:
  - Multi-Looking 
  - Creation of a Mean-Reflectivity-Map (MRM)
  - Calculation of coherence

## Acknowledgements

The authors express sincere gratitude to the Dutch Research Council (Nederlandse Organisatie voor Wetenschappelijk Onderzoek, NWO) for their generous funding of the `SARXarray` development through the Collaboration in Innovative Technologies (CIT 2021) Call, grant NLESC.CIT.2021.006. We would like to extend special thanks to SURF for providing valuable computational resources for `SARXarray` testing via grants EINF-2051, EINF-4287 and EINF-6883.

We would also like to thank Dr. Francesco Nattino, Dr. Meiert Willem Grootes and Dr. Pranav Chandramouli of the Netherlands eScience Center for the insightful discussions, which are important contributions to this work.

## AI usage disclosure

In writing the software documentation and the JOSS paper, GPT-5 was used for language improvements for grammar correction and style edits.

Specifically, in the documentation process, an agent skill (under path `../.github/skills/release-changelog`) is used to generate changelog entries from git tags and commit history. The generated content was always reviewed and edited by a human before being committed to the repository.

Additionally, various language models were used via [GitHub Copilot](https://copilot.github.com/) in Pull Requests reviews, for pre-filtering obvious issues such as typos, small logical errors, and for suggesting code improvements. All suggestions from AI were reviewed and verified by the authors before merging into the codebase. The correctness of the code was ensured by the unit tests.

## References
