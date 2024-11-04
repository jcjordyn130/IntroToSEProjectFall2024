import copy

GenericOK = ({"status": "ok"}, 200)

def build(resp, data):
    if not isinstance(data, dict):
        raise ValueError("Data can only be a dict as it's passed to dict().update()!")
        
    response = copy.deepcopy(resp)
    response[0].update(data)
    return response