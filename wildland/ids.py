import uuid

def gen_uuid():
    # Note: UUIDs are epheral! i.e. they make sense only for a particular
    # instance of a client. They are _not_ guaranteed to be globally-unique!
    return str(uuid.uuid4())
