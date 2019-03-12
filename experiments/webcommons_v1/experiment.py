
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
#################################################################

curr_dir = os.path.join(BASE_DIR, 'experiments', 'webcommons_v1')
meta_dir = os.path.join(curr_dir, "meta.csv")


def web_commons_to_csv():
    f = open(meta_dir)
    reader = csv.reader(f)
    for line in reader:
        file_name, concept = get_file_and_concept_from_line(line)
        print file_name, concept
        csv_file_name = get_csv_file(concept, file_name)
        output_file = os.path.join(BASE_DIR, UPLOAD_DIR, csv_file_name)
        input_fname = "data/%s.csv" % file_name
        input_file = os.path.join(curr_dir, input_fname)
        comm = """ cp "%s" "%s" """ % (input_file, output_file)
        print comm
        subprocess.Popen(comm, shell=True)


def get_file_concept_and_subject_idx_from_line(line):
    """
    get file name without extension and the concept without spaces
    :param line:
    :return:
    """
    file_name = line[0][:-7]
    concept = line[1].replace(' ', '_')
    return file_name, concept, int(line[4])


def get_file_and_concept_from_line(line):
    """
    get file name without extension and the concept without spaces
    :param line:
    :return:
    """
    file_name = line[0][:-7]
    concept = line[1].replace(' ', '_')
    return file_name, concept


def get_csv_file(concept, file_name):
    return "wcv1_%s_%s.csv" % (concept, file_name)


def build_empty_models_from_meta():
    f = open(meta_dir)
    reader = csv.reader(f)
    for line in reader:
        file_name, concept = get_file_and_concept_from_line(line)
        csv_fname = get_csv_file(concept, file_name)
        print("csv fname: "+csv_fname)
        if len(AnnRun.objects.filter(name=csv_fname)) == 0:
            annotation_run = AnnRun(name=csv_fname, status='Created')
            annotation_run.save()


def annotate_models():
    f = open(meta_dir)
    reader = csv.reader(f)
    file_subject_idx_pairs = []
    for line in reader:
        fname, concept , subject_idx = get_file_concept_and_subject_idx_from_line(line)
        model_name = get_csv_file(fname, concept)
        file_subject_idx_pairs.append((model_name, subject_idx))

    # anns = AnnRun.objects.filter(status='Created')
    # for ann_run in anns:
    for model_name, subject_idx in file_subject_idx_pairs:
        ann_run = AnnRun.objects.get(name=model_name, status='Created')
        ann_run.status = "started"
        ann_run.save()
        csv_file_dir = os.path.join(proj_path, UPLOAD_DIR, ann_run.name)
        prefix = "http://dbpedia.org/ontology/"
        annotator.annotate_csv(ann_run_id=ann_run.id, csv_file_dir=csv_file_dir,
                               endpoint=commons.ENDPOINT, hierarchy=False, entity_col_id=subject_idx, onlyprefix=prefix,
                               camel_case=True)
        annotator.dotype(ann_run, commons.ENDPOINT, onlyprefix=None)


def workflow():
    build_empty_models_from_meta()
    annotate_models()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == 'tocsv':
            web_commons_to_csv()
        elif sys.argv[1] == 'annotate':
            workflow()
