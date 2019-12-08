# Helper classes for building graph respresenting The Wildland NameSpace

from edge_types import EdgeType
from ids import gen_uuid

class NameSpaceNode:
    """A node for use in namespace graphs."""
    def __init__ (self, name, *path):
        # self.uuid = gen_uuid()
        self.name = name

        # Make sure nodes are uniqe,
        # e.g. ensure that `b` in `/a/b/c` and `/x/b/c` will not
        # be represented by the same node in the graph.
        self.path = "/".join(*path)

    def __hash__ (self):
        return hash(f"{self.path}/{self.name}")

    def __eq__(self, other):
        return hash(self) == hash(other)

class NameSpacePath:
    """A linear subgraph forming a filesystem-like path."""

    def __init__ (self, G, root, *path_as_list_of_tokens):
        self.G = G
        self.root = root
        prev_node = root
        path_to_token = []
        for token in path_as_list_of_tokens:
            node = NameSpaceNode (token, path_to_token)
            G.add_node (node)
            G.add_edge (prev_node, node, type=EdgeType.points)
            prev_node = node
            path_to_token.append (token)

        self.last_node = prev_node

class NameSpace:
    """A collection of NameSpacePath objects."""

    def __init__ (self, G=None, root=None):
        self.G = G
        self.root = root
        self.paths = set()

    def add_path (self, *path_as_list_of_tokens):
        p = NameSpacePath (self.G, self.root, *path_as_list_of_tokens)
        self.paths.add (p)
        return p.last_node
