#!/usr/bin/python3

from wildland.core import \
    WildlandUserManifest, \
    WildlandStorageManifest
from wildland.storage import BackendStorage
from wildland.reporting import prep_output_dir, dump_state
from bootstrap_bare import wl_barebones_init

# Alternative user config, ignoring Golem Foundation infrastructure

def altuser_init():
    wl_barebones_init()

    storage_ipfs = BackendStorage('ipfs', friendly_name="IPFS")

    wlm_storage_altuser = WildlandStorageManifest(
        bknd_storage_backend = storage_ipfs
    )

    wlm_actor_altuser = WildlandUserManifest (
        wlm_storage_directory = wlm_storage_altuser,
        paths = ["/tichy"])

if __name__ == "__main__":
    prep_output_dir()
    altuser_init()
    dump_state()
