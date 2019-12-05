from globals import *
from logger import Logger
from reporting import dump_state
from ns_graph import NameSpace

# Barebones Init


def wl_barebones_init():

    print (
    """
      o       o   o    o o             o
      |       | o |    | |             |
      o   o   o   |  o-O |  oo o-o   o-O
       \ / \ /  | | |  | | | | |  | |  |
        o   o   | o  o-o o o-o-o  o  o-o
    """
    )
    # figlet fonts credits:
    # Tinker-toy by Wendell Hicken 11/93 (whicken@parasoft.com)

    Logger.log ("Wildland client barebones init")
    g_wlgraph.add_node('@namespace')
