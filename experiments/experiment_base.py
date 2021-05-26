from annotator.annot import Annotator
from commons import ENDPOINT


class ExperimentBase:

    def __init__(self, log_fname=None, title_case=False):
        self.annotator = Annotator(endpoint=ENDPOINT, title_case=title_case,
                                   class_prefs=["http://dbpedia.org/ontology/", "http://www.w3.org/2002/07/owl#Thing"])
        self.not_founds = []
        self.total_processed = 0
        self.col_id = None
        self.fpath = None
        self.k = dict()
        self.log_fname = log_fname
        if log_fname:
            f = open(log_fname, "w")
            f.write(",".join(["fname", "colid" , "fs", "alpha", "k"])+"\n")
            f.close()
        for i in range(1, 6):
            self.k[i] = dict()

    def append_line(self, line):
        if self.log_fname:
            f = open(self.log_fname, "a")
            f.write(line+"\n")
            f.close()

    def clear(self):
        self.not_founds = []
        self.fpath = None
        self.col_id = None
        self.k = dict()
        for i in range(1, 6):
            self.k[i] = dict()

    def annotate_single(self, fpath, col_id):
        self.annotator.clear_for_reuse()
        self.fpath = fpath
        self.col_id = col_id
        self.annotator.annotate_table(file_dir=fpath, subject_col_id=col_id)

    def validate_with_opt_alpha(self, correct_candidates, alpha_inc=0.001):
        print("\n")
        print("fpath: %s - col id: %d" %(self.fpath, self.col_id))
        for i in range(1, 6):
            self.validate_with_opt_alpha_fsid(correct_candidates, fsid=i, alpha_inc=alpha_inc)

    def validate_with_opt_alpha_fsid(self, correct_candidates, fsid, alpha_inc=0.01):
        alpha = 0.0
        kmin = None
        max_alpha = None
        while alpha < 1:
            alpha += alpha_inc
            self.annotator.compute_f(alpha)
            candidates = self.annotator.get_top_k(fsid=fsid)

            if len(candidates) == 0:
                if self.fpath not in self.not_founds:
                    self.not_founds.append(self.fpath)
                return
            for idx, c in enumerate(candidates):
                k = idx + 1
                if c in correct_candidates:
                    if kmin is None or k < kmin:
                        kmin = k
                        max_alpha = alpha
                    if k == 1:
                        self.append_line(",".join([self.fpath.split("/")[-1], str(self.col_id), str(fsid), str(max_alpha), str(kmin)]))
                        # self.append_line(",".join([self.fpath.split("/")[-1], str(fsid), str(max_alpha), str(kmin)]))
                        print("candidates (%d): %s" % (fsid, str(candidates[:3])))
                        self.k[fsid][self.fpath + str(self.col_id)] = k
                        return
        # Ahmad check case
        # if kmin is None:
        #     self.not_founds.append(self.fpath)
        #     return
        if kmin is None:
            print("Special case: "+self.fpath)
            kmin = 999

        self.k[fsid][self.fpath + str(self.col_id)] = kmin
        self.append_line(",".join([self.fpath.split("/")[-1], str(self.col_id), str(fsid), str(max_alpha), str(kmin)]))
        print("max alpha: %s (fs%d)" % (str(max_alpha), fsid))

    def get_scores(self, k):
        for i in range(1, 6):
            self.get_scores_fsid(k, i)
        total_processed = len(self.not_founds)+len(self.k[1])
        print("total processed: %d\n\n" % total_processed)
        self.total_processed = total_processed

    def get_scores_fsid(self, k, fsid):
        corr = 0.0
        incorr = 0.0
        notf = len(self.not_founds)
        for f in self.k[fsid]:
            if self.k[fsid][f] <= k:
                corr += 1
            else:
                incorr += 1
        if (corr+incorr) > 0:
            prec = corr/(corr+incorr)
        else:
            prec = 0
        if (corr+notf) > 0:
            rec = corr/(corr+notf)
        else:
            rec = 0
        if (prec+rec) > 0:
            f1 = 2.0 * prec * rec / (prec+rec)
        else:
            f1 = 0
        print("fsid: %d" % fsid)
        print("precision: %.2f" % prec)
        print("recall: %.2f" % rec)
        print("F1: %.2f" % f1)
        return prec, rec, f1
