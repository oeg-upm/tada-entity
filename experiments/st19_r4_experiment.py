from experiments.experiment_base import ExperimentBase
import os
import sys
from datetime import datetime
import pandas as pd

class ST19R4(ExperimentBase):

    def __init__(self, log_fname=None, title_case=False):
        super().__init__(log_fname=log_fname, title_case=title_case)
        self.invalid_files = []
        self.notparsed_files = []

    def workflow(self, meta_fdir, data_dir, ks):
        df = pd.read_csv(meta_fdir).fillna('')
        # f = open(meta_fdir)
        num_files = 0
        # #test
        # print(len(df.columns))
        for idx, row in df.iterrows():
        # for line in f.readlines():
            num_files += 1
            fname = str(row[0])
            # test
            # if fname != "List_of_tallest_buildings_in_Aurora,_Colorado#0":
            #     continue
            # if fname != "List_of_snack_foods_from_the_Indian_subcontinent#1":
            #     continue
            col_id = int(row[1])
            # attrs = line.split(",")
            # fname, col_id= attrs[:2]
            classes = [row[2]]
            # print("row[2] = ")
            # print(row[2])
            # print("row[3] = ")
            # print(row[3])
            ok_classes = [str(class_uri).strip() for class_uri in row[3].split(' ') if class_uri.strip()!='']
            classes = classes + ok_classes
            # print("ok classes: ")
            # print(ok_classes)
            # classes = [str(class_uri).strip() for class_uri in row[2:] ]
            # classes = [class_uri for class_uri in classes if class_uri != '']
            fname = fname.strip()+".csv"
            # fname = fname.replace('"', '').strip()+".csv"
            # col_id = int(col_id.replace('"', ''))
            fdir = os.path.join(data_dir, fname)
            if not os.path.exists(fdir):
                self.invalid_files.append(fdir)
                num_files -=1
                continue
            try:
                _ = pd.read_csv(fdir)
            except Exception as e:
                self.notparsed_files.append(fdir)
                num_files -=1
                continue

            self.annotate_single(fpath=fdir, col_id=col_id)
            self.validate_with_opt_alpha(correct_candidates=classes)
            # for testing
            # if num_files == 3:
            #     break # for testing
        print("Total number of files: %d" % num_files)
        print("# of invalid files: %d" % len(self.invalid_files))
        print("# of files which are not parsed: %d" % len(self.notparsed_files))
        print("invalid files: ")
        for invf in self.invalid_files:
            print(invf)
        print("not parsed files: ")
        for invf in self.notparsed_files:
            print(invf)

        for k in ks:
            print("Scores for k=%d" % k)
            self.get_scores(k)


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        results_fname_original = "st19-r4-results.csv"
        results_fname_title = "st19-r4-results-title.csv"
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
        o = ST19R4(results_fname, title_case=title_case)
        o.workflow(meta_fdir=meta_fdir, data_dir=data_dir, ks=[1, 3, 5])
        end = datetime.now()
        print("time consumed: "+str(end-start))
    else:
        print("Missing arguments: <meta file> <data directory> [<title/original>]")
