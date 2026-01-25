class Inventory:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        return cls(**data)

    def __repr__(self):
        return f"<Inventory Item {getattr(self, 'item_name', None)} ({getattr(self, 'item_id', None)})>"

    def __getattr__(self, name):
        return None