from extensions import db

class Review(db.Model):
    __tablename__ = 'review'

    review_id = db.Column(db.Integer, primary_key=True)
    # Khóa ngoại và ràng buộc UNIQUE để đảm bảo 1-1 với Booking
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.booking_id'), unique=True)
    rating = db.Column(db.Integer) # Thường từ 1-5 sao
    comment = db.Column(db.String(500))
    review_date = db.Column(db.Date)
    response = db.Column(db.String(500))
    response_date = db.Column(db.Date)

    def __repr__(self):
        return f"<Review {self.review_id} - Booking {self.booking_id} - Rating {self.rating}>"