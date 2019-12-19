import yaml

class ContainerContentItem(yaml.YAMLObject):
    """Represents a single generic item within a WL container"""

    def __init__(self, path):
        path = path.lstrip('/')
        self.path = path    # path & name, realtive to the container root dir

    yaml_tag = u'!content'
    @classmethod
    def to_yaml(cls, dumper, c):
        dict_representation = {
            'path': c.path,
            'type': '?',
        }
        node = dumper.represent_mapping(u'!content', dict_representation)
        return node

class ContainerContentFile(ContainerContentItem):
    """A static file within a WL container"""
    
    def __init__(self, path):
        super().__init__(path=path)
    
    def __repr__(self):
        return f"content_file_"\
               f"{self.path.strip('/').replace('/','_').replace(' ','_')}"

    yaml_tag = u'!content_file'
    @classmethod
    def to_yaml(cls, dumper, c):
        dict_representation = {
            'path': c.path,
            'type': 'file',
        }
        node = dumper.represent_mapping(u'!content_file', dict_representation)
        return node


class ContainerContentWLC(ContainerContentItem):
    """A a WL container as content within a container
        
        For delegated containers, path could be "", which means
        to map all the root dir of the delegated container onto the
        root dir of the current container. Having more than one such item might give undesireable results, clients software should avoid this.
    """
    
    def __init__(self, path, wl_address):
        self.path = path
        self.wl_address = wl_address
        super().__init__(path=path)

    def __repr__(self):
        return f"content_wlc_{strip('/').replace('/','_').replace(' ','_')}->"\
               f"{self.wl_address}"

    yaml_tag = u'!content_wlm'
    @classmethod
    def to_yaml(cls, dumper, c):
        dict_representation = {
            'path': c.path,
            'type': 'wlmanifest',
            'wl_address': c.wl_address
        }
        node = dumper.represent_mapping(u'!content_wlm', dict_representation)
        return node

class ContainerContentDynamic(ContainerContentItem):
    pass
