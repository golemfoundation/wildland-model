# Core global objects

import networkx as nx
from ns_graph import NameSpace

g_wlgraph = nx.DiGraph()
g_drivers_storage = {}
g_wlnamespace = NameSpace (g_wlgraph, '@namespace')
