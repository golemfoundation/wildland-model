#!/usr/bin/python3

from bootstrap import wl_barebones_init
from storage import BackendStorage, BackendStorageWildland
from core import WildlandManifest, WildlandUserManifest, WildlandStorageManifest
from reporting import dump_state, prep_output_dir

# Alternative user config, ignoring Golem Foundation infrastructure
prep_output_dir()
wl_barebones_init()

local_storage = BackendStorage('local', friendly_name="host")
storage_ipfs = BackendStorage('ipfs', friendly_name="IPFS")
storage_mynas = BackendStorage('webdav', friendly_name="My NAS")
mailbox_work = BackendStorage('imap', friendly_name="joanna@golem.foundation")
mailbox_personal = BackendStorage('imap', friendly_name="joasia@example.com")
storage_mynas = BackendStorage('webdav', friendly_name="My NAS")

wlm_storage_joanna = WildlandStorageManifest(
    bknd_storage_backend = storage_mynas
)

wlm_actor_joanna = WildlandUserManifest (
    wlm_storage_directory = wlm_storage_joanna,
    paths = ["/uids/j@g.f",
             "/uids/j@q-os.org",
             "/uids/j@i.org"])
dump_state()
