from experiments.experiment_base import ExperimentBase
import os
import sys


class WCV1(ExperimentBase):

    def __init__(self, log_fname=None):
        super().__init__(log_fname)

    def workflow(self, meta_fdir, data_dir, ks):
        f = open(meta_fdir)
        num_files = 0
        for line in f.readlines():
            num_files += 1
            "18321599_0_4014218119449874050.tar.gz", "Thing", "http://www.w3.org/2002/07/owl#Thing", ""
            fname, _, class_uri, col_id = line.split(",")
            col_id = col_id.replace('"', '').strip()
            if col_id == "":
                num_files -= 1
                continue
            col_id = int(col_id)
            fname = fname.replace('"', '').strip()[:-6] + "csv"
            class_uri = class_uri.replace('"', '').strip()
            fdir = os.path.join(data_dir, fname)
            self.annotate_single(fpath=fdir, col_id=col_id)
            self.validate_with_opt_alpha(correct_candidates=[class_uri], alpha_inc=0.001)
        print("Total number of files: %d" % num_files)
        for k in ks:
            print("Scores for k=%d" % k)
            self.get_scores(k)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        meta_fdir, data_dir = sys.argv[1:]
        o = WCV1("wc1-results.csv")
        o.workflow(meta_fdir=meta_fdir, data_dir=data_dir, ks=[1, 3, 5])
    else:
        print("Missing arguments: <meta file> <data directory>")
