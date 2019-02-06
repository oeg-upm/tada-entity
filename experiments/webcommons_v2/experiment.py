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


#################################################################################
#                           JSON to CSV                                         #
#################################################################################


import logging
from commons.logger import set_config
logger = set_config(logging.getLogger(__name__), logdir=os.path.join(LOG_DIR, 'tadae.log'))


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
    curr_dir = os.path.join(BASE_DIR, 'experiments', 'webcommons_v2')
    f = open(os.path.join(curr_dir, "meta.csv"))
    reader = csv.reader(f)
    for line in reader:
        file_name = line[0][:-7]
        concept = line[1].replace(' ', '_')
        print file_name, concept
        csv_file_name = "wcv1_%s_%s.csv" % (concept, file_name)
        output_file = os.path.join(BASE_DIR, UPLOAD_DIR, csv_file_name)
        input_fname = "data/%s.json" % file_name
        input_file = os.path.join(curr_dir, input_fname)
        web_commons_json_table_to_csv(input_file, output_file)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == 'tocsv':
            web_commons_to_csv()
