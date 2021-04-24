

class Node:

    def __init__(self):
        self.class_uri = ""
        self.Ic = None
        self.Lc = None
        self.fc = None
        self.Is = None
        self.Ls = None
        self.fs = None
        self.parents = dict()  # to nodes
        self.childs = dict()  # to nodes

    def clear(self):
        self.Ic = None
        self.Lc = None
        self.fc = None
        self.Is = None
        self.Ls = None
        self.fs = None


class TGraph:

    def __init__(self):
        self.nodes = dict()  # to nodes
        self.roots = dict()  # to nodes
        self.m = 0

    def add_class(self, class_uri):
        if class_uri in self.nodes:
            return False
        else:
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
            for p in self.get_parents(class_uri):
                ancestors.append(p)
                ancestors += self.get_ancestors(p)
            return ancestors
            # return list(set(ancestors))
        else:
            print("get_ancestors: <%s> is not added" % class_uri)
            return None

    def clear_scores(self):
        for node in self.nodes:
            node.clear()
