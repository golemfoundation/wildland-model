# Classes respresenting storage for Wildland

from globals import *
from edge_types import EdgeType
from logger import Logger
from ns_graph import NameSpaceNode, NameSpacePath, NameSpace
from utils import wl_resolve_recursively

class BackendStorage:
    """A specific storage backend (e.g. specific S3 bucket or WebDAV URL)

        This includes:
        - backend type/protocol (e.g. local, S3, WebDAV, etc.)
        - user-specifc configuration (e.g. S3 bucket name)
        - optional other arguments (e.g. AWS access credentials)
    """

    def __init__(self, type, friendly_name=""):
        Logger.log (f"creating storage {type} backend {friendly_name}")

        self.type = type
        self.friendly_name = friendly_name
        if type not in g_drivers_storage:
            self.drv = StorageDriver(type)
            g_drivers_storage[type] = self.drv
        else:
            self.drv = g_drivers_storage[type]

        g_wlgraph.add_edge (self, self.drv, type=EdgeType.provided_by)
        # A node respresenting mounted fs tree (not a Container)
        self.ns = NameSpace (self, g_wlgraph)

    def __repr__ (self):
        return f"bknd_storage_{self.type}_{self.friendly_name}"

class BackendStorageWildland (BackendStorage):
    """A storage implemented on top of a Wildland container. Turtles..."""

    def __init__ (self, uid, path):
    # def __init__ (self, backend_container):
        self.type='wildland'
        self.backend_container = wl_resolve_recursively (uid, path)
        self.friendly_name =\
            f"{uid.id}:{path}"
        g_wlgraph.add_edge (self, self.backend_container, type=EdgeType.stored_at)

class StorageDriver:
    """A protocol-sepcific storage driver. One for each type of storage.

        Abstracts from the actual user-specific config options,
        such as buckets, uids, keys, etc.
    """
    def __init__ (self, type):
        self.type=type
        Logger.log (f"loading storage driver: {type}")
        g_wlgraph.add_node (self)
        # g_wlgraph.add_edge ('@storage', self)

    def __repr__ (self):
        return f"drv_storage_{self.type}"

    def __hash__(self):
        # We need only one driver for each type/protocol of storage
        return hash((self.type))
