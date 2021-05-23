from annotator.annot import Annotator
from commons import ENDPOINT


class ExperimentBase:

    def __init__(self):
        self.annotator = Annotator(endpoint=ENDPOINT,
                      class_prefs=["http://dbpedia.org/ontology/", "http://www.w3.org/2002/07/owl#Thing"])
        self.not_founds = []
        self.fpath = None
        self.k = dict()

    def clear(self):
        self.not_founds = []
        self.fpath = None
        self.k = dict()

    def annotate_single(self, fpath, col_id):
        self.annotator.clear_for_reuse()
        self.fpath = fpath
        self.annotator.annotate_table(file_dir=fpath, subject_col_id=col_id)

    def validate_with_opt_alpha(self, correct_candidates, alpha_inc=0.01):
        alpha = 0.0
        kmin = None
        while alpha < 1:
            alpha += alpha_inc
            self.annotator.compute_f(alpha)
            candidates = self.annotator.get_top_k()

            if len(candidates) == 0:
                self.not_founds.append(self.fpath)
                return
            for idx, c in enumerate(candidates):
                k = idx + 1
                if c in correct_candidates:
                    if kmin is None or k < kmin:
                        kmin = k
                    if k == 1:
                        print("\n")
                        print("fpath: "+self.fpath)
                        print("candidates: ")
                        print(candidates[:3])
                        self.k[self.fpath] = k
                        return
        # Ahmad check case
        # if kmin is None:
        #     self.not_founds.append(self.fpath)
        #     return
        kmin = 999
        self.k[self.fpath] = kmin

    def get_scores(self, k):
        corr = 0.0
        incorr = 0.0
        notf = len(self.not_founds)
        for f in self.k:
            if self.k[f] <= k:
                corr += 1
            else:
                incorr += 1

        prec = corr/(corr+incorr)
        rec = corr/(corr+notf)
        f1 = 2.0 * prec * rec / (prec+rec)
        print("precision: %.2f" % prec)
        print("recall: %.2f" % rec)
        print("F1: %.2f" % f1)
        return prec, rec, f1