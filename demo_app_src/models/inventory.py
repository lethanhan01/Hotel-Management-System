from extensions import db

class Inventory(db.Model):
    __tablename__ = 'inventory'

    item_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(500))
    quantity_in_stock = db.Column(db.Integer)
    unit_price = db.Column(db.Numeric(10, 2))
    supplier_info = db.Column(db.String)
    location_in_storage = db.Column(db.String(100))

    # Mối quan hệ Many-to-Many đã được định nghĩa ở Room, không cần định nghĩa lại ở đây
    # 'rooms' backref từ Room model đã tạo ra thuộc tính này.

    def __repr__(self):
        return f"<Inventory Item {self.item_name} ({self.item_id})>"