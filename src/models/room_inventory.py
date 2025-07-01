from extensions import db

class RoomInventory(db.Model):
    __tablename__ = 'room_inventory'

    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory.item_id'), primary_key=True)

    # Có thể thêm các thuộc tính khác nếu cần cho mối quan hệ này, ví dụ: quantity, date_assigned
    # quantity = db.Column(db.Integer)
    # assigned_date = db.Column(db.Date)

    def __repr__(self):
        return f"<RoomInventory Room {self.room_id} - Item {self.item_id}>"