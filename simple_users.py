#!/usr/bin/python3

from wildland.core import WildlandManifest, \
    WildlandUserManifest, \
    WildlandStorageManifest
from wildland.storage import BackendStorage
from wildland.reporting import prep_output_dir, dump_state

from wildland.resolve import wl_resolve, \
    wl_set_default_directory, \
    fetch_container

from bootstrap_golem import golem_foundation_init, \
    golem_foundation_dir_submit_key, \
    golem_foundation_dir_key


# User-specific config, building on Golem Foundation default infrastructure
prep_output_dir()
golem_foundation_init()

def simple_users_setup():

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

    dump_state()

    # Publish user manifest to the golem foundation directory
    # so others can also discover/get access the contaibner

    golem_foundation_dir_submit_key (wlm_actor_tichy)
    wl_set_default_directory (wlm_actor_tichy)
    dump_state()

    # Lets now add some containers...

    some_containers = [
        WildlandManifest(wlm_actor_tichy,
            content_urls = ["file://~/Photos/2123-12-01/"],
            paths = [
                "/photos/nature/animals/kurdle",
                "/trips/14th/kurdle",
                "/plantes/Entropy/photos/kurdle"
                ]),
        WildlandManifest(wlm_actor_tichy,
            content_urls = ["file://~/Journal/TimeLapses/"],
            paths = [
                "/trips/7th/journal",
                "/journal/trip7th",
                "/topics/physics/time/trip7th"
                ])
            ]

    dump_state()

    for c in some_containers:
        c.add_storage_backend (storage_ipfs)
        c.add_storage_backend (storage_mynas)
        c.add_storage_backend (storage_mys3)

    # Add another User

    wlm_storage_tarantoga = WildlandStorageManifest(
        bknd_storage_backend = storage_ipfs
    )

    wlm_actor_tarantoga = WildlandUserManifest (
        wlm_storage_directory = wlm_storage_tarantoga,
        paths = ["/users/names/Prof. Tarantoga"])

    dump_state()


simple_users_setup()
dump_state()

wl_resolve ("/users/names/Ijon Tichy:/trips/14th/kurdle")

wl_set_default_directory (golem_foundation_dir_key())
dump_state()
c = wl_resolve(
    "/wildland/uids/community/Ijon Tichy:"\
    "/trips/14th/kurdle")
fetch_container (c)
