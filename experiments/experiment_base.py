from annotator.annot import Annotator
from commons import ENDPOINT


class ExperimentBase:

    def __init__(self):
        self.annotator = Annotator(endpoint=ENDPOINT,
                      class_prefs=["http://dbpedia.org/ontology/", "http://www.w3.org/2002/07/owl#Thing"])
        self.not_founds = []
        self.corrs = []
        self.incorrs = []
        self.fpath = None

    def clear(self):
        self.not_founds = []
        self.corrs = []
        self.incorrs = []

    def annotate_single(self, fpath, col_id):
        self.annotator.clear_for_reuse()
        self.fpath = fpath
        self.annotator.annotate_table(file_dir=fpath, subject_col_id=col_id)

    # def validate_top_k(self, alpha, k=1, correct_candidates=[]):
    #     self.recompute_alpha(alpha)
    #     candidates = self.get_top_k(k)

    def validate_with_opt_alpha(self, correct_candidates, alpha_inc=0.01, k=1):
        alpha = 0
        while alpha < 1:
            alpha += alpha_inc
            self.recompute_alpha(alpha)
            candidates = self.get_top_k(1)
            if len(candidates) == 0:
                self.not_founds.append(self.fpath)
                return
            for c in candidates[:k]:
                if c in correct_candidates:
                    self.corrs.append(self.fpath)
                    return

        self.incorrs.append(self.fpath)

    def get_scores(self):
        corr = len(self.corrs) * 1.0
        incorr = len(self.incorrs)
        notf = len(self.not_founds)

        prec = corr/(corr+incorr)
        rec = corr/(corr+notf)
        f1 = 2.0 * prec * rec / (prec+rec)
        print("precision: %.2f" % (prec))
        print("recall: %.2f" % (rec))
        print("F1: %.2f" % (f1))
        return prec, rec, f1
