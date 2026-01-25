from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from forms.profile_form import ProfileEditForm
from models.room import Room
from models.booking import Booking 
from models.service import Service 
from models.invoice import Invoice
from extensions import supabase
from forms.booking_form import BookingForm, AddServiceForm, CancelBookingForm
from forms.room_form import RoomSearchForm 
from datetime import date
from decimal import Decimal

main_bp = Blueprint('main', __name__)

def _parse_date(value):
    if isinstance(value, date) or value is None:
        return value
    try:
        return date.fromisoformat(value)
    except Exception:
        return value

def _raise_on_error(response):
    error = getattr(response, 'error', None)
    if error:
        message = getattr(error, 'message', None) or str(error)
        raise Exception(message)

def _to_iso(value):
    if isinstance(value, date):
        return value.isoformat()
    return value

def _to_json_value(value):
    if isinstance(value, Decimal):
        return float(value)
    return value

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
            update_data = {}

            if form.full_name.data: 
                update_data['full_name'] = form.full_name.data
            
            if form.identification_number.data: 
                update_data['identification_number'] = form.identification_number.data
            
            if form.phone_number.data: 
                update_data['phone_number'] = form.phone_number.data
            
            if form.email.data: 
                update_data['email'] = form.email.data

            if form.current_password.data and form.new_password.data:
                if current_user.password != form.current_password.data:
                    flash('Current password is incorrect.', 'danger')
                    return render_template('profile.html', form=form)
                
                update_data['password'] = form.new_password.data
                flash('Your password has been changed successfully.', 'success')

            if update_data:
                response = supabase.table('customer') \
                    .update(update_data) \
                    .eq('customer_id', current_user.customer_id) \
                    .execute()

                _raise_on_error(response)

                for key, value in update_data.items():
                    setattr(current_user, key, value)

            flash('Profile information updated successfully.', 'success')
            return redirect(url_for('main.profile'))
        except Exception as e:
            flash(f'An error occurred while updating profile: {e}', 'danger')
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
            response = supabase.rpc(
                'get_available_rooms',
                {
                    'p_check_in_date': _to_iso(check_in_date),
                    'p_check_out_date': _to_iso(check_out_date),
                    'p_room_type': room_type,
                    'p_min_price': _to_json_value(min_price),
                    'p_max_price': _to_json_value(max_price),
                    'p_min_capacity': min_capacity,
                    'p_room_number': room_number
                }
            ).execute()

            _raise_on_error(response)

            rooms_list = []
            for r in response.data or []:
                temp_room = Room.from_dict({
                    'room_id': r.get('room_id'),
                    'room_number': r.get('room_number'),
                    'room_type': r.get('room_type'),
                    'price_per_night': r.get('price_per_night'),
                    'capacity': r.get('capacity'),
                    'status': r.get('status')
                })
                if temp_room:
                    temp_room.view_description = r.get('description')
                    rooms_list.append(temp_room)
            rooms = rooms_list
            
            if not rooms:
                flash('No rooms matched your search criteria.', 'info')

        except Exception as e:
            flash(f'An error occurred while searching for rooms: {e}', 'danger')
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
            
            response_default = supabase.rpc(
                'get_available_rooms',
                {
                    'p_check_in_date': _to_iso(rooms_to_query['check_in_date']),
                    'p_check_out_date': _to_iso(rooms_to_query['check_out_date']),
                    'p_room_type': rooms_to_query['room_type'],
                    'p_min_price': _to_json_value(rooms_to_query['min_price']),
                    'p_max_price': _to_json_value(rooms_to_query['max_price']),
                    'p_min_capacity': rooms_to_query['min_capacity'],
                    'p_room_number': rooms_to_query['room_number']
                }
            ).execute()

            _raise_on_error(response_default)

            rooms_list_default = []
            for r in response_default.data or []:
                temp_room = Room.from_dict({
                    'room_id': r.get('room_id'),
                    'room_number': r.get('room_number'),
                    'room_type': r.get('room_type'),
                    'price_per_night': r.get('price_per_night'),
                    'capacity': r.get('capacity'),
                    'status': r.get('status')
                })
                if temp_room:
                    temp_room.view_description = r.get('description')
                    rooms_list_default.append(temp_room)
            rooms = rooms_list_default

        except Exception as e:
            flash(f'Error loading initial rooms: {e}', 'danger')
            print(f"Error loading initial rooms: {e}")
            rooms = []


    return render_template('rooms/list_rooms.html', rooms=rooms, form=form, current_date_str=current_date_str)

