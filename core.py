# Core Wildland classes

from edge_types import EdgeType
from ns_graph import NameSpaceNode, NameSpacePath, NameSpace
from storage import BackendStorage, BackendStorageWildland, StorageDriver
from logger import Logger
from ids import gen_uuid
from utils import verify_path, split_path_into_tokens
import hashlib
import yaml
from globals import *

class WildlandManifest (yaml.YAMLObject):
    """A basis for a Wildland container."""

    def __init__ (self, wlm_actor_admin=None, content_urls=[], paths=[]):

        # uuid is ephemeral and client isinstance-specific
        # We use it here mostly for easing visualization
        self.uuid = gen_uuid()
        self.original_wlm = None

        if wlm_actor_admin is None:
            self.id = self.uuid # TODO
            wlm_actor_admin = self
        self.wlm_actor_admin = wlm_actor_admin
        Logger.log (f"creating container: {self}, owned by {self.wlm_actor_admin}")

        g_wlgraph.add_node (self)
        g_wlgraph.add_edge (self, self.wlm_actor_admin, type=EdgeType.owned_by)

        self.paths = []
        for path in paths:
            self.add_path (path)

        self.content = []
        for content_url in content_urls:
            self.add_content (content_url)

        self.storage_manifests = []

    yaml_tag = u'!wlm'
    @classmethod
    def to_yaml(cls, dumper, wlm):
        dict_representation = {
            'uuid': wlm.uuid,
            'paths': wlm.paths,
            'content': wlm.content,
            'storage_manifests': repr(wlm.storage_manifests),
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

    def add_content (self, url):
        self.content.append (str(url))
        # TODO: consider implementing BackendURL class and call it from here?
        # This might be useful in some more recursive scenarios,
        # e.g. when URL will be of a form of `wildland:` :)
        # Right now we simulate the recursive scenario by explicitily
        # defining BackendStorageWildland.

        # FIXME:
        n = NameSpaceNode (url, url)
        g_wlgraph.add_edge (self, n, type=EdgeType.content)

    def add_storage_manifest (self, wlm_storage):
        if not isinstance (wlm_storage, WildlandStorageManifest):
            raise ValueError ("Need a WildlandStorageManifest object!")
        self.storage_manifests.append(wlm_storage)
        g_wlgraph.add_edge (self, wlm_storage, type=EdgeType.assigned)
        wlm_storage.update_admin (self.wlm_actor_admin)

    def add_storage_backend (self, storage_backend):
        if not isinstance (storage_backend, BackendStorage):
            raise ValueError ("Need a BackendStorage object!")

        wlm_manifest = WildlandStorageManifest (
                bknd_storage_backend=storage_backend)
        self.add_storage_manifest (wlm_manifest)

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

        Logger.log (f"creating new user: {paths[0]}, id = {self.id}")
        assert isinstance (wlm_storage_directory, WildlandStorageManifest)

        if wlm_storage_directory is None:
            raise ValueError ("WildlandUserManifest() must specify a storage manifest for its directory!")

        Logger.nest_up()
        WildlandManifest.__init__ (self, wlm_actor_admin=self, paths=paths)
        Logger.nest_down()
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

    def add_container (self, wlm_c):
        Logger.log (f"adding container {wlm_c} for user {self}")
        # Create a *new* container respresenting 'wlm_c':
        # Show we can rewrite wlm_c's paths as we like. See also comment
        # in add_uid_container() on this.
        # TODO: use some better naming convention here?
        self.wlm_new_c = WildlandManifest (wlm_actor_admin=self,
            paths = [f"/@guests/{wlm_c.wlm_actor_admin.id}{path}" for path in wlm_c.paths])    
        g_wlgraph.add_edge (self.wlm_new_c, wlm_c, type=EdgeType.refers)
        return self.wlm_new_c

    def add_uid_container (self, wlm_actor_c):
        Logger.log (f"adding user manifest container {wlm_actor_c.paths[0]} to user {self}")
        Logger.nest_up()
        self.wlm_new_c = self.add_container (wlm_actor_c)
        self.wlm_new_c.original_wlm = wlm_actor_c
        Logger.nest_down()

        # TODO: This is really very best-effort and hard-coded...
        # Just to show the dir owner can arbitrairly rewrite offered
        # container's paths. Which is cruciual, e.g. for building reputation
        # directories.
        uid = f"{wlm_actor_c.paths[0].rsplit('/',1).pop()}"
        self.wlm_new_c.add_path(f"/wildland/uids/community/{uid}")
        self.wlm_new_c.id = wlm_actor_c.id
        g_wlgraph.add_edge (self.wlm_new_c, wlm_actor_c, type=EdgeType.refers)

class WildlandStorageManifest (WildlandManifest):
    """A manifest assigned to a container, which tells where it is to be stored.
    """

    def __init__ (self, bknd_storage_backend):
        assert isinstance(bknd_storage_backend, BackendStorage)
        Logger.nest_up()
        WildlandManifest.__init__ (self)
        Logger.nest_down()
        self.bknd_storage_backend = bknd_storage_backend
        Logger.log (f"adding storage manifest ({self}):")
        Logger.nest_up()
        Logger.log (f"backed on {bknd_storage_backend}")
        g_wlgraph.add_node (self)
        g_wlgraph.add_edge (self, self.bknd_storage_backend,
                            type=EdgeType.points)
        Logger.nest_down()
    yaml_tag = u'!wlm_storage'
    @classmethod
    def to_yaml(cls, dumper, wlm):
        dict_representation = {
            'uuid': wlm.uuid,
            'paths': [],
            'backend' : repr (wlm.bknd_storage_backend)
        }
        node = dumper.represent_mapping(u'!wlm_storage', dict_representation)
        return node

    def __repr__ (self):
        return f"wlm_storage_{self.uuid:.8}"
