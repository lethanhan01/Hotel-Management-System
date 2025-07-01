from extensions import db

class Service(db.Model):
    __tablename__ = 'service'

    service_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.booking_id')) # FK tới Booking
    price = db.Column(db.Numeric(10, 2))
    service_type = db.Column(db.String(100))

    def __repr__(self):
        return f"<Service {self.service_name} ({self.service_id})>"