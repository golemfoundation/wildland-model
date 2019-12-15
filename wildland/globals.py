# Core global objects

import networkx as nx
from . ns_graph import NameSpace
from . logger import Logger

g_wlgraph = nx.DiGraph()
g_drivers_storage = {}
g_wlnamespace = NameSpace (g_wlgraph, '@namespace')

g_logger = Logger ()
