from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from forms.profile_form import ProfileEditForm
from models.room import Room
from models.booking import Booking 
from models.service import Service 
from extensions import db
from forms.booking_form import BookingForm, AddServiceForm, CancelBookingForm
from forms.room_form import RoomSearchForm 
from datetime import date
from decimal import Decimal

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def index():
    return render_template('index.html')

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileEditForm() 

    if form.validate_on_submit():
        try:
            if form.full_name.data: 
                current_user.full_name = form.full_name.data
            
            if form.identification_number.data: 
                current_user.identification_number = form.identification_number.data
            
            if form.phone_number.data: 
                current_user.phone_number = form.phone_number.data
            
            if form.email.data: 
                current_user.email = form.email.data

            if form.current_password.data and form.new_password.data:
                if current_user.password != form.current_password.data:
                    flash('Mật khẩu hiện tại không đúng.', 'danger')
                    return render_template('profile.html', form=form)
                
                current_user.password = form.new_password.data 
                flash('Mật khẩu của bạn đã được thay đổi thành công.', 'success')

            db.session.commit()
            flash('Thông tin hồ sơ đã được cập nhật thành công.', 'success')
            return redirect(url_for('main.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Đã xảy ra lỗi khi cập nhật hồ sơ: {e}', 'danger')
            print(f"Error updating profile: {e}")
    elif request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.identification_number.data = current_user.identification_number
        form.phone_number.data = current_user.phone_number
        form.email.data = current_user.email
    
    return render_template('profile.html', form=form)

@main_bp.route('/rooms', methods=['GET', 'POST'])
def list_rooms():
    form = RoomSearchForm()
    rooms = []
    
    current_date_str = date.today().strftime('%Y-%m-%d')

    if form.validate_on_submit():
        check_in_date = form.check_in_date.data
        check_out_date = form.check_out_date.data
        room_type = form.room_type.data if form.room_type.data != '' else None
        min_price = form.min_price.data
        max_price = form.max_price.data
        min_capacity = form.min_capacity.data
        room_number = form.room_number.data # LẤY GIÁ TRỊ TỪ FORM

        try:
            sql_query = f"""
                SELECT room_id, room_number, room_type, price_per_night, capacity, status, description
                FROM get_available_rooms(
                    :check_in_date,
                    :check_out_date,
                    :room_type,
                    :min_price,
                    :max_price,
                    :min_capacity,
                    :room_number -- TRUYỀN THAM SỐ MỚI
                );
            """
            result = db.session.execute(
                db.text(sql_query),
                {
                    'check_in_date': check_in_date,
                    'check_out_date': check_out_date,
                    'room_type': room_type,
                    'min_price': min_price,
                    'max_price': max_price,
                    'min_capacity': min_capacity,
                    'room_number': room_number # GÁN GIÁ TRỊ VÀO PARAMETERS
                }
            ).fetchall()

            rooms_list = []
            for r in result:
                temp_room = Room(
                    room_id=r.room_id,
                    room_number=r.room_number,
                    room_type=r.room_type,
                    price_per_night=r.price_per_night,
                    capacity=r.capacity,
                    status=r.status
                )
                temp_room.view_description = r.description
                rooms_list.append(temp_room)
            rooms = rooms_list
            
            if not rooms:
                flash('Không tìm thấy phòng phù hợp với tiêu chí tìm kiếm của bạn.', 'info')

        except Exception as e:
            flash(f'Đã xảy ra lỗi khi tìm kiếm phòng: {e}', 'danger')
            print(f"Error calling get_available_rooms: {e}")
            rooms = []
    else:
        try:
            form.check_in_date.data = request.args.get('check_in_date', type=date.fromisoformat)
            form.check_out_date.data = request.args.get('check_out_date', type=date.fromisoformat)
            form.room_type.data = request.args.get('room_type', type=str)
            form.min_price.data = request.args.get('min_price', type=Decimal) # Sử dụng Decimal
            form.max_price.data = request.args.get('max_price', type=Decimal) # Sử dụng Decimal
            form.min_capacity.data = request.args.get('min_capacity', type=int)
            form.room_number.data = request.args.get('room_number', type=int) # LẤY GIÁ TRỊ room_number TỪ QUERY ARGS

            # Gọi hàm get_available_rooms với các giá trị mặc định (hoặc từ query args)
            # Điều này đảm bảo trang luôn hiển thị danh sách phòng khi tải lần đầu
            # và khi có các tham số trên URL
            rooms_to_query = {
                'check_in_date': form.check_in_date.data,
                'check_out_date': form.check_out_date.data,
                'room_type': form.room_type.data if form.room_type.data != '' else None,
                'min_price': form.min_price.data,
                'max_price': form.max_price.data,
                'min_capacity': form.min_capacity.data,
                'room_number': form.room_number.data # TRUYỀN room_number VÀO ĐÂY CŨNG
            }
            
            sql_query_default = f"""
                SELECT room_id, room_number, room_type, price_per_night, capacity, status, description
                FROM get_available_rooms(
                    :check_in_date, :check_out_date, :room_type, :min_price, :max_price, :min_capacity, :room_number
                );
            """
            result_default = db.session.execute(db.text(sql_query_default), rooms_to_query).fetchall()
            
            rooms_list_default = []
            for r in result_default:
                temp_room = Room(
                    room_id=r.room_id,
                    room_number=r.room_number,
                    room_type=r.room_type,
                    price_per_night=r.price_per_night,
                    capacity=r.capacity,
                    status=r.status
                )
                temp_room.view_description = r.description
                rooms_list_default.append(temp_room)
            rooms = rooms_list_default

        except Exception as e:
            flash(f'Lỗi khi tải danh sách phòng ban đầu: {e}', 'danger')
            print(f"Error loading initial rooms: {e}")
            rooms = []


    return render_template('rooms/list_rooms.html', rooms=rooms, form=form, current_date_str=current_date_str)

@main_bp.route('/book_room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    if current_user.account_status == 0: 
        flash('Tài khoản của bạn hiện đang bị vô hiệu hóa hoặc không hoạt động. Vui lòng liên hệ quản trị viên để biết thêm chi tiết.', 'danger')
        return redirect(url_for('main.list_rooms'))
    
    room = Room.query.get_or_404(room_id)
    form = BookingForm()

    if form.validate_on_submit():
        if form.check_out_date.data <= form.check_in_date.data:
            flash('Ngày trả phòng phải sau ngày nhận phòng.', 'danger')
            return render_template('rooms/book_room.html', room=room, form=form) 

        # Kiểm tra ngày check-in không được trong quá khứ
        if form.check_in_date.data < date.today():
            flash('Ngày nhận phòng không thể là ngày trong quá khứ.', 'danger')
            return render_template('rooms/book_room.html', room=room, form=form) 

        try:
            promotion_code_param = form.promotion_code.data if form.promotion_code.data else None
            
            deposit_amount_param = form.deposit_amount.data if form.deposit_amount.data is not None else Decimal(0)

            result = db.session.execute(
                db.text("""
                    SELECT booking_id, invoice_id, final_amount, message 
                    FROM create_booking_with_invoice_fixed(
                        :p_customer_id, 
                        :p_room_id, 
                        :p_check_in_date, 
                        :p_check_out_date, 
                        :p_special_requests, 
                        :p_deposit_amount, 
                        :p_promotion_code
                    );
                """),
                {
                    'p_customer_id': current_user.customer_id,
                    'p_room_id': room_id,
                    'p_check_in_date': form.check_in_date.data,
                    'p_check_out_date': form.check_out_date.data,
                    'p_special_requests': form.special_requests.data,
                    'p_deposit_amount': deposit_amount_param,
                    'p_promotion_code': promotion_code_param
                }
            ).fetchone() 

            if result and result.booking_id: 
                db.session.commit() 
                flash(f'Yêu cầu đặt phòng của bạn đã được gửi thành công! (Mã booking: {result.booking_id}, Hóa đơn: {result.invoice_id}, Tổng tiền: {result.final_amount}).', 'success')
                return redirect(url_for('main.booking_details', booking_id=result.booking_id))
            else:
                db.session.rollback() 
                flash(f'Lỗi đặt phòng: {result.message if result and result.message else "Không rõ lỗi từ hệ thống. Vui lòng thử lại."}', 'danger')
                return render_template('rooms/book_room.html', room=room, form=form) # Sửa đường dẫn template

        except Exception as e:
            db.session.rollback() 
            flash(f'Đã xảy ra lỗi hệ thống khi đặt phòng: {e}', 'danger')
            print(f"Error calling create_booking_with_invoice_fixed: {e}")
            return render_template('rooms/book_room.html', room=room, form=form) 
    
    if request.args.get('check_in_date') and request.args.get('check_out_date'):
        try:
            form.check_in_date.data = date.fromisoformat(request.args.get('check_in_date'))
            form.check_out_date.data = date.fromisoformat(request.args.get('check_out_date'))
        except ValueError:
            flash('Định dạng ngày không hợp lệ trong URL.', 'warning')

    return render_template('rooms/book_room.html', room=room, form=form)

@main_bp.route('/my_bookings')
@login_required
def my_bookings():
    user_bookings = Booking.query.filter_by(customer_id=current_user.customer_id)\
                                 .order_by(Booking.booking_date.desc()).all()
    return render_template('customer/my_bookings.html', bookings=user_bookings)

@main_bp.route('/booking_details/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def booking_details(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.customer_id != current_user.customer_id:
        flash('Bạn không có quyền truy cập đặt phòng này.', 'danger')
        return redirect(url_for('main.my_bookings'))

    # Khởi tạo các form
    add_service_form = AddServiceForm()
    cancel_form = CancelBookingForm()

    if request.method == 'POST':
        if add_service_form.submit_service.data and add_service_form.validate_on_submit():
            if booking.status != 1: 
                flash('Không thể thêm dịch vụ cho đặt phòng này do trạng thái hiện tại không hợp lệ (chỉ được thêm khi "Đã Xác nhận").', 'danger')
                return redirect(url_for('main.booking_details', booking_id=booking_id))

            p_service_name = add_service_form.service_name.data
            p_service_description = add_service_form.service_description.data
            p_service_price = add_service_form.service_price.data
            p_service_type = add_service_form.service_type.data if add_service_form.service_type.data else 'ADDITIONAL'

            try:
                result = db.session.execute(
                    db.text("""
                        SELECT service_id, updated_final_amount, message
                        FROM add_service_to_booking(
                            :p_booking_id,
                            :p_service_name,
                            :p_service_description,
                            :p_service_price,
                            :p_service_type
                        );
                    """),
                    {
                        'p_booking_id': booking.booking_id,
                        'p_service_name': p_service_name,
                        'p_service_description': p_service_description,
                        'p_service_price': p_service_price,
                        'p_service_type': p_service_type
                    }
                ).fetchone()

                if result and result.service_id:
                    db.session.commit() 
                    flash(f'Dịch vụ "{p_service_name}" đã được thêm thành công! Hóa đơn cập nhật: {result.updated_final_amount:,.0f} VNĐ. {result.message}', 'success')
                    return redirect(url_for('main.booking_details', booking_id=booking.booking_id))
                else:
                    db.session.rollback() 
                    flash(f'Lỗi thêm dịch vụ: {result.message if result and result.message else "Không rõ lỗi từ hệ thống."}', 'danger')
            except Exception as e:
                db.session.rollback()
                flash(f'Đã xảy ra lỗi hệ thống khi thêm dịch vụ: {e}', 'danger')
                print(f"Error calling add_service_to_booking: {e}")

        elif cancel_form.submit_cancel.data and cancel_form.validate_on_submit():
            if booking.status != 1: 
                flash('Không thể hủy đặt phòng này do trạng thái hiện tại không hợp lệ (chỉ được hủy khi "Đã Xác nhận").', 'danger')
                return redirect(url_for('main.booking_details', booking_id=booking_id))

            p_cancellation_reason = cancel_form.cancellation_reason.data
            p_customer_id = current_user.customer_id

            try:
                result = db.session.execute(
                    db.text("""
                        SELECT booking_id, message
                        FROM cancel_booking_by_customer(
                            :p_booking_id,
                            :p_customer_id,
                            :p_cancellation_reason
                        );
                    """),
                    {
                        'p_booking_id': booking.booking_id,
                        'p_customer_id': p_customer_id,
                        'p_cancellation_reason': p_cancellation_reason
                    }
                ).fetchone()

                if result and result.booking_id:
                    db.session.commit() # Commit transaction
                    flash(f'Đã hủy đặt phòng {result.booking_id} thành công! {result.message}', 'success')
                    return redirect(url_for('main.my_bookings')) 
                else:
                    db.session.rollback() 
                    flash(f'Lỗi hủy phòng: {result.message if result and result.message else "Không rõ lỗi từ hệ thống."}', 'danger')
            except Exception as e:
                db.session.rollback()
                flash(f'Đã xảy ra lỗi hệ thống khi hủy phòng: {e}', 'danger')
                print(f"Error calling cancel_booking_by_customer: {e}")
    try:
        sql_query_details = f"SELECT * FROM get_booking_details(:booking_id);"
        print(f"Executing SQL query for booking_id: {booking.booking_id}") # DEBUG
        booking_details_result = db.session.execute(
            db.text(sql_query_details),
            {'booking_id': booking.booking_id}
        ).fetchone()

        print(f"Raw booking_details_result: {booking_details_result}") # DEBUG

        if booking_details_result is None:
            flash('Không tìm thấy chi tiết đặt phòng hoặc hóa đơn liên quan.', 'warning')
            booking_details_dict = None
        else:
            # Chuyển RowProxy object thành dict để dễ dàng truy cập trong template
            # Cần đảm bảo các tên cột khớp với template của bạn
            booking_details_dict = {
                'booking_id': booking_details_result.booking_id,
                'customer_name': booking_details_result.customer_name,
                'room_number': booking_details_result.room_number,
                'room_type': booking_details_result.room_type,
                'check_in_date': booking_details_result.check_in_date,
                'check_out_date': booking_details_result.check_out_date,
                'nights': booking_details_result.nights,
                'room_price': booking_details_result.room_price,
                'promotion_name': booking_details_result.promotion_name,
                'total_room_amount': booking_details_result.total_room_amount,
                'service_charges': booking_details_result.service_charges,
                'tax_amount': booking_details_result.tax_amount,
                'discount_amount': booking_details_result.discount_amount,
                'final_amount': booking_details_result.final_amount,
                'payment_status': booking_details_result.payment_status,
                # Thêm các thuộc tính khác từ booking_details_result nếu cần,
                # ví dụ: special_requests nếu bạn muốn lấy từ hàm SQL thay vì đối tượng Booking
            }
            print(f"Converted booking_details_dict: {booking_details_dict}") # DEBUG

        services = Service.query.filter_by(booking_id=booking.booking_id).all()
        print(f"Services for booking_id {booking.booking_id}: {services}") # DEBUG

    except Exception as e:
        flash(f'Lỗi khi tải chi tiết đặt phòng: {e}', 'danger')
        print(f"Error fetching booking details or services: {e}")
        booking_details_dict = None
        services = [] 

    return render_template('customer/booking_details.html',
                           booking=booking, 
                           booking_details=booking_details_dict, 
                           services=services, 
                           add_service_form=add_service_form,
                           cancel_form=cancel_form)