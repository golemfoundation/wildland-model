#!/usr/bin/python3

from wildland.core import WildlandManifest, \
                          WildlandUserManifest, \
                          WildlandStorageManifest
from wildland.storage import BackendStorage
from wildland.reporting import prep_output_dir, dump_state
from wildland.cli import WildlandClient
from wildland.content import *

from bootstrap_golem import golem_foundation_init, \
    golem_foundation_dir_submit_key, \
    golem_foundation_dir_key

# User-specific config, building on Golem Foundation default infrastructure
prep_output_dir()
golem_foundation_init()

storage_ipfs = BackendStorage('ipfs', friendly_name="IPFS")
storage_mynas = BackendStorage('webdav', friendly_name="Ijon's NAS")
storage_mys3 = BackendStorage('s3', friendly_name="Tichy's s3 bucket")

# Create new user:

# 1. Create a storage manifest object which will tell where the directory of the
# user is located:

wlm_storage_tichy = WildlandStorageManifest(
    bknd_storage_backend = storage_mynas
)

# 2. Create a user manifest, provide names for this manifest, refer to the
# storage manifest we created in the previous step:

wlm_actor_tichy = WildlandUserManifest (
    wlm_storage_directory = wlm_storage_tichy,
    paths = ["/users/names/Ijon Tichy",
             "/users/emails/ijon@lunar.extraction.module"])

# 3. Add another Tichy's key to the manifest
wlm_actor_tichy.add_pubkey('0x490ae7ff')

dump_state()

# Publish user manifest to the golem foundation directory
# so others can also discover/get access the contaibner

golem_foundation_dir_submit_key (wlm_actor_tichy)
dump_state()

# Add another User

wlm_storage_tarantoga = WildlandStorageManifest(
    bknd_storage_backend = storage_ipfs
)

wlm_actor_tarantoga = WildlandUserManifest (
    wlm_storage_directory = wlm_storage_tarantoga,
    paths = ["/users/names/Prof. Tarantoga"])
    
golem_foundation_dir_submit_key (wlm_actor_tarantoga)
dump_state()

# Create client instances representing view's of different actors:

wlm_actor_gf = golem_foundation_dir_key()

cli_tichy = WildlandClient (
    wlm_actor_me = wlm_actor_tichy,
    wlm_actor_default_dir = wlm_actor_tichy)

cli_tichy.map_container (wlm_actor_tichy)
cli_tichy.map_container (wlm_actor_gf)

cli_tarantoga = WildlandClient (
    wlm_actor_me = wlm_actor_tarantoga,
    wlm_actor_default_dir = wlm_actor_gf)

cli_tarantoga.map_container (wlm_actor_tarantoga)
cli_tarantoga.map_container (wlm_actor_gf)

all_clients = [cli_tichy, cli_tarantoga]
dump_state(clients=all_clients)

# Lets now add some containers...

some_containers = [
    WildlandManifest(wlm_actor_tichy,
        content = [
            ContainerContentFile(f"IMG{i:03}.jpeg") for i in range (1,10)
            ],
        paths = [
            "/photos/nature/animals/kurdle",
            "/trips/14th/kurdle",
            "/plantes/Entropy/photos/kurdle"
            ]),
    WildlandManifest(wlm_actor_tichy,
        content = [
            ContainerContentFile("journal-mon.md"),
            ContainerContentFile("journal-tue.md"),
            ContainerContentFile("timelapse01.mov")
            ],
        paths = [
            "/trips/7th/journal",
            "/journal/trip7th",
            "/topics/physics/time/trip7th"
            ])
        ]

dump_state()

# Assign storage infrastructure for containers:
for c in some_containers:
    cli_tichy.map_container (c)
    # When we have economy we could do just:
    # c.find_storeage(available_storge_backends)
    c.add_storage_manifest (WildlandStorageManifest(storage_ipfs))
    c.add_storage_manifest (
        WildlandStorageManifest(storage_mynas,
                                [f'webdav://mynas.mydomain.org/{repr(c)}-storage.yaml',
                                 f'wildland://{c.wlm_actor_admin.id}:/storage-manifests/{repr(c)}.yaml']))
    c.add_storage_manifest (WildlandStorageManifest(storage_mys3))
dump_state(clients=all_clients)

cli_tichy.map_container (wlm_actor_tarantoga)
dump_state(clients=all_clients)
cli_tichy.resolve ("/users/names/Ijon Tichy:/trips/14th/kurdle")
dump_state(clients=all_clients)

cli_tichy.set_default_directory(golem_foundation_dir_key())
c = cli_tichy.resolve(
    "/wildland/community/users/Ijon Tichy:"\
    "/trips/14th/kurdle")
cli_tichy.fetch (c)

# Clone a container from another user and map into own namespace:
cli_tarantoga.set_default_directory(golem_foundation_dir_key())
wlm_ijons_stuff = cli_tarantoga.resolve(
                "/wildland/community/users/Ijon Tichy:/trips/14th/kurdle")
cli_tarantoga.clone (wlm_ijons_stuff, paths=["/tichy's trips/kurdle"])
dump_state(clients=all_clients)
