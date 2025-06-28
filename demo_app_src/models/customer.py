from extensions import db
from flask_login import UserMixin
import datetime

class Customer(db.Model, UserMixin):
    __tablename__ = 'customer'

    customer_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    identification_number = db.Column(db.String(12))
    phone_number = db.Column(db.String(11))
    email = db.Column(db.String(100))
    nationality = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False) # Đổi lại thành 'password', độ dài tùy thuộc bạn

    registration_date = db.Column(db.Date, default=datetime.date.today)
    membership_level = db.Column(db.Integer, default=0)
    account_status = db.Column(db.Integer)

    bookings = db.relationship('Booking', backref='customer', lazy=True)

    def __repr__(self):
        return f"<Customer {self.username} ({self.customer_id})>"

    def get_id(self):
        return str(self.customer_id)

    # Bỏ các phương thức set_password và check_password
    # Thay vào đó, bạn sẽ truy cập self.password trực tiếp để so sánh