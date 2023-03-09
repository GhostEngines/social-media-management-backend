

def serializeDict(a, exclude = []) -> dict:
    return {**{i:str(a[i]) for i in a if i=='_id' and i not in exclude},**{i:a[i] for i in a if i!='_id' and i not in exclude}}

def serializeList(entity, exclude = []) -> list:
    return [serializeDict(a, exclude) for a in entity]
