from flask_wtf import FlaskForm
from wtforms import DateField, StringField, DecimalField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from datetime import date

class BookingForm(FlaskForm):
    check_in_date = DateField('Ngày nhận phòng', format='%Y-%m-%d', validators=[DataRequired()])
    check_out_date = DateField('Ngày trả phòng', format='%Y-%m-%d', validators=[DataRequired()])
    special_requests = StringField('Yêu cầu đặc biệt', validators=[Optional()])
    deposit_amount = DecimalField('Số tiền đặt cọc', default=0, validators=[Optional(), NumberRange(min=0)])
    promotion_code = StringField('Mã khuyến mãi', validators=[Optional()])
    submit = SubmitField('Đặt phòng ngay')

class AddServiceForm(FlaskForm):
    service_name = StringField('Tên dịch vụ', validators=[DataRequired(), Length(max=100)])
    service_description = TextAreaField('Mô tả', validators=[Optional(), Length(max=500)])
    service_price = DecimalField('Giá', validators=[DataRequired(), NumberRange(min=0)])
    service_type = StringField('Loại dịch vụ', validators=[DataRequired(), Length(max=50)])
    submit_service = SubmitField('Thêm dịch vụ')

class CancelBookingForm(FlaskForm):
    cancellation_reason = TextAreaField('Lý do hủy', validators=[DataRequired(), Length(min=10, max=500)])
    submit_cancel = SubmitField('Hủy đặt phòng')