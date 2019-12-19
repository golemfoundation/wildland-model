# Core Wildland classes

from . edge_types import EdgeType
from . ns_graph import NameSpaceNode, NameSpacePath, NameSpace
from . storage import BackendStorage, BackendStorageWildland, StorageDriver
from . logger import Logger
from . ids import gen_uuid
from . resolve import verify_path, split_path_into_tokens
from . globals import *
import hashlib
import yaml

class WildlandManifest (yaml.YAMLObject):
    """A basis for a Wildland container."""

    def __init__ (self, wlm_actor_admin=None, content=[], paths=[]):

        # uuid is ephemeral and client isinstance-specific
        # We use it here mostly for easing visualization
        self.uuid = gen_uuid()
        self.original_wlm = None

        if wlm_actor_admin is None:
            self.id = self.uuid # TODO
            wlm_actor_admin = self
        self.wlm_actor_admin = wlm_actor_admin
        self.logger = Logger (self)
        self.logger.log (f"creating container owned by {self.wlm_actor_admin}")
        g_wlgraph.add_node (self)
        g_wlgraph.add_edge (self, self.wlm_actor_admin, type=EdgeType.owned_by)

        self.paths = []
        for path in paths:
            self.logger.log (f"- adding path: {Terminal().yellow}{path}")
            self.add_path (path)

        self.storage_manifests = []
        self.content = []
        for c in content:
            self.add_content (c)

    yaml_tag = u'!wlm'
    @classmethod
    def to_yaml(cls, dumper, wlm):
        dict_representation = {
            'uuid': wlm.uuid,
            'paths': wlm.paths,
            'storage_manifests': repr(wlm.storage_manifests),
            'content': wlm.content,
            'original_wlm' : wlm.original_wlm
        }
        node = dumper.represent_mapping(u'!wlm', dict_representation)
        return node

    def __repr__ (self):
        return f"wlm_{self.uuid:.8}"

    def add_path (self, path):
        verify_path (path)
        path_as_list = split_path_into_tokens (path)
        last_node = g_wlnamespace.add_path (
            self.wlm_actor_admin.id, *path_as_list)
        g_wlgraph.add_edge (last_node, self)
        self.paths.append (path)

    def add_content (self, c):
        self.content.append (c)
        self.store_content()
        
    def get_storage_manifests (self):
        return self.storage_manifests
        
    def add_storage_manifest (self, wlm_storage):
        if not isinstance (wlm_storage, WildlandStorageManifest):
            raise ValueError ("Need a WildlandStorageManifest object!")
        wlm_storage.container = self
        self.storage_manifests.append(wlm_storage)
        g_wlgraph.add_edge (self, wlm_storage, type=EdgeType.assigned)
        wlm_storage.update_admin (self.wlm_actor_admin)
        self.store_manifest()
        self.store_content()
        
    # Save the container manifest on the underlying storage backend
    def store_manifest (self):
        assert len(self.storage_manifests) > 0
        for s in self.storage_manifests:
            for path in self.paths:
                s.store_manifest(path=path, object=self)
    
    def store_content (self):
        # self.logger.log (f"store_content(): c={self.content}, s={self.storage_manifests}")
        for c in self.content:
            for s in self.storage_manifests:
                for path in self.paths:
                    s.store_content (path=path, object=c)

    def update_admin (self, wlm_actor_admin):
        g_wlgraph.remove_edge (self, self.wlm_actor_admin)
        self.wlm_actor_admin = wlm_actor_admin
        g_wlgraph.add_edge (self, self.wlm_actor_admin, type=EdgeType.owned_by)


class WildlandUserManifest (WildlandManifest):
    """A user/owner/admin of a container.

        When creating a new user, a storage manifest
    """

    def __init__ (self, wlm_storage_directory, paths=[]):

        self.paths = paths
        self.id = self.gen_pubkey()
        self.logger = Logger (self)
        self.original_storage_manifests = None

        self.logger.log (f"creating new user: {Terminal().blue}{paths[0]}, id = {self.id}")
        assert isinstance (wlm_storage_directory, WildlandStorageManifest)

        if wlm_storage_directory is None:
            raise ValueError ("WildlandUserManifest() must specify a storage manifest for its directory!")

        WildlandManifest.__init__ (self, wlm_actor_admin=self, paths=paths)
        WildlandManifest.add_storage_manifest (self, wlm_storage_directory)

    yaml_tag = u'!wlm_actor'
    @classmethod
    def to_yaml(cls, dumper, wlm):
        dict_representation = {
            'uuid': wlm.uuid,
            'pubkey': wlm.id,
            'paths': wlm.paths,
            'storage_manifests': repr(wlm.storage_manifests)
        }
        node = dumper.represent_mapping(u'!wlm_actor', dict_representation)
        return node

    def __repr__ (self):
        return f"wlm_actor_{self.id:.8}"

    def gen_pubkey (self):
        # We would like the "pubkey hash" to persist accorss runs
        # to allow for more complex experiments :)
        return f"0x{hashlib.sha256(self.paths[0].encode()).hexdigest()[1:8]}"

class WildlandStorageManifest (WildlandManifest):
    """A manifest assigned to a container, which tells where it is to be stored.
    """

    def __init__ (self, bknd_storage_backend):
        assert isinstance(bknd_storage_backend, BackendStorage)
        WildlandManifest.__init__ (self)
        self.bknd_storage_backend = bknd_storage_backend
        self.logger.log (f"adding storage manifest ({self}):")
        self.logger.log (f"backed on {bknd_storage_backend}")
        g_wlgraph.add_node (self)
        g_wlgraph.add_edge (self, self.bknd_storage_backend,
                            type=EdgeType.points)
    yaml_tag = u'!wlm_storage'
    @classmethod
    def to_yaml(cls, dumper, wlm):
        dict_representation = {
            'uuid': wlm.uuid,
            'container': repr(wlm.container),
            'backend' : repr (wlm.bknd_storage_backend)
        }
        node = dumper.represent_mapping(u'!wlm_storage', dict_representation)
        return node

    def __repr__ (self):
        return f"wlm_storage_{self.uuid:.8}"
    
    def get_backend(self):
        return self.bknd_storage_backend
        
    def encode_path_for_backend (self, path):
        return path.strip('/').replace('/','_').replace(' ','_')

    def store_manifest (self, path, object):
        path = self.encode_path_for_backend (path) + ".yaml"
        self.bknd_storage_backend.store_object (path=path, object=object)

    def store_content (self, path, object):
        path = self.encode_path_for_backend (path) + ".blob"
        self.bknd_storage_backend.store_object (path=path, object=object)

    def request_manifest (self, path):
        path = self.encode_path_for_backend (path) + ".yaml"
        return self.bknd_storage_backend.request_object(path)

    def request_content (self, path):
        path = self.encode_path_for_backend (path) + ".blob"
        return self.bknd_storage_backend.request_object(path)
