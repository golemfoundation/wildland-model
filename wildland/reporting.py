# Graph and other reporting functions

import os
import yaml
from datetime import datetime

from . globals import *
from . logger import Logger
from . core import WildlandManifest, WildlandUserManifest, WildlandStorageManifest
from . storage import BackendStorage, BackendStorageWildland, StorageDriver
from . ns_graph import NameSpaceNode, NameSpace
from . edge_types import EdgeType

def dump_graph_with_graphviz (G, filepath, description):

    for n in list (g_wlgraph.adj):
        # default node style
        G.node[n] = {
            'shape': 'box',
            # 'style': 'rounded',
            'penwidth': 0.5,
            'fontsize': 12,
        }
        if isinstance (n, WildlandUserManifest):
            G.node[n]['label']=f"id:{n.id:.8}\nuuid:{n.uuid:.8}\n(user manifest)"
        elif isinstance (n, WildlandStorageManifest):
            G.node[n]['label']=f"uuid:{n.uuid:.8}\n(storage manifest)"
            G.node[n]['style'] = 'filled'
            G.node[n]['fillcolor'] = 'gray90'
        elif isinstance (n, WildlandManifest):
            G.node[n]['label']=f"uuid:{n.uuid:.8}\n(container manifest)"
            G.node[n]['penwidth']=2
        elif isinstance (n, NameSpaceNode):
            G.node[n]['label']=f"{n.name}"
            G.node[n]['shape']='plaintext'
        elif isinstance (n, BackendStorageWildland):
            G.node[n]['label'] = f"wildland backend:\n{n.friendly_name}"
            G.node[n]['style'] = 'filled'
            G.node[n]['penwidth']=0.5
            G.node[n]['pencolor']='black'
        elif isinstance (n, BackendStorage):
            G.node[n]['label'] = f"backend:\n{n.friendly_name}"
            G.node[n]['style'] = 'filled'
            G.node[n]['color'] = 'gray90'
        elif isinstance (n, StorageDriver):
            G.node[n]['label']=f"driver:{n.type}"
            G.node[n]['style'] = 'filled'
            G.node[n]['color'] = 'gray'
        if n == '@namespace':
            G.node[n]['shape'] = 'plaintext'
            G.node[n]['label'] = "The Wildland NameSpace"
        if n == '@default_directory':
            G.node[n]['shape'] = 'plaintext'

    for u, v, type in G.edges(data='type'):
        if type is not None:
            G[u][v]['label'] = type
            G[u][v]['fontsize'] = 8

            if type == EdgeType.owned_by:
                G[u][v]['style'] = 'dotted'
            elif type == EdgeType.stored_at:
                G[u][v]['penwidth'] = 1
            elif type == EdgeType.points:
                G[u][v]['label'] = ""
                G[u][v]['penwidth'] = 0.2
            elif type == EdgeType.content:
                G[u][v]['penwidth'] = 0.2
                G[u][v]['style'] = 'dotted'

    # convert to pyGraphviz's AGraph object
    vizG = nx.nx_agraph.to_agraph(G)

    # vizG.graph_attr['label'] = description
    vizG.graph_attr['fontsize'] = 10
    vizG.edge_attr['arrowhead'] = 'onormal'
    vizG.edge_attr['penwidth'] = '0.2'

    vizG.add_subgraph(['@namespace', '@default_directory'],
        rank='same')

    vizG.add_subgraph([n for n in G.neighbors ('@namespace')],
        rank='same')
    vizG.add_subgraph([n for n in list (G.adj)
        if isinstance (n, StorageDriver)], rank='sink')

    # vizG.write(f"{filepath}.dot")
    vizG.layout(prog='dot')
    vizG.draw (f"{filepath}.pdf")

# def dump_graph_with_matplotlib (filepath, description):
#     # pos = nx.drawing.layout.spring_layout(G)
#     nx.draw_shell(G, with_labels=True)
#     plt.savefig (f"{filepath}.pdf")

def check_and_report_cycles (graph):
    g_logger.log ("checking for cycles in graph")
    g_logger.nest_up()
    cycles = list(nx.simple_cycles(graph))
    if len(cycles):
        g_logger.log (f"WARNING(!): Found {len(cycles)} cycles in graph:", icon='!')
        for c in cycles:
            g_logger.log (f"{c}")
        # raise AssertionError
    g_logger.nest_down()

import sys
import os.path
def prep_output_dir ():
    now = datetime.now()
    timestamp = f"{now.year}-{now.month:02}-{now.day:02}-{now.hour:02}{now.minute:02}{now.second:02}"
    global outdir
    outdir = f"./output/run-{timestamp}-{os.path.basename(sys.argv[0])}"
    g_logger.log (f"Preparing output dir for this run: {outdir}")
    os.mkdir (outdir)

def dump_yaml_for_node (filepath, n):
    # g_logger.log (f"dumping yaml for node {n}")

    with open (filepath, "w") as stream:
        yaml.dump (n, stream)

def dump_yamls(G, dirpath):
    g_logger.log (f"dumping yamls to {dirpath}")
    g_logger.nest_up()
    os.mkdir (dirpath)
    for n in list (g_wlgraph.adj):
        if isinstance (n, WildlandManifest) or isinstance (n, BackendStorage):
            filepath = f"{dirpath}/{n}.yaml"
            dump_yaml_for_node (filepath, n)
    g_logger.nest_down()

def dump_state(description="state dump", clients=[]):
    if 'iter' not in dump_state.__dict__:
        dump_state.iter = 0

    title = f"{description}, i = {dump_state.iter}"
    filepath = f"{outdir}/G-{dump_state.iter}"
    g_logger.log (f"dumping state as G-{dump_state.iter}", icon='*')
    dump_yamls (g_wlgraph, f"{outdir}/yamls-{dump_state.iter}/")
    dump_graph_with_graphviz(nx.DiGraph(g_wlgraph), filepath, title)


    # Create a copy of the graph with signed relations removed
    # and check the resulting graph for loops:
    storage_graph = nx.DiGraph (g_wlgraph)
    for u, v, type in storage_graph.edges(data='type'):
        if type == EdgeType.owned_by:
            storage_graph.remove_edge(u,v)
    check_and_report_cycles (storage_graph)

    for cli in clients:
        filepath = f"{outdir}/cli-{dump_state.iter}-{cli.me}"    
        cli.dump (filepath)
    dump_state.iter += 1
