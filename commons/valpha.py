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




# alphas = [0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.1, 0.05, 0.01, 0.005, 0.001, 0.0005, 0.0001, 0.00005, 0.00001]
alphas = [0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.1, 0.05, 0.01, 0.005, 0.001, 0.0005, 0.0001, 0.00005, 0.00001, 0.000005, 0.000001]


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


def validate_ent_ann(ent_ann, fsid, ks, correct_type, for_all_alphas, not_found_fname, incorrect_fname,
                     correct_fname, alphas_fname):
    """
    :param ent_ann:
    :param fsid:
    :param ks: a list of k values that should be sorted in a ascending order
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
    #alphas = [0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.1, 0.05, 0.01, 0.005, 0.001, 0.0005, 0.0001, 0.00005, 0.00001]
    k_id = len(ks)-1  # to start with the largest k
    k = ks[k_id]
    d = {}
    for alpha in alphas:
        if for_all_alphas:
            k_id = len(ks) - 1  # to start with the largest k
            k = ks[k_id]
        graph = annotator.load_graph(entity_ann=ent_ann)
        results = annotator.score_graph(entity_ann=ent_ann, alpha=alpha, graph=graph, fsid=fsid)[0:k]

        if results == []:
            for k in ks:
                d[k] = "NOTFOUND"
                report_not_found(fname=ent_ann.ann_run.name, not_found_fname=not_found_fname)
            return d

        while correct_type in results:
            d[k] = "CORRECT"
            report_correct(fname=ent_ann.ann_run.name, fsid=fsid, k=k, correct_fname=correct_fname)
            if for_all_alphas:
                report_alphas(fname=ent_ann.ann_run.name, fsid=fsid, k=k, alpha=alpha, alphas_fname=alphas_fname)
            if k_id == 0:  # no more values of k left
                k_id = -1
                break
            else:
                k_id -= 1
                k = ks[k_id]  # new k
                results = results[0:k]

        if k_id < 0 and not for_all_alphas:
            break

    while k_id >= 0:  # there are some values of k that is smaller than k
        d[k] = "INCORRECT"
        report_incorrect(fname=ent_ann.ann_run.name, fsid=fsid, k=k, incorrect_fname=incorrect_fname)
        k_id -= 1
        k = ks[k_id]
    return d


# This does not take into account the alphas for different fs
# def alpha_stat(ks, alphas_fname):
#     alpha_file_exists = os.path.isfile(alphas_fname)
#     if not alpha_file_exists:
#         msg = """
#             No alpha file is found, to generate it run the application with 'alpha' parameter like that \n
#             python validation.py alpha
#         """
#         print(msg)
#         return
#     df = pd.read_csv(alphas_fname, sep='\t')
#     # print df.columns.values
#     d = dict()
#     for k in ks:
#         df_k = df[df.k==k]
#         d_count = dict(Counter(df_k['alpha']))
#         d[k] = d_count
#     pp = pprint.PrettyPrinter(indent=4)
#     pp.pprint(d)
#     print d
#     plot_alpha_stat(d)

# This does not take into account the alphas for different fs
# def plot_alpha_stat(d):
#     import matplotlib
#     matplotlib.use('TkAgg')
#     import matplotlib.pyplot as plt
#
#     ind = np.arange(len(d[d.keys()[-1]]))  # the x locations for the groups
#     width = 0.20  # the width of the bars
#     fig, ax = plt.subplots()
#
#     # custom_colors = [ 'royalblue', 'mediumpurple', 'mediumvioletred','hotpink' ,'greenyellow', 'dodgerblue', 'aquamarine' ,'deeppink', 'darkturquoise', 'skyblue']
#
#     for idx, k in enumerate(sorted(d.keys())):
#         vals = []
#         for a in sorted(d[k].keys()):
#             vals.append(d[k][a])
#
#         _ = ax.bar(ind + width * idx - width/2, vals, width,
#                    color=cmap(idx*1.0/len(d.keys())),
#                    #color=custom_colors[idx],
#                    label="k="+str(k))
#
#     ax.set_ylabel('Count')
#     ax.set_title('Alphas for each k')
#     ax.set_xticks(ind)
#     ax.set_xticklabels(tuple(sorted(d[d.keys()[-1]].keys())))
#     ax.legend()
#     plt.show()


