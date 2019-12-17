from blessings import Terminal

def colorize_wl_path (path):
    return f"{Terminal().blue}{path}{Terminal().normal}"

def verify_path (path):
    if path[0] != '/':
        raise ValueError ("A path should start with a leading slash!")

def split_path_into_tokens (path):
    return path.lstrip('/').rstrip('/').split('/')

def split_addr_into_actor_and_path (addr):
    # Fully qualified address in WL has a form:
    # <actor.id>:<path>
    return addr.rsplit (':',1)

def wl_resolve_single (wlm_actor, path, logger = None):
    """Find container within The Wildland NameSpace."""
    if logger:
        logger.log (f"wl_resolve_single: "
                f"{wlm_actor}:"
                f"{colorize_wl_path(path)}", icon='.')
    verify_path(path)
    wlm_storage = None
    if wlm_actor.original_storage_manifests is not None:
        wlm_storage = wlm_actor.original_storage_manifests[0]
        if logger:
            logger.log (f"- using original storage manifest: {wlm_storage}")
    else:
        wlm_storage = wlm_actor.get_storage_manifests()[0] # TODO: support more
    return wlm_storage.request_manifest (path)

def wl_resolve_recursively (wlm_actor_root, path, logger = None):
    if logger:
        logger.log (f"resolving path: {colorize_wl_path(path)}", icon='r')
        logger.log (f"`-> using dir: {colorize_wl_path(wlm_actor_root)}", icon='.')
    pubkey_token,path_token = split_addr_into_actor_and_path (path)
    wlm_actor = None

    if len(split_addr_into_actor_and_path (pubkey_token)) > 1:
        # the pubkey part still in the x:y form
        wlm_actor = wl_resolve_recursively (wlm_actor_root, pubkey_token, logger)
    else:
        wlm_actor = wl_resolve_single (wlm_actor_root, pubkey_token, logger)
    if logger:
        logger.log (f"`-> resolved direct actor: {colorize_wl_path(wlm_actor)}", icon='.')
    ret = wl_resolve_single (wlm_actor, path_token)
    if logger:
        logger.log (f"`-> resolved: {colorize_wl_path(path)}"\
                    f" -> {ret}", icon='R')
    return ret
