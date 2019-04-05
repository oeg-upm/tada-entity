
import os
import sys
import csv
import subprocess

#################################################################
#           TO make this app compatible with Django             #
#################################################################

proj_path = (os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir))
print("proj_path: "+proj_path)
venv_python = os.path.join(proj_path, '.venv', 'bin', 'python')
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tadae.settings")
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from tadae.settings import LOG_DIR, UPLOAD_DIR, BASE_DIR
from tadae.models import AnnRun

import annotator
import commons

#################################################################

curr_dir = os.path.join(BASE_DIR, 'experiments', 'olympic_games')
meta_dir = os.path.join(curr_dir, "meta.csv")

prefix = "http://dbpedia.org/ontology/"

def olympic_games_to_csv():
    input_folder = os.path.join(curr_dir, 'data')
    f = open(meta_dir)
    reader = csv.reader(f)
    for line in reader:
        fname, class_name = line[0], line[1]
        output_file = os.path.join(BASE_DIR, UPLOAD_DIR, fname)
        input_file = os.path.join(input_folder, fname)
        comm = """ cp "%s" "%s" """ % (input_file, output_file)
        print comm
        subprocess.Popen(comm, shell=True)


def build_empty_models_from_meta():
    f = open(meta_dir)
    reader = csv.reader(f)
    for line in reader:
        file_name, concept = line[0], line[1]
        print("csv fname: "+file_name)
        if len(AnnRun.objects.filter(name=file_name)) == 0:
            annotation_run = AnnRun(name=file_name, status='Created')
            annotation_run.save()


def annotate_models():
    f = open(meta_dir)
    reader = csv.reader(f)
    file_subject_idx_pairs = []
    for line in reader:
        fname, concept, subject_idx = line[0], line[1], 0
        file_subject_idx_pairs.append((fname, subject_idx))

    for model_name, subject_idx in file_subject_idx_pairs:
        print("model name: "+model_name)
        ann_run = AnnRun.objects.get(name=model_name)
        if ann_run.status == 'Created':
            ann_run.status = "started"
            ann_run.save()
            csv_file_dir = os.path.join(proj_path, UPLOAD_DIR, ann_run.name)
            annotator.annotate_csv(ann_run_id=ann_run.id, csv_file_dir=csv_file_dir,
                                   endpoint=commons.ENDPOINT, hierarchy=False, entity_col_id=subject_idx, onlyprefix=prefix,
                                   camel_case=False)
            annotator.dotype(ann_run, commons.ENDPOINT, onlyprefix=None)
        elif ann_run.status != 'Annotation is complete':
            raise Exception("An uncompleted annotation run is found")


def workflow():
    build_empty_models_from_meta()
    annotate_models()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == 'tocsv':
            olympic_games_to_csv()
        elif sys.argv[1] == 'annotate':
            workflow()

