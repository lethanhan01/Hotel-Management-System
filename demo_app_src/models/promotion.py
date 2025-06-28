from extensions import db

class Promotion(db.Model):
    __tablename__ = 'promotion'

    promotion_id = db.Column(db.Integer, primary_key=True)
    promotion_name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    discount_percentage = db.Column(db.Numeric)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    applicable_room_types = db.Column(db.String(20))
    minimum_stay_days = db.Column(db.Integer)

    # Mối quan hệ Promotion - Booking: 1 - N (Một Promotion có nhiều Bookings)
    # 'Booking' là tên lớp Model, backref='promotion' tạo ra một thuộc tính 'promotion' trên đối tượng Booking
    bookings = db.relationship('Booking', backref='promotion', lazy=True)

    def __repr__(self):
        return f"<Promotion {self.promotion_name}>"