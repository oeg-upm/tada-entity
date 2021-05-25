from experiments.experiment_base import ExperimentBase
import os
import sys
from datetime import datetime

class ST19R1(ExperimentBase):

    def __init__(self, log_fname=None):
        super().__init__(log_fname)
        self.invalid_files = []

    def workflow(self, meta_fdir, data_dir, ks):
        f = open(meta_fdir)
        num_files = 0
        for line in f.readlines():
            num_files += 1
            fname, col_id, class_uri = line.split(",")
            fname = fname.replace('"', '').strip()+".csv"
            class_uri = class_uri.replace('"', '').strip()
            col_id = int(col_id.replace('"', ''))
            fdir = os.path.join(data_dir, fname)
            if not os.path.exists(fdir):
                self.invalid_files.append(fdir)
                num_files -=1
                continue
            self.annotate_single(fpath=fdir, col_id=col_id)
            self.validate_with_opt_alpha(correct_candidates=[class_uri], alpha_inc=0.001)
        print("Total number of files: %d" % num_files)
        print("# of invalid files: %d" % len(self.invalid_files))
        for invf in self.invalid_files:
            print(invf)
        for k in ks:
            print("Scores for k=%d" % k)
            self.get_scores(k)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        meta_fdir,  data_dir = sys.argv[1:]
        start = datetime.now()
        o = ST19R1("st19-r1-results.csv")
        o.workflow(meta_fdir=meta_fdir, data_dir=data_dir, ks=[1, 3, 5])
        end = datetime.now()
        print("time consumed: "+str(end-start))
    else:
        print("Missing arguments: <meta file> <data directory>")
