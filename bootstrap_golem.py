from globals import *
from bootstrap import wl_barebones_init
from core import WildlandManifest, WildlandUserManifest, WildlandStorageManifest
from storage import BackendStorage, BackendStorageWildland, StorageDriver
from logger import Logger
from reporting import dump_state

# Golem Foundation reference config for bootstraping

def golem_foundation_init():
    wl_barebones_init()
    dump_state()

    bknd_storage_golem = [
        BackendStorage('s3', friendly_name="golem-aws-eu"),
        BackendStorage('s3', friendly_name="golem-aws-us")
        ]

    dump_state()

    wlm_storage_golem = WildlandStorageManifest(
        bknd_storage_backend = bknd_storage_golem[0],
        wlm_parent = WildlandManifest()
    )
    dump_state()
    global wlm_actor_golem_dir
    wlm_actor_golem_dir = WildlandUserManifest (
        wlm_storage_directory = wlm_storage_golem,
        paths = [
            "/wildland/uids/golem.foundation",
            "/wildland/dns/golem.foundation"
            ])
    g_wlgraph.add_edge ('@default_user', wlm_actor_golem_dir)
    dump_state()

    wlm_storage_golem.update_parent (wlm_actor_golem_dir)
    dump_state()


def golem_foundation_dir_submit_key (wlm_actor_key):
    wlm_actor_golem_dir.add_uid_container (wlm_actor_key)

def golem_foundation_dir_key ():
    return wlm_actor_golem_dir
