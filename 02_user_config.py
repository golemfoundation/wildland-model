#!/usr/bin/python3

from bootstrap import wl_barebones_init
from storage import BackendStorage, BackendStorageWildland
from core import WildlandManifest, WildlandUserManifest, WildlandStorageManifest
from reporting import dump_state, prep_output_dir
from bootstrap_golem import golem_foundation_init, golem_foundation_dir_submit_key, golem_foundation_dir_key
from utils import wl_resolve_recursively

# User-specific config, building on Golem Foundation default infrastructure
prep_output_dir()
golem_foundation_init()

storage_ipfs = BackendStorage('ipfs', friendly_name="IPFS")
storage_mynas = BackendStorage('webdav', friendly_name="My NAS")
mailbox_work = BackendStorage('imap', friendly_name="joanna@golem.foundation")
mailbox_personal = BackendStorage('imap', friendly_name="joasia@example.com")

wlm_storage_joanna = WildlandStorageManifest(
    bknd_storage_backend = storage_mynas,
    wlm_parent = WildlandManifest()
)

wlm_actor_joanna = WildlandUserManifest (
    wlm_storage_directory = wlm_storage_joanna,
    paths = ["/uids/j@g.f",
             "/uids/j@q-os.org",
             "/uids/j@i.org"])

wlm_storage_joanna.update_parent (wlm_actor_joanna)

dump_state()

# Publish user manifest to the golem foundation directory
# so others can also discover/get access the contaibner

golem_foundation_dir_submit_key (wlm_actor_joanna)
dump_state()

# Lets now add some containers...

some_containers = [
    WildlandManifest(wlm_actor_joanna,
        content_urls = ["file://~/Photos/Tatry/"],
        paths = [
            "/photos/nature/Tatry",
            "/time/2019/03"
            ]),
    WildlandManifest(wlm_actor_joanna,
        content_urls = ["file://~/Photos/Żagle/"],
        paths = [
            "/photos/nature/Mazury",
            "/time/2019/08"
            ])
        ]

dump_state()

for c in some_containers:
    c.add_storage_manifest (storage_ipfs)
    c.add_storage_manifest (storage_mynas)

dump_state()

wl_resolve_recursively (wlm_actor_joanna, "/uids/j@i.org:/photos/nature/Tatry")
# Turtles all the way down!

wlm_turtles = WildlandManifest (wlm_actor_joanna,
    content_urls = [""],
    paths = ["/turtles"])


wlm_turtles.add_storage_manifest (storage_mynas)

storage_turtles = BackendStorageWildland (wlm_actor_joanna,
    "/uids/j@g.f:/turtles")

wlm_achilles = WildlandManifest (wlm_actor_joanna,
    content_urls = ["file://"],
    paths = ["/reading/math/GEB"])

wlm_achilles.add_storage_manifest (storage_turtles)
dump_state()

# Watch out for loops ahead!
wlm_turtles.add_storage_manifest (storage_turtles)
dump_state()
