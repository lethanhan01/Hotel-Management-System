import os
from flask import Flask, redirect, url_for
from config import config
from extensions import db, login_manager 

from models.customer import Customer
from models.room import Room
from models.promotion import Promotion
from models.booking import Booking
from models.invoice import Invoice
from models.review import Review
from models.inventory import Inventory
from models.room_inventory import RoomInventory
from models.service import Service

from routes.auth import auth_bp
from routes.main import main_bp 

config_name = os.environ.get('FLASK_CONFIG') or 'default'

app = Flask(__name__)
app.config.from_object(config[config_name])

db.init_app(app)
login_manager.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("DB created")

        if not Customer.query.filter_by(username='admin').first():
            admin_user = Customer(
                #customer_id=1501,
                username='admin',
                full_name='Admin User',
                email='admin@example.com',
                identification_number='123456789012',
                phone_number='01234567891',
                nationality='Vietnamese',
                membership_level=99,
                account_status=1
            )
            admin_user.password = 'admin123' 
            db.session.add(admin_user)      
            db.session.commit()             
            print("Admin user 'admin' created with password 'admin123'")
        else:
            print("Admin user 'admin' already exists.") 
    app.run(debug=True)
