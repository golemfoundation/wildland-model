from globals import *
from logger import Logger
import uuid

def gen_uuid():
    # Truncate for better presentation clarity
    return str(uuid.uuid4())[1:8]

def verify_path (path):
    if path[0] != '/':
        raise ValueError ("A path should start with a leading slash!")

def split_path_into_tokens (path):
    return path.lstrip('/').rstrip('/').split('/')

def split_addr_into_actor_and_path (addr):
    # Fully qualified address in WL has a form:
    # <actor.id>:<path>
    return addr.rsplit (':',1)

def wl_resolve (wlm_actor, path):
    """Find container within The Wildland NameSpace."""

    verify_path(path)

    Logger.log (f"resolving: {wlm_actor.id}:{path}")

    full_path = f"{wlm_actor.id}{path}"
    path_as_list = split_path_into_tokens(full_path)

    # Traverse the NameSpace graph along the 'path', starting from '@namespace':
    Logger.nest_up()
    prev_node = '@namespace'
    for token in path_as_list:
        next_node = None
        for node in g_wlgraph.successors(prev_node):
            if node.name == token:
                next_node = node
                break
        if next_node is None:
            raise LookupError
        prev_node = node

    Logger.nest_down()
    containers = g_wlgraph.successors(prev_node)
    Logger.log (f"-> found {len(containers)} container(s):"
            f" - {[c.uuid for c in containers]}")
    return containers[0]

def wl_resolve_recursively (wlm_actor_root, path):
    Logger.log (f"resolving full path: {path}")
    pubkey_token,path_token = split_addr_into_actor_and_path (path)

    wlm_actor = None
    Logger.nest_up()
    if len(split_addr_into_actor_and_path (pubkey_token)) > 1:
        # the pubkey part still in the x:y form
        wlm_actor = wl_resolve_recursively (wlm_actor_root, pubkey_token)
    else:
        wlm_actor = wl_resolve (wlm_actor_root, pubkey_token)
    Logger.nest_down()

    Logger.log (f"-> resolved direct actor = {wlm_actor.id}")
    return wl_resolve (wlm_actor, path_token)

def wl_resolve_full_path (full_path):
    pubkey_token, path = full_path.split(':',1)
    wlm_actor_root = golem_directory # TODO
    return wl_resolve_recursively (wlm_actor_root, path)
