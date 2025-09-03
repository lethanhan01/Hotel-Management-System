from flask_wtf import FlaskForm
from wtforms import DateField, StringField, DecimalField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from datetime import date

class BookingForm(FlaskForm):
    check_in_date = DateField('Check-in date', format='%Y-%m-%d', validators=[DataRequired()])
    check_out_date = DateField('Check-out date', format='%Y-%m-%d', validators=[DataRequired()])
    special_requests = StringField('Special requests', validators=[Optional()])
    deposit_amount = DecimalField('Deposit amount', default=0, validators=[Optional(), NumberRange(min=0)])
    promotion_code = StringField('Promotion code', validators=[Optional()])
    submit = SubmitField('Book now')

class AddServiceForm(FlaskForm):
    service_name = StringField('Service name', validators=[DataRequired(), Length(max=100)])
    service_description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    service_price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)])
    service_type = StringField('Service type', validators=[DataRequired(), Length(max=50)])
    submit_service = SubmitField('Add service')

class CancelBookingForm(FlaskForm):
    cancellation_reason = TextAreaField('Cancellation reason', validators=[DataRequired(), Length(min=10, max=500)])
    submit_cancel = SubmitField('Cancel booking')