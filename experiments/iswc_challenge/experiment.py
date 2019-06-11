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

curr_dir = os.path.join(BASE_DIR, 'experiments', 'iswc_challenge')
meta_dir = os.path.join(curr_dir, "meta.csv")

prefix = "http://dbpedia.org/ontology/"


def get_model_name(file_name):
    return "iswc_"+file_name


def build_empty_models_from_meta():
    f = open(meta_dir)
    reader = csv.reader(f)
    for line in reader:
        file_name = line[0]
        print("csv fname: "+file_name)
        model_name = get_model_name(file_name)
        if len(AnnRun.objects.filter(name=model_name)) == 0:
            annotation_run = AnnRun(name=model_name, status='Created')
            annotation_run.save()


def annotate_models():
    f = open(meta_dir)
    reader = csv.reader(f)
    file_subject_idx_pairs = []
    for line in reader:
        fname, subject_idx = line[0], 0
        # fname, concept, subject_idx = line[0], line[1], 0
        # file_subject_idx_pairs.append((fname, subject_idx))
        file_subject_idx_pairs.append((get_model_name(fname), subject_idx))

    for model_name, subject_idx in file_subject_idx_pairs:
        print("model name: "+model_name)
        ann_run = AnnRun.objects.get(name=model_name)
        if ann_run.status == 'Created':
            ann_run.status = "started"
            ann_run.save()
            fname = model_name[5:]
            csv_file_dir = os.path.join(curr_dir, "data", fname)
            # csv_file_dir = os.path.join(proj_path, UPLOAD_DIR, fname)
            annotator.annotate_csv(ann_run_id=ann_run.id, csv_file_dir=csv_file_dir,
                                   endpoint=commons.ENDPOINT, hierarchy=False, entity_col_id=subject_idx,
                                   onlyprefix=prefix, camel_case=True)
            annotator.dotype(ann_run, commons.ENDPOINT, onlyprefix=None)
        elif ann_run.status != 'Annotation is complete':
            raise Exception("An uncompleted annotation run is found: %s" % str(ann_run.id))


def workflow():
    build_empty_models_from_meta()
    annotate_models()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == 'annotate':
            workflow()

