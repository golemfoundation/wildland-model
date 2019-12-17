
from wildland.core import WildlandManifest, \
    WildlandUserManifest, \
    WildlandStorageManifest
from . logger import Logger
from . reporting import dump_yaml_for_node
import os

class WildlandClient:
    """An instance of a Wildland client."""

    def __init__(self, wlm_actor_me, wlm_actor_default_dir):
        self.me = wlm_actor_me
        self.dir = wlm_actor_default_dir
        self.containers = []
        self.logger = Logger (name=wlm_actor_me.id)
    
    def __repr__ (self):
        return f"cli_{self.me.id:.8}"
    
    def map_container (self, wlm_c):
        self.containers.append (wlm_c)
        
    def create_rel_symlink (self, basedir, symlink, target):
        basedir = os.path.normpath(basedir)
        symlink = os.path.normpath(symlink)
        target  = os.path.normpath(target)
        symlink_full = f"{basedir}/{symlink}"
        target_full = f"{basedir}/{target}"
        symlink_parent_dir, symlink_base = os.path.split (symlink_full)
        target_rel = os.path.relpath(target_full, start=symlink_parent_dir)
        
        ret = False
        if not os.path.exists (target_full):
            ret = True
        try:
            os.makedirs (symlink_parent_dir)
            os.makedirs (target_full)
        except FileExistsError:
            pass

        os.symlink (src=target_rel, dst=symlink_full)
        return ret # True if this was 1st call for this container
        
    def dump (self, basedir):
        basedir = os.path.normpath (basedir)
        self.logger.log (f"Forest created in {basedir}")
        for c in self.containers:
            
            owner = None
            if isinstance (c, WildlandUserManifest):
                owner = c.id
                container_path = f"{owner}/.uuid/{c.uuid:.8}"
                self.create_rel_symlink (
                    basedir=basedir,
                    symlink=f"{container_path}/root",
                    target=f"{owner}/"
                )
                dump_yaml_for_node (
                    f"{basedir}/{container_path}/manifest.yaml", c)
            else:
                owner = c.wlm_actor_admin.id

            for p in c.paths:
                self.create_rel_symlink (
                    basedir=f"{basedir}/{owner}",
                    symlink=f"{p.lstrip('/')}",
                    target=f".uuid/{c.uuid:.8}/"
                )
        
        self.create_rel_symlink (
            basedir=basedir,
            symlink="@me",
            target=f"{self.me.id}"
        )

        self.create_rel_symlink (
            basedir=basedir,
            symlink="@default",
            target=f"{self.dir.id}"
        )
        
