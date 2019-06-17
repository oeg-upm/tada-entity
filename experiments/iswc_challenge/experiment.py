import os
import sys
import csv
import subprocess
import pandas as pd
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


# def get_model_name(file_name, idx):
#     return "iswc_col_"+str(idx)+"__"+file_name


def get_model_name(file_name, idx):
    return "iswc_con_"+str(idx)+"__"+file_name


def get_file_name(name):
    return name.split('__')[1]


def get_numerics_from_list(nums_str_list):
    """
    :param nums_str_list: list of string or numbers or a mix
    :return: list of numbers or None if less than 50% are numbers
    """
    nums = []
    for c in nums_str_list:
        n = get_num(c)
        if n is not None:
            nums.append(n)
    if len(nums) < len(nums_str_list)/2:
        return None
    return nums


def get_num(num_or_str):
    """
    :param num_or_str:
    :return: number or None if it is not a number
    """
    if pd.isna(num_or_str):
        return None
    elif isinstance(num_or_str, (int, float)):
        return num_or_str
    elif isinstance(num_or_str, basestring):
        if '.' in num_or_str or ',' in num_or_str or num_or_str.isdigit():
            try:
                return float(num_or_str.replace(',', ''))
            except Exception as e:
                return None
    return None


def is_numeric(items):
    """
    :param items:
    :return:
    """
    return get_numerics_from_list(items) != None


def has_special_characters(items):
    """
    :param items:
    :return: whether more that half of the items contain special characters
    """
    clean_items = []
    white_chars = ["_", "-", " "]
    for item in items:
        if type(item) in [int,float]:
            continue
        for c in item:
            if not c.isalpha() and c not in white_chars:
                break
        clean_items.append(item)

    return len(clean_items) < len(items)*0.5


# def detect_subject_idx(fname):
#     """
#     :param fname:
#     :return: index of the subject column (int)
#     """
#     f_dir = os.path.join(curr_dir, "data", fname)
#     df = pd.read_csv(f_dir)
#     headers = df.columns
#     for idx, header in enumerate(headers):
#         col = list(df[header])
#         if is_numeric(col):
#             continue
#         else:
#             return idx


def detect_entity_columns(fname):
    """
    :param fname:
    :return: list of non-numeric column indices
    """
    f_dir = os.path.join(curr_dir, "data", fname)
    df = pd.read_csv(f_dir)
    headers = df.columns
    indices = []
    for idx, header in enumerate(headers):
        col = list(df[header])
        if is_numeric(col):
            continue
        elif has_special_characters(col):
            continue
        else:
            indices.append(idx)
    return indices


# def build_empty_models_from_meta():
#     f = open(meta_dir)
#     reader = csv.reader(f)
#     for line in reader:
#         file_name = line[0]
#         print("csv fname: "+file_name)
#         model_name = get_model_name(file_name)
#         if len(AnnRun.objects.filter(name=model_name)) == 0:
#             annotation_run = AnnRun(name=model_name, status='Created')
#             annotation_run.save()


def annotate_models():
    f = open(meta_dir)
    reader = csv.reader(f)
    file_subject_idx_pairs = []
    for line in reader:
        # fname, subject_idx = line[0], 0
        fname = line[0]
        indices = detect_entity_columns(fname)
        # subject_idx = detect_subject_idx(fname)
        # fname, concept, subject_idx = line[0], line[1], 0
        # file_subject_idx_pairs.append((fname, subject_idx))
        # file_subject_idx_pairs.append((get_model_name(fname), subject_idx))
        for idx in indices:
            file_subject_idx_pairs.append((get_model_name(fname, idx), idx))

    for model_name, subject_idx in file_subject_idx_pairs:
        print("model name: "+model_name)
        # ann_run = AnnRun.objects.get(name=model_name)
        ann_runs = AnnRun.objects.filter(name=model_name)
        if len(ann_runs) == 0:
            ann_run = AnnRun(name=model_name, status='Created')
            ann_run.save()
        elif len(ann_runs) ==1:
            ann_run = ann_runs[0]
        else:
            raise Exception("Multiple annotation runs with the same name: %s" % model_name)

        if ann_run.status == 'Created':
            ann_run.status = "started"
            ann_run.save()
            # fname = model_name[5:]
            fname = get_file_name(model_name)
            csv_file_dir = os.path.join(curr_dir, "data", fname)
            # csv_file_dir = os.path.join(proj_path, UPLOAD_DIR, fname)
            annotator.annotate_csv(ann_run_id=ann_run.id, csv_file_dir=csv_file_dir,
                                   endpoint=commons.ENDPOINT, hierarchy=False, entity_col_id=subject_idx,
                                   onlyprefix=prefix, camel_case=False)
            annotator.dotype(ann_run, commons.ENDPOINT, onlyprefix=None)
        elif ann_run.status != 'Annotation is complete':
            raise Exception("An uncompleted annotation run is found: %s" % str(ann_run.id))


def workflow():
    # build_empty_models_from_meta()
    annotate_models()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == 'annotate':
            workflow()

