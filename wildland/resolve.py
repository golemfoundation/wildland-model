from . globals import *
from . logger import Logger


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

    g_logger.log (f"wl_resolve_single: {wlm_actor.id}:{path}")
    verify_path(path)
    full_path = f"{wlm_actor.id}{path}"

    bknd = wlm_actor.get_backends()[0] # TODO: support more
    return bknd.request_resolve (full_path)

def wl_resolve_recursively (wlm_actor_root, path):
    g_logger.log (f"resolving full path: {path}", icon='r')
    g_logger.nest_up()
    pubkey_token,path_token = split_addr_into_actor_and_path (path)
    # g_logger.log (f"--> pubkey_token: {pubkey_token}, path_token: {path_token}")
    wlm_actor = None

    if len(split_addr_into_actor_and_path (pubkey_token)) > 1:
        # the pubkey part still in the x:y form
        wlm_actor = wl_resolve_recursively (wlm_actor_root, pubkey_token)
    else:
        wlm_actor = wl_resolve_single (wlm_actor_root, pubkey_token)
    

    g_logger.log (f"resolved direct actor = {wlm_actor}")
    ret = wl_resolve_single (wlm_actor, path_token)
    g_logger.nest_down()
    g_logger.log (f"resolved: {path} -> {ret}")
    return ret

def wl_set_default_directory(wlm_new_default_directory):
    g_logger.log (f"setting default directory to:"
        f" {wlm_new_default_directory}"
        f" (path[0]={wlm_new_default_directory.paths[0]})")
    global wlm_default_directory
    wlm_default_directory = wlm_new_default_directory
    if '@default_directory' in g_wlgraph.node:
        # g_logger.log ("--> node '@default_directory' found, removing")
        g_wlgraph.remove_node('@default_directory')
    g_wlgraph.add_edge ('@default_directory', wlm_default_directory)

def wl_resolve (path):
    if wlm_default_directory is None:
        raise AssertionError (
            "No default user set, use wl_set_default_directory() first")

    return wl_resolve_recursively (wlm_default_directory, path)
    
def fetch_container (wlm_c):
    bknds = wlm_c.get_backends ()
    g_logger.log (f"fetch_container: {wlm_c}, sending requests to all backends:")
    for b in bknds:
        # this is just for illustration
        b.request_raw_data (f"hash({wlm_c.paths[0]}).zip")
