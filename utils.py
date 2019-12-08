from globals import *
from logger import Logger


def verify_path (path):
    if path[0] != '/':
        raise ValueError ("A path should start with a leading slash!")

def split_path_into_tokens (path):
    return path.lstrip('/').rstrip('/').split('/')

def split_addr_into_actor_and_path (addr):
    # Fully qualified address in WL has a form:
    # <actor.id>:<path>
    return addr.rsplit (':',1)

def wl_resolve_single (wlm_actor, path):
    """Find container within The Wildland NameSpace."""

    Logger.log (f"wl_resolve_single: {wlm_actor.id}:{path}")
    Logger.nest_up()
    verify_path(path)
    full_path = f"{wlm_actor.id}{path}"
    path_as_list = split_path_into_tokens(full_path)

    # Traverse the NameSpace graph along the 'path', starting from '@namespace':
    Logger.nest_up()
    Logger.log (f"traversing the NameSpace tree: ")
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
        Logger.log (f"{node.name}")
        prev_node = node
    Logger.nest_down()
    Logger.nest_down()
    containers = g_wlgraph.successors(prev_node)
    Logger.log (f"found {len(containers)} container(s):"
            f" - {[c for c in containers]}")
    container = containers[0] # TODO: support more
    Logger.log (f"using 1st from the list: {container}")
    if container.original_wlm is not None:
        Logger.log (f"using the original container: {container.original_wlm}")
        container = container.original_wlm
    wlm_storage = container.storage_manifests[0] # TODO: support more
    bknd = wlm_storage.bknd_storage_backend
    Logger.log (f"backend: {bknd}")
    Logger.log (f"requesting: hash({path}/wildland.yaml) from {bknd}")
    Logger.nest_down()
    return container

def wl_resolve_recursively (wlm_actor_root, path):
    Logger.log (f"resolving full path: {path}", icon='R')
    Logger.nest_up()
    pubkey_token,path_token = split_addr_into_actor_and_path (path)
    # Logger.log (f"--> pubkey_token: {pubkey_token}, path_token: {path_token}")
    wlm_actor = None

    if len(split_addr_into_actor_and_path (pubkey_token)) > 1:
        # the pubkey part still in the x:y form
        wlm_actor = wl_resolve_recursively (wlm_actor_root, pubkey_token)
    else:
        wlm_actor = wl_resolve_single (wlm_actor_root, pubkey_token)
    

    Logger.log (f"resolved direct actor = {wlm_actor}")
    ret = wl_resolve_single (wlm_actor, path_token)
    Logger.nest_down()
    Logger.log (f"resolved: {path} -> {ret}")
    return ret

def wl_set_default_directory(wlm_new_default_directory):
    Logger.log (f"setting default directory to:"
        f" {wlm_new_default_directory}"
        f" (path[0]={wlm_new_default_directory.paths[0]})")
    global wlm_default_directory
    wlm_default_directory = wlm_new_default_directory
    if '@default_directory' in g_wlgraph.node:
        # Logger.log ("--> node '@default_directory' found, removing")
        g_wlgraph.remove_node('@default_directory')
    g_wlgraph.add_edge ('@default_directory', wlm_default_directory)

def wl_resolve (path):
    if wlm_default_directory is None:
        raise AssertionError (
            "No default user set, use wl_set_default_directory() first")

    return wl_resolve_recursively (wlm_default_directory, path)
