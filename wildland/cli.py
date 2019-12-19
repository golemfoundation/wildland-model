
from wildland.core import WildlandManifest, \
    WildlandUserManifest, \
    WildlandStorageManifest
from . logger import Logger
from . reporting import dump_yaml_for_node
from . resolve import wl_resolve_single, wl_resolve_recursively
from . content import *
import os
from blessings import Terminal

class WildlandClient:
    """An instance of a Wildland client."""

    def __init__(self, wlm_actor_me, wlm_actor_default_dir):
        self.me = wlm_actor_me
        self.dir = wlm_actor_default_dir
        self.containers = []
        self.logger = Logger (name=self, color=Terminal().magenta)
        self.logger.log (f"New client instance for {self.me}, default dir: {self.dir}")
    
    def __repr__ (self):
        return f"cli_{self.me.id:.8}"
    
    def set_default_directory (self, wlm_actor_default_dir):
        self.logger.log (f"Updating default dir to: {self.dir}")
        self.dir = wlm_actor_default_dir
    
    def map_container (self, wlm_c):
        self.containers.append (wlm_c)
        
    def create_rel_symlink (self, symlink, target):
        symlink = os.path.normpath(symlink)
        target  = os.path.normpath(target)
        symlink_parent_dir, symlink_base = os.path.split (symlink)
        target_rel = os.path.relpath(target, start=symlink_parent_dir)
        
        try:
            os.makedirs (symlink_parent_dir)
            os.makedirs (target)
        except FileExistsError:
            pass
            
        os.symlink (src=target_rel, dst=symlink)

    def create_container_content (self, container_path, wlm, delegated=False):
        for content in wlm.content:
            if isinstance (content, ContainerContentFile):
                f = open (f"{container_path}/"
                          f"{'@' if delegated else ''}"
                          f"{content.path}", 'w')
                f.close()
            elif isinstance (content, ContainerContentWLC):
                self.create_container_content (
                    container_path=container_path,
                    wlm=content.wlm,
                    delegated=True)
            else:
                raise AssertionError        
        
        
    def create_forest (self, basedir):
        basedir = os.path.normpath (basedir)

        for c in self.containers:
            owner = c.id if isinstance (c, WildlandUserManifest) \
                else c.wlm_actor_admin.id
            owner_forest_dir = f"{basedir}/{owner}/"
            container_path = f"{owner_forest_dir}/.uuid/{c.uuid:.8}"
            
            os.makedirs (container_path)
            
            # if isinstance (c, WildlandUserManifest):
            #     # Create special metafiles for user manifest containers:
            #     self.create_rel_symlink (
            #         symlink=f"{container_path}/root",
            #         target=f"../.."
            #     )
            
            # TODO: replce with proper content object
            dump_yaml_for_node (
                f"{container_path}/.wlmanifest.yaml", c)

            # Dump storage manifests assigned to this container:
            os.makedirs (f"{container_path}/.wlinfra/")
            for wlm_storage in c.storage_manifests:
                dump_yaml_for_node (
                    f"{container_path}/.wlinfra/{wlm_storage}.yaml",
                    wlm_storage)
            
            self.create_container_content (
                container_path=container_path,
                wlm=c)

            for p in c.paths:
                self.create_rel_symlink (
                    symlink=f"{owner_forest_dir}/{p.lstrip('/')}",
                    target=container_path
                )

        self.create_rel_symlink (
            symlink=f"{basedir}/@me",
            target=f"{basedir}/{self.me.id}"
        )

        self.create_rel_symlink (
            symlink=f"{basedir}/@default",
            target=f"{basedir}/{self.dir.id}"
        )
        
    def resolve (self, path):
        return wl_resolve_recursively (self.dir, path, logger=self.logger)

    def fetch (self, wlm_c):
        wlm_storages = wlm_c.get_storage_manifests ()
        self.logger.log (f"fetch_container: {wlm_c}, requesting from all backends:")
        for s in wlm_storages:
            # TODO: properly encode path
            s.request_content (wlm_c.paths[0])

    def clone (self, wlm_remote_c, paths=[]):
        self.map_container (wlm_remote_c)
        if len(paths) == 0:
            paths = [f"/cloned/{wlm_remote_c.wlm_actor_admin.id}/{p}" for p in wlm_remote_c.paths]
            
        wlm_cloned_c = WildlandManifest (
            wlm_actor_admin=self.me,
            paths=paths,
            content= [
                ContainerContentWLC (
                    path="", # map remote WLC to root dir of this container
                    wlm=wlm_remote_c,
                    wl_address=f"@me:{wlm_remote_c.wlm_actor_admin}/"
                               f"{wlm_remote_c.paths[0]}" # use any path
                )]
            )
        
        self.map_container (wlm_cloned_c)
        return wlm_cloned_c
