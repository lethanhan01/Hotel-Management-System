class Room:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        return cls(**data)

    def __repr__(self):
        return f"<Room {getattr(self, 'room_number', None)} ({getattr(self, 'room_type', None)})>"

    def __getattr__(self, name):
        return None
    
    def is_available(self):
        return getattr(self, 'status', None) == 0