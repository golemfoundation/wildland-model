#!/usr/bin/python3

from wildland.core import WildlandManifest, \
    WildlandUserManifest, \
    WildlandStorageManifest
from wildland.storage import BackendStorage
from wildland.reporting import prep_output_dir, dump_state
from bootstrap_bare import wl_barebones_init
from wildland.globals import g_wlgraph
from wildland.logger import Logger
from wildland.edge_types import EdgeType

# Golem Foundation reference config for bootstraping

def golem_foundation_init():
    wl_barebones_init()

    bknd_storage_golem = [
        BackendStorage('s3', friendly_name="golem-aws-eu"),
        BackendStorage('s3', friendly_name="golem-aws-us")
        ]

    wlm_storage_golem = WildlandStorageManifest(
        bknd_storage_backend = bknd_storage_golem[0]
    )

    global wlm_actor_golem_dir
    wlm_actor_golem_dir = WildlandUserManifest (
        wlm_storage_directory = wlm_storage_golem,
        paths = [
            "/wildland/uids/golem.foundation",
            "/wildland/dns/golem.foundation"
            ])


def golem_foundation_dir_submit_key (wlm_actor):
    gf_logger = Logger (name="golem.foundation", color=Logger.t.magenta)
    gf_logger.log (f"adding {wlm_actor.id} to Golem Foundation Directory")

    # Here would be a call to some code for verification
    # of the user-declared names/paths, follwed by
    # rewriting to canonical form according to some policy
    # defined by the directory (this is really just a demo):
    uid = f"{wlm_actor.paths[0].rsplit('/',1).pop()}"

    # Create new container to represent original actor:
    wlm_new_c = WildlandManifest (
        wlm_actor_admin=wlm_actor_golem_dir,
        paths=[f"/wildland/community/users/{uid}"])
     
    wlm_new_c.add_storage_manifest (wlm_actor_golem_dir.storage_manifests[0])
    
    wlm_new_c.original_storage_manifests = wlm_actor.get_storage_manifests()
    
    # Cruciually, make this new container really represent the submited one:
    wlm_new_c.id = wlm_actor.id
    wlm_new_c.store_manifest()
    
    g_wlgraph.add_edge (wlm_new_c, wlm_actor, type=EdgeType.refers)


def golem_foundation_dir_key ():
    return wlm_actor_golem_dir

if __name__ == "__main__":
    prep_output_dir()
    golem_foundation_init()
    dump_state()
