

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
            return None

    def add_parent(self, class_uri, parent_uri):
        if class_uri in self.nodes and parent_uri in self.nodes:
            if parent_uri not in self.nodes[class_uri].parents:
                self.nodes[class_uri].parents[parent_uri] = self.nodes[parent_uri]
                self.nodes[parent_uri].childs[class_uri] = self.nodes[class_uri]
                return True
            return False
        raise Exception("parent uri: <%s> does not exists in the nodes " % parent_uri)
