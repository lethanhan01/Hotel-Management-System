from extensions import db
import datetime # Import datetime cho booking_date mặc định

class Booking(db.Model):
    __tablename__ = 'booking'

    booking_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id')) # FK tới Customer
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'))             # FK tới Room
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotion.promotion_id')) # FK tới Promotion
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    booking_date = db.Column(db.Date, default=datetime.date.today) # Mặc định là ngày hiện tại
    status = db.Column(db.Integer) # 0: Cancelled, 1: Confirmed
    special_requests = db.Column(db.String(500))
    deposit_amount = db.Column(db.Numeric(10, 2))
    cancellation_reason = db.Column(db.String(500))
    cancellation_date = db.Column(db.Date)

    # Mối quan hệ Booking - Review: 1 - 1
    review = db.relationship('Review', backref='booking', uselist=False, lazy=True)

    # Mối quan hệ Booking - Invoice: 1 - 1
    invoice = db.relationship('Invoice', backref='booking', uselist=False, lazy=True)

    # Mối quan hệ Booking - Service: 1 - 1 (Một Booking có nhiều Services)
    service = db.relationship('Service', backref='booking', uselist = False, lazy=True)

    def __repr__(self):
        return f"<Booking {self.booking_id} (Customer {self.customer_id}, Room {self.room_id})>"