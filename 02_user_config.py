#!/usr/bin/python3

from bootstrap import wl_barebones_init
from storage import BackendStorage, BackendStorageWildland
from core import WildlandManifest, WildlandUserManifest, WildlandStorageManifest
from reporting import dump_state, prep_output_dir
from bootstrap_golem import golem_foundation_init, golem_foundation_dir_submit_key, golem_foundation_dir_key
from resolve import wl_resolve, wl_set_default_directory, wl_resolve_recursively, fetch_container

# User-specific config, building on Golem Foundation default infrastructure
prep_output_dir()
golem_foundation_init()

storage_ipfs = BackendStorage('ipfs', friendly_name="IPFS")
storage_mynas = BackendStorage('webdav', friendly_name="My NAS")
mailbox_work = BackendStorage('imap', friendly_name="joanna@golem.foundation")
mailbox_personal = BackendStorage('imap', friendly_name="joasia@example.com")
storage_mys3 = BackendStorage('s3', friendly_name="joanna's s3 bucket")

# Create new user:

# 1. Create a storage manifest object which will tell where the directory of the
# user is located:

wlm_storage_joanna = WildlandStorageManifest(
    bknd_storage_backend = storage_mynas
)

# 2. Create a user manifest, provide names for this manifest, refer to the
# storage manifest we created in the previous step:

wlm_actor_joanna = WildlandUserManifest (
    wlm_storage_directory = wlm_storage_joanna,
    paths = ["/uids/j@g.f",
             "/uids/j@q-os.org",
             "/uids/j@i.org"])


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
    c.add_storage_backend (storage_ipfs)
    c.add_storage_backend (storage_mynas)
    c.add_storage_backend (storage_mys3)

wl_set_default_directory (wlm_actor_joanna)
dump_state()
wl_resolve ("/uids/j@i.org:/photos/nature/Tatry")

# Add another User

wlm_storage_andrzej = WildlandStorageManifest(
    bknd_storage_backend = storage_ipfs
)

wlm_actor_andrzej = WildlandUserManifest (
    wlm_storage_directory = wlm_storage_andrzej,
    paths = ["/uids/andrzej@g.f"])



wl_set_default_directory (golem_foundation_dir_key())
dump_state()
c = wl_resolve("/wildland/uids/community/j@g.f:/photos/nature/Tatry")
fetch_container (c)

# exit(0)
# Turtles all the way down!

wlm_turtles = WildlandManifest (wlm_actor_joanna,
    content_urls = [""],
    paths = ["/turtles"])


wlm_turtles.add_storage_backend (storage_mynas)

storage_turtles = BackendStorageWildland (wlm_actor_joanna,
    "/uids/j@g.f:/turtles")
dump_state()

wlm_achilles = WildlandManifest (wlm_actor_joanna,
    content_urls = ["file://"],
    paths = ["/reading/math/GEB"])

wlm_achilles.add_storage_backend (storage_turtles)
dump_state()

# Watch out for loops ahead!
wlm_turtles.add_storage_backend (storage_turtles)
dump_state()
