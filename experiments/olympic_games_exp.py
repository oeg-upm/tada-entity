from experiments.experiment_base import ExperimentBase
import os
import sys


class Olympic(ExperimentBase):

    def __init__(self):
        super().__init__()

    def workflow(self, meta_fdir, data_dir, k):
        f = open(meta_fdir)
        for line in f.readlines():
            fname, class_name = line.split(",")
            fdir = os.path.join(data_dir, fname)
            class_uri = "http://dbpedia.org/ontology/"+class_name
            self.annotate_single(fpath=fdir, col_id=0)
            self.validate_with_opt_alpha(correct_candidates=[class_uri], k=k)
        print("Scores for k=%d" % k)
        self.get_scores()


if __name__ == "__main__":
    if len(sys.argv) == 3:
        meta_fdir, data_dir = sys.argv[1:]
        o = Olympic()
        for k in [1,3,5]:
            o.workflow(meta_fdir=meta_fdir, data_dir=data_dir, k = k)
            o.clear()
    else:
        print("Missing arguments: <meta file> <data directory>")
