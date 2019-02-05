# tada-entity
[![Build Status](https://semaphoreci.com/api/v1/ahmad88me/tada-entity/branches/master/badge.svg)](https://semaphoreci.com/ahmad88me/tada-entity)
[![codecov](https://codecov.io/gh/oeg-upm/tada-entity/branch/master/graph/badge.svg)](https://codecov.io/gh/oeg-upm/tada-entity)
[![status](https://img.shields.io/badge/status-under%20development-ff69b4.svg)](https://github.com/oeg-upm/bob)

expected alpha version release: *17-Feb-2019*

Tabular Data Annotation of entity columns


# Perform experiments
## Web Commons v2
1. Create the directory `tada-entity/experiments/webcommons_v2/data` (where `tada-entity` is the project's directory.
2. Copy the json files to that directory. The data can be found [here](http://webdatacommons.org/webtables/goldstandardV2.html).
3. Generate the csv files using the command:

```python experiment.py tocsv```

# Environment
## Operating Systems
* MacOS (tested with Mojave)
* Linux (tested with Ubuntu)
* Windows (not tested but let us know if it works for you)

## Python
v2.7
