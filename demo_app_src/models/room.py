from extensions import db

class Room(db.Model):
    __tablename__ = 'room'

    room_id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.Integer, unique=True) # Số phòng thường là duy nhất
    room_type = db.Column(db.String(20))
    capacity = db.Column(db.Integer)
    price_per_night = db.Column(db.Numeric(10, 2))
    view_description = db.Column(db.String(500))
    amenities = db.Column(db.TEXT)
    status = db.Column(db.Integer) # 0: Available, 1: Occupied, 2: Under Maintenance
    floor_number = db.Column(db.Integer)

    # Mối quan hệ Room - Booking: 1 - N (Một Room có nhiều Bookings)
    # 'Booking' là tên lớp Model, backref='room' tạo ra một thuộc tính 'room' trên đối tượng Booking
    bookings = db.relationship('Booking', backref='room', lazy=True)

    # Mối quan hệ Room - Inventory: N - N
    # Sử dụng secondary='room_inventory' để chỉ định bảng trung gian
    # backref='rooms' sẽ tạo một thuộc tính 'rooms' trên Inventory để truy cập các Room liên quan
    inventory_items = db.relationship(
        'Inventory',
        secondary='room_inventory', # Tên bảng trung gian
        backref=db.backref('rooms', lazy=True)
    )

    def __repr__(self):
        return f"<Room {self.room_number} ({self.room_type})>"
    
    def is_available(self):
        return self.status == 0 