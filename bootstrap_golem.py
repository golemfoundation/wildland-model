#!/usr/bin/python3

from wildland.core import \
    WildlandUserManifest, \
    WildlandStorageManifest
from wildland.storage import BackendStorage
from wildland.reporting import prep_output_dir, dump_state
from bootstrap_bare import wl_barebones_init

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


def golem_foundation_dir_submit_key (wlm_actor_key):
    wlm_actor_golem_dir.add_uid_container (wlm_actor_key)

def golem_foundation_dir_key ():
    return wlm_actor_golem_dir

if __name__ == "__main__":
    prep_output_dir()
    golem_foundation_init()
    dump_state()
