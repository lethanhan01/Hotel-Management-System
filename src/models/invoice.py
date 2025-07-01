from extensions import db

class Invoice(db.Model):
    __tablename__ = 'invoice'

    invoice_id = db.Column(db.Integer, primary_key=True)
    # Khóa ngoại và ràng buộc UNIQUE để đảm bảo 1-1 với Booking
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.booking_id'), unique=True)
    issue_date = db.Column(db.Date)
    total_amount = db.Column(db.Numeric(10, 2))
    payment_method = db.Column(db.String(20))
    payment_status = db.Column(db.Integer) # 0: Pending, 1: Paid
    tax_amount = db.Column(db.Numeric(10, 2))
    service_charges = db.Column(db.Numeric(10, 2))
    discount_amount = db.Column(db.Numeric(10, 2))
    final_amount = db.Column(db.Numeric(10, 2))

    def __repr__(self):
        return f"<Invoice {self.invoice_id} for Booking {self.booking_id}>"