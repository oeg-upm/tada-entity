import os
import subprocess
import json
from basic_graph import BasicGraph, Node


class TypeGraph(BasicGraph):

    def __init__(self, *args, **kwargs):
        self.m = 0
        super(TypeGraph, self).__init__(*args, **kwargs)

    def verify_roots(self):
        # just to test the roots
        print "checking root"
        for t in self.cache:
            node = self.index[t]
            if node.parents == [] and node not in self.roots:
                print "checking root> %s" % node.title
                print "parents: %s " % (str([p.title for p in node.parents]))
                print "childs: %s" % (str([ch.title for ch in node.childs]))
                raise Exception("checking root error")

    # new specificity function
    def fs(self, node, delta=0.01, epsilon=10):
        """
        function that computes the specificity of a node

                      1                         1
        fs(x, d) = ---------------------  -  ----------- + 1
                    (Lc(node)+1)^10           (d+1)^0.1

        more generally,
                      1                        1
        fs(x, d) = ---------------------- - ----------- + 1
                    (Lc(node)+1)^epsilon    (d+1)^delta

        :param node: node
        :return: the specificity score
        """
        l = node.path_specificity
        d = node.depth
        fs_score = 1.0/(l+1)**epsilon - 1.0/(d+1)**delta + 1
        return fs_score

    def fc(self, node, m):
        """
        actually exists in the annotator module.
        a function that compute the coverage score of a given node
        :param node: node
        :param m: the number of cells that has entities and types
        :return: the coverage score
        """
        if m==0:
            print "m is zero for node: %s" % (node.title)
        return node.coverage_score/m

    def break_cycles(self, log_path=None):
        for r in self.roots:
            self.dfs_break_cycle(visited=[r], log_path=log_path)

    def dfs_break_cycle(self, visited, log_path):
        node = visited[-1]
        for ch in node.childs:
            if ch in visited:  # there is a cycle
                print "\n\n******CYCLE*****"
                print "%s -> %s\n\n\n" % (node.title, ch.title)
                if log_path is not None:
                    comm = 'echo "%s, %s" >> %s' % (node.title, ch.title, os.path.join(log_path, 'tadaa_cycles.txt'))
                    print "comm: %s" % comm
                    subprocess.call(comm, shell=True)
                # raise Exception("boom")
                self.remove_edge(node, ch)
            else:
                self.dfs_break_cycle(visited=visited+[ch], log_path=log_path)

    def draw_with_score_separate(self):
        for idx, r in enumerate(self.roots):
            self.draw_score_for_root(r, "%d_graph.gv"%idx)

    def get_scores(self):
        nodes = []
        for n in self.roots:
            nodes += self.get_score_for_node(n)
        nodes = list(set(nodes))
        return sorted(nodes, key=lambda node: node.score, reverse=True)

    def get_score_for_node(self, node):
        nodes = [node]
        for child in node.childs:
            nodes += self.get_score_for_node(child)
        return nodes

    def set_score_for_graph(self, coverage_weight=0.5, m=1):
        """
        :param coverage_weight: the alpha
        :param coverage_norm: since coverage is actually increase when the number of entities increase, we need to
        normalize the coverage score by dividing it with the coverage_norm
        :return:
        """
        for n in self.roots:
            self.set_score_for_node(n, coverage_weight, m)

    def set_score_for_node(self, node, coverage_weight, m):
        if node.score != -1:
            return
        node.score = coverage_weight * self.fc(node=node, m=m) + (1-coverage_weight) * self.fs(node)
        for child in node.childs:
            self.set_score_for_node(child, coverage_weight, m)

    def set_converage_score(self):
        for n in self.roots:
            print 'set coverage root: %s' % n.title
            self.compute_coverage_score_for_node(n)

    def compute_coverage_score_for_node(self, node):
        print 'enter in %s' % node.title
        if node._coverage_computed:
            return node.coverage_score
        for child in node.childs:
            node.coverage_score += self.compute_coverage_score_for_node(child)
        if len(node.childs) == 0:
            print 'leave score of %s: %g' % (node.title, node.coverage_score)
        else:
            print 'mid score of %s: %g' % (node.title, node.coverage_score)
        print 'leaving %s' % node.title
        node._coverage_computed = True
        return node.coverage_score

    def set_path_specificity(self):
        for n in self.get_leaves_from_graph():
            self.set_path_specificity_for_node(n)

    def set_path_specificity_for_node(self, node):  # solve bug #2
        if node.path_specificity == -1:
            if node.parents == []:
                node.path_specificity = 1
            else:
                node.path_specificity = min([self.set_path_specificity_for_node(p) for p in node.parents]) * node.specificity_score
        return node.path_specificity

    # iteration 8
    def set_nodes_subjects_counts(self, d):
        for n in self.roots:
            self.set_subjects_count_for_node(n, d)

    def set_subjects_count_for_node(self, node, d):
        if node.num_of_subjects != -1:  # it is already set
            return
        for child in node.childs:
            self.set_subjects_count_for_node(child, d)
        if node.title in d:
            node.num_of_subjects = int(d[node.title])
        else:
            node.num_of_subjects = 0
            raise Exception("in iteration 8 this should not happen as we are checking the childs as well")

    def set_specificity_score(self):
        for n in self.roots:
            self.compute_specificity_for_node(n)

    def compute_specificity_for_node(self, node):
        if node.specificity_score != -1:  # if specificity score is computed
            return

        if node.parents == []:
            node.specificity_score = 1
        else:
            for p in node.parents:
                node.specificity_score = node.num_of_subjects * 1.0 / max([p.num_of_subjects for p in node.parents])

        for child in node.childs:
            self.compute_specificity_for_node(child)

    def set_depth_for_graph(self):
        for n in self.roots:
            n.depth = 0
        for t in self.cache:
            n = self.find_v(t)
            self.set_depth_for_node(n)

    def set_depth_for_node(self, node):
        if node.depth == -1:  # depth is not set

            if(len(node.parents)==0):
                node.depth = 0
                self.roots.append(node)
                return node.depth
            max_node = node.parents[0]
            self.set_depth_for_node(max_node)
            for p in node.parents[1:]:
                self.set_depth_for_node(p)
                if self.set_path_specificity_for_node(p) > max_node.path_specificity:
                    max_node = p
            node.depth = 1 + max_node.depth

        return node.depth

    def save_to_string(self):
        j = {}
        for title in self.cache:
            node = self.index[title]
            j[title] = {
                "title": title,
                "Lc": node.coverage_score,
                "Ls": node.path_specificity,
                "d": node.depth,
                "childs": [n.title for n in node.childs]
            }
        s = json.dumps(j)
        print "graph in str: "
        print s
        return s

    def save(self, abs_file_dir):
        f = open(abs_file_dir, 'w')
        j = {}
        for title in self.cache:
            node = self.index[title]
            j[title] = {
                "title": title,
                "Lc": node.coverage_score,
                "Ls": node.path_specificity,
                "d": node.depth,
                "childs": [n.title for n in node.childs]
            }
        json.dump(j, f)
        f.close()
        f = open(abs_file_dir, 'r')
        return f

    def load(self, j, m):
        self.m = m
        titles = j.keys()
        # add nodes
        for t in titles:
            self.add_v(t, parents=None)
        # add paths
        for t in titles:
            for ch in j[t]["childs"]:
                self.add_e(t, ch)
        # infer and set the roots
        self.build_roots()
        # set other attributes:
        for t in titles:
            jn = j[t]
            node = self.index[t]
            node.coverage_score = jn["Lc"]
            node.path_specificity = jn["Ls"]
            node.depth = jn["d"]

        self.set_labels()

    def set_labels(self):
        for t in self.cache:
            node = self.index[t]
            #node.label = clean_with_score(node)
            node.label = clean_with_f_scores(self, node)


def clean_with_score(n):
    return "%s cove(%g) num(%d) depth(%d) pspec(%f) score(%f)" % (
        clean(n.title), n.coverage_score, n.num_of_subjects, n.depth, n.path_specificity, n.score)


def clean_with_f_scores(g, n):
    title = "/".join(clean(n.title).split('/')[-2:])
    return "%s fc(%g) fs(%g)" % (title, g.fc(n, g.m), g.fs(n))


def clean(s):
    return s.replace("http://", "")
