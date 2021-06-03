from experiments.experiment_base import ExperimentBase
import os
import sys
from datetime import datetime
import pandas as pd

class ST19R2(ExperimentBase):

    def __init__(self, log_fname=None, title_case=False):
        super().__init__(log_fname=log_fname, title_case=title_case)
        self.invalid_files = []

    def workflow(self, meta_fdir, data_dir, ks):
        df = pd.read_csv(meta_fdir)

        # f = open(meta_fdir)
        num_files = 0
        for idx, row in df.iterrows():
        # for line in f.readlines():
            num_files += 1
            fname = row[0]
            col_id = int(row[1])
            # attrs = line.split(",")
            # fname, col_id= attrs[:2]
            classes = [class_uri.replace('"', '').replace("'", "").strip() for class_uri in row[2:] ]
            classes = [class_uri for class_uri in classes if class_uri != '']
            fname = fname.strip()+".csv"
            # fname = fname.replace('"', '').strip()+".csv"
            # col_id = int(col_id.replace('"', ''))
            fdir = os.path.join(data_dir, fname)
            if not os.path.exists(fdir):
                self.invalid_files.append(fdir)
                num_files -=1
                continue
            self.annotate_single(fpath=fdir, col_id=col_id)
            self.validate_with_opt_alpha(correct_candidates=classes)
            # for testing
            # if num_files == 3:
            #     break # for testing
        print("Total number of files: %d" % num_files)
        print("# of invalid files: %d" % len(self.invalid_files))
        for invf in self.invalid_files:
            print(invf)
        for k in ks:
            print("Scores for k=%d" % k)
            self.get_scores(k)


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        results_fname_original = "st19-r2-results.csv"
        results_fname_title = "st19-r2-results-title.csv"
        results_fname = results_fname_original
        title_case = False
        meta_fdir,  data_dir = sys.argv[1:3]
        if len(sys.argv) == 4:
            if sys.argv[3]=="title":
                print("Title case")
                results_fname = results_fname_title
                title_case = True
            elif sys.argv[3]=="original":
                print("original case")
                results_fname = results_fname_original
                title_case = False
            else:
                print("Error: expects the fourth paramerter to either be title or original")
                raise Exception("Invalid case")
        start = datetime.now()
        o = ST19R2(results_fname, title_case=title_case)
        o.workflow(meta_fdir=meta_fdir, data_dir=data_dir, ks=[1, 3, 5])
        end = datetime.now()
        print("time consumed: "+str(end-start))
    else:
        print("Missing arguments: <meta file> <data directory> [<title/original>]")
