# Installation

SARXarray can be installed from PyPI:

```sh
pip install 'sarxarray'
```

or from the source:

```sh
git clone git@github.com:TUDelftGeodesy/sarxarray.git
cd sarxarray
pip install .
```

Note that Python version `>=3.10` is required for SARXarray.

### Install extra dependencies

SARXarray has some optional dependencies to support additional functionality besides the core features. You can install them depending on your needs:

```sh
pip install 'sarxarray[demo]'    # to run the demo notebook
pip install 'sarxarray[dev]'     # to run the test suite
pip install 'sarxarray[docs]'    # to build the docs locally
```

## Tips

We strongly recommend installing separately from your default Python environment. E.g. you can use environment manager (e.g. [mamba](https://mamba.readthedocs.io/en/latest/mamba-installation.html)) to create a separate environment.
