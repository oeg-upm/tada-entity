from experiments.experiment_base import ExperimentBase
import os
import sys


class WCV2(ExperimentBase):

    def __init__(self, log_fname=None):
        super().__init__(log_fname)

    def workflow(self, meta_fdir, subject_col_dir, data_dir, ks):
        d = dict()
        f = open(subject_col_dir)
        for line in f.readlines():
            fname, col_id = line.split(',')
            fname = fname.strip() + ".csv"
            col_id = int(col_id)
            d[fname] = col_id
        f.close()

        f = open(meta_fdir)
        num_files = 0
        for line in f.readlines():
            num_files += 1
            fname, class_name, class_uri = line.split(",")
            fname = fname.replace('"', '').strip()[:-6] + "csv"
            class_uri = class_uri.replace('"', '').strip()
            fdir = os.path.join(data_dir, fname)
            self.annotate_single(fpath=fdir, col_id=d[fname])
            self.validate_with_opt_alpha(correct_candidates=[class_uri], alpha_inc=0.001)
        print("Total number of files: %d" % num_files)
        for k in ks:
            print("Scores for k=%d" % k)
            self.get_scores(k)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        meta_fdir, sc_dir, data_dir = sys.argv[1:]
        o = WCV2("wc2-results.csv")
        o.workflow(meta_fdir=meta_fdir, subject_col_dir=sc_dir, data_dir=data_dir, ks=[1, 3, 5])
    else:
        print("Missing arguments: <meta file> <data directory>")