def alpha_stat(ks, alphas_fname):
    alpha_file_exists = os.path.isfile(alphas_fname)
    if not alpha_file_exists:
        msg = """
            No alpha file is found, to generate it run the application with 'alpha' parameter like that \n
            python validation.py alpha
        """
        print(msg)
        return
    df = pd.read_csv(alphas_fname, sep='\t')
    # print df.columns.values
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
    #print d
    plot_alpha_stat(d)

# This is a different matplotlib example not related to the code
# def plot_alpha_stat(d):
#     men_means, men_std = (20, 35, 30, 35, 27), (2, 3, 4, 1, 2)
#     women_means, women_std = (25, 32, 34, 20, 25), (3, 5, 2, 3, 3)
#
#     ind = np.arange(len(men_means))  # the x locations for the groups
#     width = 0.35  # the width of the bars
#
#     fig, ax = plt.subplots()
#     rects1 = ax.bar(ind - width / 2, men_means, width, yerr=men_std,
#                     color='SkyBlue', label='Men')
#     rects2 = ax.bar(ind + width / 2, women_means, width, yerr=women_std,
#                     color='IndianRed', label='Women')
#
#     # Add some text for labels, title and custom x-axis tick labels, etc.
#     ax.set_ylabel('Scores')
#     ax.set_title('Scores by group and gender')
#     ax.set_xticks(ind)
#     ax.set_xticklabels(('G1', 'G2', 'G3', 'G4', 'G5'))
#     ax.legend()
#     #plt.savefig("secret_fig.png")
#     plt.show(block=True)

# The correct one
def plot_alpha_stat(d):
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

    global alphas
    ind = np.arange(len(alphas))  # the x locations for the groups
    width = 0.18  # the width of the bars
    fig, ax = plt.subplots()

    for idx, fs in enumerate(sorted(d.keys())):
        vals = []
        for a in alphas:
            if a in d[fs][1]:
                vals.append(d[fs][1][a])
            else:
                vals.append(0)

        _ = ax.bar(ind + width * idx - width/2, vals, width,
                   color=cmap(fs*1.0/len(d.keys())),
                   label="fs="+str(fs)
                   )
    ax.set_ylabel('Count')
    ax.set_title('Alphas for each k')
    ax.set_xticks(ind)
    ax.set_xticklabels(tuple(alphas))
    ax.legend()
    plt.show()



# show with plot
# def plot_alpha_stat(d):
#     import matplotlib
#     matplotlib.use('TkAgg')
#     import matplotlib.pyplot as plt
#     global alphas
#     #ind = np.array(alphas)
#     ind = np.arange(len(alphas))  # the x locations for the groups
#     width = 0.20  # the width of the bars
#     fig, ax = plt.subplots()
#
#     # custom_colors = [ 'royalblue', 'mediumpurple', 'mediumvioletred','hotpink' ,'greenyellow', 'dodgerblue', 'aquamarine' ,'deeppink', 'darkturquoise', 'skyblue']
#
#     for idx, fs in enumerate(sorted(d.keys())):
#         vals = []
#         # for a in sorted(d[fs][1].keys()):
#         #     vals.append(d[fs][1][a])
#         for a in alphas:
#             if a in d[fs][1]:
#                 vals.append(d[fs][1][a])
#             else:
#                 vals.append(0)
#
#         alphas_as_str = [str(a) for a in alphas]
#         # _ = ax.bar(alphas_as_str, vals,
#         #            color=cmap(fs*1.0/len(d.keys())),
#         #            #color=custom_colors[idx],
#         #            #label="fs="+str(fs)
#         #            )
#         # _ = ax.bar(ind + width * idx - width/2, vals, width,
#         #            color=cmap(fs*1.0/len(d.keys())),
#         #            #color=custom_colors[idx],
#         #            label="fs="+str(fs)
#         #            )
#         # _ = ax.bar(ind + width * idx - width/2, vals, width,
#         #            color=cmap(fs*1.0/len(d.keys())),
#         #            #color=custom_colors[idx],
#         #            label="fs="+str(fs)
#         #            )
#         print("alphas: "+str(alphas))
#         print("vals: "+str(vals))
#         _ = ax.plot(alphas_as_str, vals,
#                     color=cmap(fs * 1.0 / len(d.keys())),
#                     )
#
#
#     ax.set_ylabel('Count')
#     ax.set_title('Alphas for each k')
#     # ax.set_xticks(ind)
#     ax.set_xticks(alphas_as_str)
#     ax.set_xticklabels(tuple(alphas_as_str))
#     ax.legend()
#     plt.show()