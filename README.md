# tada-entity
[![Build Status](https://semaphoreci.com/api/v1/ahmad88me/tada-entity/branches/master/badge.svg)](https://semaphoreci.com/ahmad88me/tada-entity)
[![codecov](https://codecov.io/gh/oeg-upm/tada-entity/branch/master/graph/badge.svg)](https://codecov.io/gh/oeg-upm/tada-entity)
[![status](https://img.shields.io/badge/status-under%20development-ff69b4.svg)](https://github.com/oeg-upm/bob)

Tabular Data Annotation of entity columns

# Installation

## Requirements
* `virtualenv`
* `python2.7`
* `mysql`

## Installation steps (Linux and MacOS)
1. Download the project 
```
git clone git@github.com:oeg-upm/tada-entity.git; cd tada-entity/
```
2. Create virtual environment 
```
virtualenv  -p /usr/bin/python2.7 .venv
```
3. Install dependencies 
``` 
pip install -r requirements.txt 
```
4. create a mysql.cfg file in the same folder (see below)
5. Setup database and apply migrations 
``` 
python manage.py makemigrations; python manage.py makemigrations tadae; python manage.py migrate
```


## Mysql configuration
fill in the database name, user, and password
```
# my.cnf
[client]
database = 
user = 
password = 
default-character-set = utf8mb4
wait_timeout = 28800
```

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

To report different alphas (note that it would take more time to compute it)
```python validation.py alpha```

To show the alphas for each k
```python validation.py alphastat```

## Other tests
Follow the same as in Web Commons v2 and change it to the corresponding name (e.g., webcommons_v1, olympic_games)


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
