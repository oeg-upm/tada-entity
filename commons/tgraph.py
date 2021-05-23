

class Node:

    def __init__(self):
        self.class_uri = ""
        self.Ic = None
        self.Lc = None
        self.fc = None
        self.Is = None
        self.Ls = None
        self.fs = dict()
        self.f = dict()
        # self.fs = None
        # self.fs1 = None
        # self.fs2 = None
        # self.fs3 = None
        # self.fs4 = None
        # self.fs5 = None
        # self.f = None
        # self.f1 = None
        # self.f2 = None
        # self.f3 = None
        # self.f4 = None
        # self.f5 = None
        self.parents = dict()  # to nodes
        self.childs = dict()  # to nodes

    def clear(self):
        self.Ic = None
        self.Lc = None
        self.fc = None
        self.Is = None
        self.Ls = None
        self.fs = dict()
        self.f = dict()
        # self.fs = None
        # self.fs1 = None
        # self.fs2 = None
        # self.fs3 = None
        # self.fs4 = None
        # self.fs5 = None
        # # self.f = None
        # self.f1 = None
        # self.f2 = None
        # self.f3 = None
        # self.f4 = None
        # self.f5 = None

    def print(self):
        print("fc: %s" % str(self.fc))
        for i in range(1, 6):
            if i in self.fs:
                print("fs%d: %s" % (i, str(self.fs[i])))
            else:
                print("fs%d: does not exist" % i)
        print("f: %s" % str(self.f))


class TGraph:

    def __init__(self):
        self.nodes = dict()  # to nodes
        self.roots = dict()  # to nodes
        self.m = 0

    def clear_for_reuse(self):
        self.m = 0
        for class_uri in self.nodes:
            node = self.nodes[class_uri]
            node.Ic = node.Lc = node.fc = None
            node.f = dict()

    def add_class(self, class_uri):
        if class_uri in self.nodes:
            return False
        else:
            # print("add class: "+class_uri)
            self.nodes[class_uri] = Node()
            self.nodes[class_uri].class_uri = class_uri
            return True

    def get_parents(self, class_uri):
        if class_uri in self.nodes:
            return list(self.nodes[class_uri].parents.keys())
        else:
            return None

    def get_childs(self, class_uri):
        if class_uri in self.nodes:
            return list(self.nodes[class_uri].childs.keys())
        else:
            print("get_childs: <%s> does not exists in the nodes " % class_uri)
            return None

    def add_parent(self, class_uri, parent_uri):
        # print("add to %s %s as a parent" % (class_uri, parent_uri))
        if class_uri in self.nodes and parent_uri in self.nodes:
            if parent_uri not in self.nodes[class_uri].parents:
                self.nodes[class_uri].parents[parent_uri] = self.nodes[parent_uri]
                self.nodes[parent_uri].childs[class_uri] = self.nodes[class_uri]
                return True
            return False
        else:
            print("parent uri: <%s> does not exists in the nodes " % parent_uri)
            return None

    def get_ancestors(self, class_uri):
        ancestors = []
        if class_uri in self.nodes:
            # print("get_ancestors> parents of %s" % class_uri)
            for p in self.get_parents(class_uri):
                # print("get_ancestors>: "+p)
                ancestors.append(p)
                # ancestors += self.get_ancestors(p)
                p_ancestors = self.get_ancestors(p)
                ancestors += p_ancestors
            return ancestors
            # return list(set(ancestors))
        else:
            print("get_ancestors: <%s> is not added" % class_uri)
            return None

    def clear_scores(self):
        for node in self.nodes:
            node.clear()

    def print_scores(self):
        for class_uri in self.nodes:
            node = self.nodes[class_uri]
            node.print()


