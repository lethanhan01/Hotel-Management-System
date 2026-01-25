class Review:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        return cls(**data)

    def __repr__(self):
        return f"<Review {getattr(self, 'review_id', None)} - Booking {getattr(self, 'booking_id', None)} - Rating {getattr(self, 'rating', None)}>"

    def __getattr__(self, name):
        return None