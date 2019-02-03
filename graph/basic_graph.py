class Node:
    def __init__(self):
        self.__init__('default')

    def __init__(self, title):
        self.title = title
        self.parents = []
        self.childs = []
        self.coverage_score = 0
        self.specificity_score = -1
        self._coverage_computed = False
        self.num_of_subjects = -1
        self.path_specificity = -1
        self.score = -1
        self.depth = -1
        self.label = 'label'

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return self.title


class BasicGraph(object):
    def __init__(self):
        self.roots = []  # a list of nodes that has no parents (e.g. roots)
        self.cache = []  # this is used to check whether an item is in the graph or not
        self.index = {}  # like a hash table to access a node by its title

    def add_v(self, title, parents):
        """
        :param title:
        :param parents: a list of parents
        :return:
        """
        if title in self.cache:
            print "%s already in the graph" % title
            return

        node = Node(title=title)
        print "%s new to the graph" % node.title
        self.index[title] = node  # title should not be previously in the index
        self.cache.append(title)
        if parents is None:
            pass
        elif parents == [] and node not in self.roots:
            self.roots.append(node)
        else:
            parents = [self.find_v(p) for p in parents]
            node.parents += parents
            node.parents = list(set(node.parents))
            for pnode in parents:
                pnode.childs.append(node)
                pnode.childs = list(set(pnode.childs))

    def add_e(self, from_title, to_title):
        parent_node = self.index[from_title]
        child_node = self.index[to_title]
        if child_node not in parent_node.childs:
            parent_node.childs.append(child_node)
        if parent_node not in child_node.parents:
            child_node.parents.append(parent_node)

    def remove_edge(self, from_node, to_node):
        from_node.childs.remove(to_node)
        to_node.parents.remove(from_node)
        if to_node.parents == []:
            self.roots.append(to_node)

    def build_roots(self):
        for n in self.cache:
            node = self.index[n]
            if node.parents == [] and len(node.childs) > 0:
                self.roots.append(node)
        self.roots = list(set(self.roots))

    def remove_lonely_nodes(self):
        removed_titles = []
        for n in self.cache:
            node = self.index[n]
            if node.parents == node.childs == []:
                # del self.index[n]
                # self.cache.remove(n)
                removed_titles.append(n)
        for n in removed_titles:
            del self.index[n]
            self.cache.remove(n)
        return removed_titles

    def break_cycles(self):
        for r in self.roots:
            self.dfs_break_cycle([r])
        # breaking cycles which remove edges can cause nodes with no parents which are not initially in the roots
        self.fix_roots()

    def dfs_break_cycle(self, visited):
        node = visited[-1]
        for ch in node.childs:
            if ch in visited:  # there is a cycle
                self.remove_edge(node, ch)
            else:
                self.dfs_break_cycle(visited=visited+[ch])

    def fix_roots(self):
        for title in self.index.keys():
            node = self.index[title]
            if len(node.parents) == 0 and node not in self.roots:
                self.roots.append(node)
                print "fixing root %s" % node.title

    def find_v(self, title):
        if title in self.index:
            return self.index[title]
        return None

    def draw(self, file_name='graph.gv'):
        from graphviz import Digraph
        dot = Digraph(comment='The Round Table')
        for n in self.cache:
            dot.node(clean(n))
        print "draw nodes"
        for n in self.cache:
            node = self.index[n]
            for ch in node.childs:
                dot.edge(clean(n), clean(ch.title))
        dot.render(file_name, view=True)

    def get_all_child_nodes(self, node, visited):
        """
        called by draw_score_for_root
        :param node:
        :param visited:
        :return:
        """
        if node in visited:
            print "cycle node: %s" % node.title
            return visited
        visited_local = visited[:] + [node]

        for ch in node.childs:
            visited_local = self.get_all_child_nodes(ch, visited_local)
        return visited_local

    def get_leaves_from_graph(self):
        leaves = []
        for n in self.roots:
            leaves += self.get_leaves_of_node(n)
        return list(set(leaves))

    def get_leaves_of_node(self, node):
        if node.childs == []:
            return [node]
        leaves = []
        for child in node.childs:
            leaves += self.get_leaves_of_node(child)
        return leaves

    def get_edges(self):
        edges = []
        for t in self.cache:
            node = self.index[t]
            for ch in node.childs:
                e = (node.title, ch.title)
                edges.append(e)
        return edges


def clean(s):
    return s.replace("http://", "")
