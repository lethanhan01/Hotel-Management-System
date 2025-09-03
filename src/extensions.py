from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # This is the destination when @login_required finds the user not logged in
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"



# Hàm để tải người dùng từ ID, cần thiết cho Flask-Login
# Bạn sẽ cần import Customer model ở đây hoặc trong app.py sau
# from models.customer import Customer # Ví dụ, sẽ import sau khi Customer được định nghĩa

@login_manager.user_loader
def load_user(user_id):
#     # Đảm bảo bạn import Customer model ở trên cùng của file này hoặc trong app.py
#     # nếu bạn muốn giữ extensions.py chỉ khởi tạo db và manager
#     # Để đơn giản, ta sẽ import Customer ngay tại đây
    from models.customer import Customer
    return Customer.query.get(int(user_id))