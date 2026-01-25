from flask_login import UserMixin
import datetime

def _parse_date(value):
    if isinstance(value, datetime.date) or value is None:
        return value
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value.split('T')[0])
        except Exception:
            return value
    return value

class Customer(UserMixin):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        if 'registration_date' in data:
            data['registration_date'] = _parse_date(data.get('registration_date'))
        return cls(**data)

    def __repr__(self):
        return f"<Customer {getattr(self, 'username', None)} ({getattr(self, 'customer_id', None)})>"

    def __getattr__(self, name):
        return None

    def get_id(self):
        return str(getattr(self, 'customer_id', ''))