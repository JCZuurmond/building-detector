# Building detector

## Installation

The packages requires `gdal`, which is not pip-installable. A hybrid between
conda is chosen (for now):

```bash
$ conda env create -f environment.yml
(building-detector) $ pip install -r requirements.txt     # with conda env activated
```