@main_bp.route('/book_room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    if current_user.account_status == 0: 
        flash('Your account is currently disabled or inactive. Please contact the administrator for details.', 'danger')
        return redirect(url_for('main.list_rooms'))
    
    room_response = supabase.table('room').select('*').eq('room_id', room_id).maybe_single().execute()
    if not room_response or not room_response.data:
        abort(404)
    room = Room.from_dict(room_response.data)
    form = BookingForm()

    if form.validate_on_submit():
        if form.check_out_date.data <= form.check_in_date.data:
            flash('Check-out date must be after check-in date.', 'danger')
            return render_template('rooms/book_room.html', room=room, form=form) 

        # Kiểm tra ngày check-in không được trong quá khứ
        if form.check_in_date.data < date.today():
            flash('Check-in date cannot be in the past.', 'danger')
            return render_template('rooms/book_room.html', room=room, form=form) 

        try:
            promotion_code_param = form.promotion_code.data if form.promotion_code.data else None
            
            deposit_amount_param = form.deposit_amount.data if form.deposit_amount.data is not None else Decimal(0)

            response = supabase.rpc(
                'create_booking_with_invoice_fixed',
                {
                    'p_customer_id': current_user.customer_id,
                    'p_room_id': room_id,
                    'p_check_in_date': _to_iso(form.check_in_date.data),
                    'p_check_out_date': _to_iso(form.check_out_date.data),
                    'p_special_requests': form.special_requests.data,
                    'p_deposit_amount': _to_json_value(deposit_amount_param),
                    'p_promotion_code': promotion_code_param
                }
            ).execute()

            _raise_on_error(response)

            result = (response.data or [None])[0]

            if result and result.get('booking_id'):
                flash(f'Your booking request was submitted successfully! (Booking ID: {result.get("booking_id")}, Invoice: {result.get("invoice_id")}, Total: {result.get("final_amount")}).', 'success')
                return redirect(url_for('main.booking_details', booking_id=result.get('booking_id')))
            else:
                flash(f'Booking error: {result.get("message") if result else "Unknown error from system. Please try again."}', 'danger')
                return render_template('rooms/book_room.html', room=room, form=form) # Sửa đường dẫn template

        except Exception as e:
            flash(f'A system error occurred while creating the booking: {e}', 'danger')
            print(f"Error calling create_booking_with_invoice_fixed: {e}")
            return render_template('rooms/book_room.html', room=room, form=form) 
    
    if request.args.get('check_in_date') and request.args.get('check_out_date'):
        try:
            form.check_in_date.data = date.fromisoformat(request.args.get('check_in_date'))
            form.check_out_date.data = date.fromisoformat(request.args.get('check_out_date'))
        except ValueError:
            flash('Invalid date format in the URL.', 'warning')

    return render_template('rooms/book_room.html', room=room, form=form)

@main_bp.route('/my_bookings')
@login_required
def my_bookings():
    response = supabase.table('booking') \
        .select('*') \
        .eq('customer_id', current_user.customer_id) \
        .order('booking_date', desc=True) \
        .execute()

    bookings = []
    for b in response.data or []:
        booking = Booking.from_dict(b)
        booking.check_in_date = _parse_date(booking.check_in_date)
        booking.check_out_date = _parse_date(booking.check_out_date)
        booking.booking_date = _parse_date(booking.booking_date)

        room_response = supabase.table('room') \
            .select('room_number, room_type') \
            .eq('room_id', booking.room_id) \
            .maybe_single() \
            .execute()

        invoice_response = supabase.table('invoice') \
            .select('final_amount') \
            .eq('booking_id', booking.booking_id) \
            .maybe_single() \
            .execute()

        room_data = getattr(room_response, 'data', None) if room_response else None
        invoice_data = getattr(invoice_response, 'data', None) if invoice_response else None

        booking.room = Room.from_dict(room_data or {})
        booking.invoice = Invoice.from_dict(invoice_data or {})

        bookings.append(booking)

    return render_template('customer/my_bookings.html', bookings=bookings)

@main_bp.route('/booking_details/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def booking_details(booking_id):
    booking_response = supabase.table('booking').select('*').eq('booking_id', booking_id).maybe_single().execute()
    if not booking_response or not booking_response.data:
        abort(404)
    booking = Booking.from_dict(booking_response.data)
    booking.check_in_date = _parse_date(booking.check_in_date)
    booking.check_out_date = _parse_date(booking.check_out_date)
    booking.booking_date = _parse_date(booking.booking_date)

    if booking.customer_id != current_user.customer_id:
        flash('You do not have permission to access this booking.', 'danger')
        return redirect(url_for('main.my_bookings'))

    # Khởi tạo các form
    add_service_form = AddServiceForm()
    cancel_form = CancelBookingForm()

    if request.method == 'POST':
        if add_service_form.submit_service.data and add_service_form.validate_on_submit():
            if booking.status != 1: 
                flash('Cannot add services to this booking due to its current status (only allowed when "Confirmed").', 'danger')
                return redirect(url_for('main.booking_details', booking_id=booking_id))

            p_service_name = add_service_form.service_name.data
            p_service_description = add_service_form.service_description.data
            p_service_price = add_service_form.service_price.data
            p_service_type = add_service_form.service_type.data if add_service_form.service_type.data else 'ADDITIONAL'

            try:
                response = supabase.rpc(
                    'add_service_to_booking',
                    {
                        'p_booking_id': booking.booking_id,
                        'p_service_name': p_service_name,
                        'p_service_description': p_service_description,
                        'p_service_price': p_service_price,
                        'p_service_type': p_service_type
                    }
                ).execute()

                _raise_on_error(response)

                result = (response.data or [None])[0]

                if result and result.get('service_id'):
                    flash(f'Service "{p_service_name}" was added successfully! Invoice updated: {result.get("updated_final_amount"):,.0f} VND. {result.get("message")}', 'success')
                    return redirect(url_for('main.booking_details', booking_id=booking.booking_id))
                else:
                    flash(f'Error adding service: {result.get("message") if result else "Unknown error from system."}', 'danger')
            except Exception as e:
                flash(f'A system error occurred while adding the service: {e}', 'danger')
                print(f"Error calling add_service_to_booking: {e}")

        elif cancel_form.submit_cancel.data and cancel_form.validate_on_submit():
            if booking.status != 1: 
                flash('Cannot cancel this booking due to its current status (only allowed when "Confirmed").', 'danger')
                return redirect(url_for('main.booking_details', booking_id=booking_id))

            p_cancellation_reason = cancel_form.cancellation_reason.data
            p_customer_id = current_user.customer_id

            try:
                response = supabase.rpc(
                    'cancel_booking_by_customer',
                    {
                        'p_booking_id': booking.booking_id,
                        'p_customer_id': p_customer_id,
                        'p_cancellation_reason': p_cancellation_reason
                    }
                ).execute()

                _raise_on_error(response)

                result = (response.data or [None])[0]

                if result and result.get('booking_id'):
                    flash(f'Booking {result.get("booking_id")} was cancelled successfully! {result.get("message")}', 'success')
                    return redirect(url_for('main.my_bookings')) 
                else:
                    flash(f'Cancellation error: {result.get("message") if result else "Unknown error from system."}', 'danger')
            except Exception as e:
                flash(f'A system error occurred while cancelling the booking: {e}', 'danger')
                print(f"Error calling cancel_booking_by_customer: {e}")
    try:
        booking_details_response = supabase.rpc(
            'get_booking_details',
            {'p_booking_id': booking.booking_id}
        ).execute()

        _raise_on_error(booking_details_response)

        booking_details_result = (booking_details_response.data or [None])[0]

        if booking_details_result is None:
            flash('No booking details or related invoice found.', 'warning')
            booking_details_dict = None
        else:
            booking_details_dict = {
                'booking_id': booking_details_result.get('booking_id'),
                'customer_name': booking_details_result.get('customer_name'),
                'room_number': booking_details_result.get('room_number'),
                'room_type': booking_details_result.get('room_type'),
                'check_in_date': _parse_date(booking_details_result.get('check_in_date')),
                'check_out_date': _parse_date(booking_details_result.get('check_out_date')),
                'nights': booking_details_result.get('nights'),
                'room_price': booking_details_result.get('room_price'),
                'promotion_name': booking_details_result.get('promotion_name'),
                'total_room_amount': booking_details_result.get('total_room_amount'),
                'service_charges': booking_details_result.get('service_charges'),
                'tax_amount': booking_details_result.get('tax_amount'),
                'discount_amount': booking_details_result.get('discount_amount'),
                'final_amount': booking_details_result.get('final_amount'),
                'payment_status': booking_details_result.get('payment_status'),
                # Thêm các thuộc tính khác từ booking_details_result nếu cần,
                # ví dụ: special_requests nếu bạn muốn lấy từ hàm SQL thay vì đối tượng Booking
            }

        services_response = supabase.table('service') \
            .select('*') \
            .eq('booking_id', booking.booking_id) \
            .execute()

        services = [Service.from_dict(item) for item in (services_response.data or [])]

    except Exception as e:
        flash(f'Error loading booking details: {e}', 'danger')
        print(f"Error fetching booking details or services: {e}")
        booking_details_dict = None
        services = [] 

    return render_template('customer/booking_details.html',
                           booking=booking, 
                           booking_details=booking_details_dict, 
                           services=services, 
                           add_service_form=add_service_form,
                           cancel_form=cancel_form)