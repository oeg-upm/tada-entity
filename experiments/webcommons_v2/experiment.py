import chardet
import json
import csv
import os
import sys
import subprocess
from datetime import datetime
# f = open("web_commons_progress.txt")


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
#################################################################################
#                           JSON to CSV                                         #
#################################################################################


import logging
from commons.logger import set_config
logger = set_config(logging.getLogger(__name__), logdir=os.path.join(LOG_DIR, 'tadae.log'))

curr_dir = os.path.join(BASE_DIR, 'experiments', 'webcommons_v2')
meta_dir = os.path.join(curr_dir, "meta.csv")


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


def web_commons_json_table_to_csv(in_file_dir, out_file_dir):
    fin = open(in_file_dir)
    s_raw = fin.read()
    detected_encoding = chardet.detect(s_raw)
    s = s_raw.decode(detected_encoding['encoding'])
    j = json.loads(s)
    index = j["keyColumnIndex"]
    entity_column = j["relation"][index]
    entities = []
    for e in entity_column:
        ee = e.replace('"', '').strip()
        ee = '"'+ee+'"'
        entities.append(ee)
    fout = open(out_file_dir, 'w')
    fout.write(("\n".join(entities)).encode('utf8'))
    fout.close()


def web_commons_to_csv():
    f = open(meta_dir)
    reader = csv.reader(f)
    for line in reader:
        file_name, concept = get_file_and_concept_from_line(line)
        print file_name, concept
        csv_file_name = get_csv_file(concept, file_name)
        output_file = os.path.join(BASE_DIR, UPLOAD_DIR, csv_file_name)
        input_fname = "data/%s.json" % file_name
        input_file = os.path.join(curr_dir, input_fname)
        web_commons_json_table_to_csv(input_file, output_file)


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
    anns = AnnRun.objects.filter(status='Created')
    for ann_run in anns:
        ann_run.status = "started"
        ann_run.save()
        csv_file_dir = os.path.join(proj_path, UPLOAD_DIR, ann_run.name)
        prefix = "http://dbpedia.org/ontology/"
        annotator.annotate_csv(ann_run_id=ann_run.id, csv_file_dir=csv_file_dir,
                               endpoint=commons.ENDPOINT, hierarchy=False, entity_col_id=0, onlyprefix=prefix,
                               camel_case=False)
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
