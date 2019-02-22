# tada-entity
[![Build Status](https://semaphoreci.com/api/v1/ahmad88me/tada-entity/branches/master/badge.svg)](https://semaphoreci.com/ahmad88me/tada-entity)
[![codecov](https://codecov.io/gh/oeg-upm/tada-entity/branch/master/graph/badge.svg)](https://codecov.io/gh/oeg-upm/tada-entity)
[![status](https://img.shields.io/badge/status-under%20development-ff69b4.svg)](https://github.com/oeg-upm/bob)

Tabular Data Annotation of entity columns

# Status
* Web GUI: :white_check_mark:
* API: :x:
* T2D Experiments: :x:


# Run the experiments
## Web Commons v2
1. Create the directory `tada-entity/experiments/webcommons_v2/data` (where `tada-entity` is the project's directory.
2. Copy the json files to that directory. The data can be found [here](http://webdatacommons.org/webtables/goldstandardV2.html).
3. In the terminal (command line interface) go the directory `tada-entity/experiments/webcommons_v2/` using the below command (assuming you are in the directory `tada-entity`):

```cd experiments/webcommons_v2```
 
4. Generate the csv files using the command:

```python experiment.py tocsv```

5. Run the automatic annotator using the command:

```python experiment.py annotate```

6. Get the scores for the experiment. Note that this will run test with multiple values of alpha and k using the command:
```python validation.py```

# Environment
## Operating Systems
* MacOS (tested with Mojave)
* Linux (tested with Ubuntu)
* Windows (not tested but let us know if it works for you)

## Python
v2.7

## Database
Having a database accessible by the application is a must. The file `mysql.cnf` should include the credential.
Below is an example of the file content : 
```
[client]
database = mydbname
user = dbuser
password = dbpassword
default-character-set = utf8
```
To user an *alternative* database engine, you might need to update the `settings.py` file 
to specify the engine of your choosing (`sqlite` is not thread-safe, we don't recommend using it). 

# Tests
## To run automated test
```sh run_tests.sh```

## To run the coverage
```sh run_coverage.sh```

*Note that the experiments are not included in the coverage*
