# Classes respresenting storage for Wildland

from globals import *
from edge_types import EdgeType
from logger import Logger
from ns_graph import NameSpaceNode, NameSpacePath, NameSpace
from resolve import wl_resolve_recursively, split_path_into_tokens

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

    # This simulates normal, Wildland-agnostic request for a blob (file):
    def request_raw_data (self, request):
        Logger.log (f"{self}: got REQUEST for blob: {request}", icon='B')
            
    # Note: in real implentation the backend will not need to do any resolve
    # since it would just return the requested file/key -- but as we're
    # not using any backing for storage it needs to actually do the
    # graph trabersing
    
    def request_resolve (self, request):
        
        Logger.log (f"{self}: got REQUEST: {request}", icon='B')
        # Lets actually find what the backend would normaly return
        # Of course in practical scenario, the backend would not have
        # a full view of the Graph. And might be as simple as a static
        # file server of key-dir server. 
        path_as_list = split_path_into_tokens(request)

        Logger.log (f"{self}: traversing the NameSpace tree: (ONLY in Simulation!) ", 'B')
        Logger.nest_up()
        prev_node = '@namespace'
        for token in path_as_list:
            next_node = None
            for node in g_wlgraph.successors(prev_node):
                if node.name == token:
                    next_node = node
                    break
            if next_node is None:
                raise LookupError
            Logger.log (f"{node.name}", 'B')
            prev_node = node
        Logger.nest_down()
        containers = g_wlgraph.successors(prev_node)
        Logger.log (f"{self}: found {len(containers)} container(s):"
                f" - {[c for c in containers]}", 'B')
        container = containers[0] # TODO: support more
        Logger.log (f"{self}: using 1st from the list: {container}", 'B')
        if container.original_wlm is not None:
            Logger.log (f"{self}: using the original container: {container.original_wlm}", 'B')
            container = container.original_wlm
        Logger.log (f"{self}: RESPONSE: {container}.yaml (incl. storage manifest(s))", 'B')
        return container
        
        

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
