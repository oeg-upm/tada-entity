from collections import Counter
import pandas as pd
import pprint
import numpy as np


import os
import sys
import csv
import subprocess

#################################################################
#           TO make this app compatible with Django             #
#################################################################

proj_path = (os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
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

#################################################################

CORRECT = "CORRECT"
NOTFOUND = "NOTFOUND"
INCORRECT = "INCORRECT"

# alphas = [0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.1, 0.05, 0.01, 0.005, 0.001, 0.0005, 0.0001, 0.00005, 0.00001]
alphas = [0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.1, 0.05, 0.01, 0.005, 0.001, 0.0005, 0.0001, 0.00005, 0.00001,
          0.000005, 0.000001,  0.0000005, 0.0000001, 0.00000005, 0.00000001]


def prepare_report_files(not_found_fname, incorrect_fname, correct_fname, alphas_fname):
    f = open(os.path.join(proj_path, not_found_fname), "w")
    f.write("file name\n")
    f.close()
    f = open(os.path.join(proj_path, incorrect_fname), "w")
    f.write("file name\tfs\tk\n")
    f.close()
    f = open(os.path.join(proj_path, correct_fname), "w")
    f.write("file name\tfs\tk\n")
    f.close()
    f = open(os.path.join(proj_path, alphas_fname), "w")
    f.write("file name\tfs\tk\talpha\n")
    f.close()


def report_incorrect(fname, fsid, k, incorrect_fname):
    f = open(os.path.join(proj_path, incorrect_fname), "a")
    f.write("%s\t%s\t%s\n" % (fname, str(fsid), str(k)))
    f.close()


def report_not_found(fname, not_found_fname):
    f = open(os.path.join(proj_path, not_found_fname))
    t = f.read()
    f.close()
    if fname not in t:
        f = open(os.path.join(proj_path, not_found_fname), "a")
        f.write(fname+"\n")
        f.close()


def report_correct(fname, fsid, k, correct_fname):
    f = open(os.path.join(proj_path, correct_fname), "a")
    f.write("%s\t%s\t%s\n" % (fname, str(fsid), str(k)))
    f.close()


def report_alphas(fname, fsid, k, alpha, alphas_fname):
    f = open(os.path.join(proj_path, alphas_fname), "a")
    f.write("%s\t%s\t%s\t%f\n" % (fname, str(fsid), str(k), alpha))
    f.close()


# Original (but does not work well if alphas_fname is True )
# def validate_ent_ann(ent_ann, fsid, ks, correct_type, for_all_alphas, not_found_fname, incorrect_fname,
#                      correct_fname, alphas_fname):
#     """
#     :param ent_ann:
#     :param fsid:
#     :param ks: a list of k values that should be sorted in a ascending order
#     :param correct_type:
#     :param for_all_alphas: bool (if true, then it will check alphas that yields a good score)
#     :return:
#         {
#             "k_1": bool,
#             "k_2": bool,
#             ....
#         }
#     """
#     global alphas
#     k_id = len(ks)-1  # to start with the largest k
#     k = ks[k_id]
#     d = {}
#     for alpha in alphas:
#         if for_all_alphas:
#             k_id = len(ks) - 1  # to start with the largest k
#             k = ks[k_id]
#         graph = annotator.load_graph(entity_ann=ent_ann)
#         results = annotator.score_graph(entity_ann=ent_ann, alpha=alpha, graph=graph, fsid=fsid)[0:k]
#
#         if results == []:
#             for k in ks:
#                 d[k] = "NOTFOUND"
#                 report_not_found(fname=ent_ann.ann_run.name, not_found_fname=not_found_fname)
#             return d
#
#         while correct_type in results:
#             d[k] = "CORRECT"
#             report_correct(fname=ent_ann.ann_run.name, fsid=fsid, k=k, correct_fname=correct_fname)
#             if for_all_alphas:
#                 report_alphas(fname=ent_ann.ann_run.name, fsid=fsid, k=k, alpha=alpha, alphas_fname=alphas_fname)
#             if k_id == 0:  # no more values of k left
#                 k_id = -1
#                 break
#             else:
#                 k_id -= 1
#                 k = ks[k_id]  # new k
#                 results = results[0:k]
#
#         if k_id < 0 and not for_all_alphas:
#             break
#
#     while k_id >= 0:  # there are some values of k that is smaller than k
#         d[k] = "INCORRECT"
#         report_incorrect(fname=ent_ann.ann_run.name, fsid=fsid, k=k, incorrect_fname=incorrect_fname)
#         k_id -= 1
#         k = ks[k_id]
#     return d

# Correct even with alphas_fname=True
def validate_ent_ann(ent_ann, fsid, ks, correct_type, for_all_alphas, not_found_fname, incorrect_fname,
                     correct_fname, alphas_fname):
    """
    :param ent_ann:
    :param fsid:
    :param ks: a list of k values (order is not important)
    :param correct_type:
    :param for_all_alphas: bool (if true, then it will check alphas that yields a good score)
    :return:
        {
            "k_1": bool,
            "k_2": bool,
            ....
        }
    """
    global alphas

    max_k = max(ks)
    d = {}
    for alpha in alphas:
        graph = annotator.load_graph(entity_ann=ent_ann)
        results = annotator.score_graph(entity_ann=ent_ann, alpha=alpha, graph=graph, fsid=fsid)[0:max_k]

        if results == []:
            for k in ks:
                d[k] = NOTFOUND
                report_not_found(fname=ent_ann.ann_run.name, not_found_fname=not_found_fname)
            return d

        for k in ks[::-1]:
            results = results[0:k]
            if correct_type in results:
                # If this is not set before
                if k not in d or d[k] != CORRECT:
                    d[k] = CORRECT
                    report_correct(fname=ent_ann.ann_run.name, fsid=fsid, k=k, correct_fname=correct_fname)

                if for_all_alphas:
                    report_alphas(fname=ent_ann.ann_run.name, fsid=fsid, k=k, alpha=alpha, alphas_fname=alphas_fname)

    for k in ks:
        if k not in d or d[k] != CORRECT:
            d[k] = INCORRECT
            report_incorrect(fname=ent_ann.ann_run.name, fsid=fsid, k=k, incorrect_fname=incorrect_fname)
    return d


def alpha_stat(ks, alphas_fname, k_filter):
    alpha_file_exists = os.path.isfile(alphas_fname)
    if not alpha_file_exists:
        msg = """
            No alpha file is found, to generate it run the application with 'alpha' parameter like that \n
            python validation.py alpha
        """
        print(msg)
        return
    df = pd.read_csv(alphas_fname, sep='\t')
    d = dict()
    for fs in range(1, 6):
        for k in ks:
            df_k_fsid = df[df.k==k][df.fs==fs]
            d_count = dict(Counter(df_k_fsid['alpha']))
            if fs not in d:
                d[fs] = dict()

            d[fs][k] = d_count
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(d)
    plot_alpha_stat(d=d, k=k_filter)


def plot_alpha_stat(d, k, with_plot=False):
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt

    import matplotlib.cm

    # cmap = matplotlib.cm.jet
    cmap = matplotlib.cm.viridis
    # cmap = matplotlib.cm.plasma
    # cmap = matplotlib.cm.inferno
    # cmap = matplotlib.cm.magma
    # cmap = matplotlib.cm.GnBu
    # cmap = matplotlib.cm.winter
    # cmap = matplotlib.cm.hot

    hatches = ['+','///', 'OO', '--',  '...', 'xxx']
    markers = [ "*", "v" ,"o","s","P","X",]

    global alphas
    ind = np.arange(len(alphas))  # the x locations for the groups
    width = 0.16  # the width of the bars
    fig, ax = plt.subplots()
    # for k in [ks[0], ks[-1]]:
    # for k in ks[1::-1]:  # get k=3 then k=1
    for idx, fs in enumerate(sorted(d.keys())):
        vals = []
        for a in alphas:
            print("alpha: "+str(a))
            print("fs: "+str(fs))
            print("k: "+str(k))
            print("d[fs]"+str(d[fs]))
            print("d[fs][k]"+str(d[fs][k]))
            if a in d[fs][k]:
                print("in alpha: "+str(a)+"   - "+str(d[fs][k][a]))
                vals.append(d[fs][k][a])
            else:
                print("not in alpha: "+str(a))
                vals.append(0)

        if with_plot:
            _ = ax.bar(ind + width * idx - width / 2, vals, width,
                       # edgecolor="black",
                       color=cmap(fs * 1.0 / len(d.keys())),
                       fill=True,
                       # hatch=hatches[fs],
                       # label="fs=" + str(fs)
                       )

            _ = ax.plot(ind + width * idx - width / 2, vals,
                        color=cmap((fs * 1.0) / len(d.keys())),
                        marker=markers[fs],
                        markeredgecolor="black",
                        markerfacecolor="white",
                        markeredgewidth=1,
                        label="fs"+str(fs)+"(k="+str(k)+")"
                        )
        else:
            print "vals: "
            print vals

            _ = ax.bar(ind + width * idx - width / 2, vals, width,
                       # edgecolor="black",
                       color=cmap(fs * 1.0 / len(d.keys())),
                       fill=True,
                       # hatch=hatches[fs],
                       label="fs=" + str(fs)
                       )

    ax.set_ylabel('Count')
    ax.set_title('Alphas for different fs with k='+str(k))
    ax.set_xticks(ind)
    ax.set_xticklabels(tuple(alphas))
    ax.legend()
    plt.show()