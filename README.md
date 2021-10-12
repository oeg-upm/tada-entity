# tada-entity
[![Build Status](https://semaphoreci.com/api/v1/ahmad88me/tada-entity/branches/master/badge.svg)](https://semaphoreci.com/ahmad88me/tada-entity)
[![codecov](https://codecov.io/gh/oeg-upm/tada-entity/branch/master/graph/badge.svg)](https://codecov.io/gh/oeg-upm/tada-entity)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)

**This is being re-written**

## Alpha analysis

To run alpha analysis

### T2Dv1
1. Generate the alpha ranges.

Original case
```
python -m experiments.wcv1_experiment experiments/wcv1_meta.csv ~/workspaces/Datasets/T2Dv1/tables_complete original alpha
```

Title case
```
python -m experiments.wcv1_experiment experiments/wcv1_meta.csv ~/workspaces/Datasets/T2Dv1/tables_complete title alpha
```

2. Generate mid alpha diagrams.

Title case
```
python -m experiments.alpha_analysis wc1_alpha_title_case.csv  experiments/wcv1_meta.csv wcv1 --draw wcv1_alpha_mid_title --midalpha  
```
   
Original case
```
python -m experiments.alpha_analysis wc1_alpha_original_case.csv  experiments/wcv1_meta.csv wcv1 --draw wcv1_alpha_mid_original --midalpha  
```

3. Generate from-to alpha diagrams.
   
Title case

```
python -m experiments.alpha_analysis wc1_alpha_title_case.csv  experiments/wcv1_meta.csv wcv1 --draw wcv1_alpha_from_to_title
```

Original case.

```
python -m experiments.alpha_analysis wc1_alpha_original_case.csv  experiments/wcv1_meta.csv wcv1 --draw wcv1_alpha_from_to_original
```

### T2Dv2

1. Generate alpha ranges

Original 
```
python -m experiments.wcv2_experiment experiments/wcv2_meta.csv experiments/wcv2_subject_columns_gs.csv ~/workspaces/Datasets/T2Dv2/csv original alpha 
```

Title 
```
python -m experiments.wcv2_experiment experiments/wcv2_meta.csv experiments/wcv2_subject_columns_gs.csv ~/workspaces/Datasets/T2Dv2/csv title alpha 
```


1. Generate mid alpha diagrams
   
Title case.

```
python -m experiments.alpha_analysis wc2_alpha_title_case.csv  experiments/wcv2_meta.csv wcv2 --draw wcv2_alpha_mid_title --midalpha
```
   
Original case.

```
python -m experiments.alpha_analysis wc2_alpha_original_case.csv  experiments/wcv2_meta.csv wcv2 --draw wcv2_alpha_mid_original --midalpha
```

3. Generate from-to alpha diagrams
   
Title case.

```
python -m experiments.alpha_analysis wc2_alpha_title_case.csv  experiments/wcv2_meta.csv wcv2 --draw wcv2_alpha_from_to_title
```

Original case.

```
python -m experiments.alpha_analysis wc2_alpha_original_case.csv  experiments/wcv2_meta.csv wcv2 --draw wcv2_alpha_from_to_original
```


### ST19R1

1. Generate alpha ranges

Original 
```
python -m experiments.st19_r1_experiment ~/workspaces/Datasets/semtab2019/Round\ 1/gt/CTA_Round1_gt.csv ~/workspaces/Datasets/semtab2019/Round\ 1/tables original alpha
```

Title 
```
python -m experiments.st19_r1_experiment ~/workspaces/Datasets/semtab2019/Round\ 1/gt/CTA_Round1_gt.csv ~/workspaces/Datasets/semtab2019/Round\ 1/tables title alpha
```


1. Generate mid alpha diagrams
   
Title case.

```
python -m experiments.alpha_analysis wc2_alpha_title_case.csv  experiments/wcv2_meta.csv wcv2 --draw wcv2_alpha_mid_title --midalpha
```
   
Original case.

```
python -m experiments.alpha_analysis wc2_alpha_original_case.csv  experiments/wcv2_meta.csv wcv2 --draw wcv2_alpha_mid_original --midalpha
```

3. Generate from-to alpha diagrams
   
Title case.

```
python -m experiments.alpha_analysis wc2_alpha_title_case.csv  experiments/wcv2_meta.csv wcv2 --draw wcv2_alpha_from_to_title
```

Original case.

```
python -m experiments.alpha_analysis wc2_alpha_original_case.csv  experiments/wcv2_meta.csv wcv2 --draw wcv2_alpha_from_to_original
```






## Alpha k-fold evaluation

### T2Dv1
To run alpha evaluation

1. Generate scores file

Title case

```
python -m experiments.alpha_eval_k_fold --falpha wc1_alpha_title_case.csv --fmeta experiments/wcv1_meta.csv --data_dir ~/workspaces/Datasets/T2Dv1/tables_complete --title true --dataset wcv1
```

Original case

```
python -m experiments.alpha_eval_k_fold --falpha wc1_alpha_original_case.csv --fmeta experiments/wcv1_meta.csv --data_dir ~/workspaces/Datasets/T2Dv1/tables_complete --title false --dataset wcv1
```

2. Generate the diagrams

Title case

```
python -m experiments.alpha_eval_k_fold --draw wcv1_alpha_k_fold_scores --fscores wcv1_k_fold_alpha_title.csv --title true  --dataset wcv1
```

Original case

```
python -m experiments.alpha_eval_k_fold --draw wcv1_alpha_k_fold_scores --fscores wcv1_k_fold_alpha_original.csv --title false  --dataset wcv1
```


### T2Dv2
To run alpha evaluation

1. Generate scores file

Title case

```
python -m experiments.alpha_eval_k_fold --falpha wc2_alpha_title_case.csv --fmeta experiments/wcv2_meta.csv --data_dir ~/workspaces/Datasets/T2Dv2/csv --title true --dataset wcv2
```

Original case

```
python -m experiments.alpha_eval_k_fold --falpha wc2_alpha_original_case.csv --fmeta experiments/wcv2_meta.csv --data_dir ~/workspaces/Datasets/T2Dv2/csv --title false --dataset wcv2
```

2. Generate the diagrams

Title case
```
python -m experiments.alpha_eval_k_fold --draw wcv2_alpha_k_fold_scores --fscores wcv2_k_fold_alpha_title.csv --title true --dataset wcv2
```

Original case
```
python -m experiments.alpha_eval_k_fold --draw wcv2_alpha_k_fold_scores --fscores wcv2_k_fold_alpha_original.csv --title false --dataset wcv2
```


## One alpha for all

### T2Dv2

Title case
```
 python -m experiments.alpha_eval_one --falpha wc2_alpha_title_case.csv --fmeta experiments/wcv2_meta.csv --dataset wcv2 --fscores wcv2_k_fold_alpha_title.csv --draw wcv2_alpha_one_title
```

Original case
```
 python -m experiments.alpha_eval_one --falpha wc2_alpha_original_case.csv --fmeta experiments/wcv2_meta.csv --dataset wcv2 --fscores wcv2_k_fold_alpha_original.csv --draw wcv2_alpha_one_original
```

# NEW
## Experiments
* alpha inc `0.001`

### WCv2

meta_fdir, sc_dir, data_dir 
To run the experiment
`python -m experiments.wcv2_experiment <meta dir> <subject column dir> <data dir>`

meta dir: the path to the file which contains the file names and their classes
subject column dir: the path to the file which contains the subject column ids
data dir: the path to the folder which contain the csv files
```
python -m experiments.wcv2_experiment <meta dir> <subject column dir> <data dir>
```
### SemTab
#### Invalid
```
Round 1/tables/8286121_0_8471791395229161598.csv
Round 1/tables/71137051_0_8039724067857124984.csv
Round 1/tables/55004961_0_2904467548072189860.csv
Round 1/tables/8286121_0_8471791395229161598.csv
Round 1/tables/61121469_0_6337620713408906340.csv
Round 1/tables/55004961_0_2904467548072189860.csv
Round 1/tables/61121469_0_6337620713408906340.csv
Round 1/tables/55238374_0_3379409961751009152.csv
Round 1/tables/57943722_0_8666078014685775876.csv
Round 1/tables/55238374_0_3379409961751009152.csv
Round 1/tables/57943722_0_8666078014685775876.csv
```

# OLD

Tabular Data Annotation of entity columns

http://tada-entity.linkeddata.es

# Installation

## Requirements
* `virtualenv`
* `python3`
* `mysql`
* `SPARQLWrapper` (using [this fork](https://github.com/syats/sparqlwrapper) as it supports self-signed certificates).


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

To show the alphas for each k (where k can be 1,3,5, or 10).
```python validation.py astat k```

## Other tests
Follow the same as in Web Commons v2 and change it to the corresponding name (e.g., webcommons_v1, olympic_games)


# Environment
## Operating Systems
* MacOS (tested with Mojave)
* Linux (tested with Ubuntu)
* Windows (not tested but let us know if it works for you)



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
