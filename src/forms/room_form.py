from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, DecimalField, SubmitField, SelectField
from wtforms.validators import Optional, NumberRange, ValidationError
from datetime import date

class RoomSearchForm(FlaskForm):
    check_in_date = DateField('Check-in date', format='%Y-%m-%d', validators=[Optional()])
    check_out_date = DateField('Check-out date', format='%Y-%m-%d', validators=[Optional()])
    room_type = SelectField('Room type', choices=[
        ('', 'All'),
        ('Standard', 'Standard'),
        ('Deluxe', 'Deluxe'),
        ('Suite', 'Suite'),
        ('Single', 'Single'),
        ('Double', 'Double')
    ], validators=[Optional()])
    min_price = DecimalField('Min price', validators=[Optional(), NumberRange(min=0)], places=0)
    max_price = DecimalField('Max price', validators=[Optional(), NumberRange(min=0)], places=0)
    min_capacity = IntegerField('Min capacity', validators=[Optional(), NumberRange(min=1)])
    room_number = IntegerField('Room number', validators=[Optional(), NumberRange(min=1)]) 
    submit = SubmitField('Search')

    def validate(self, **kwargs):
        if not super().validate(**kwargs):
            return False
        # Custom validation for check-in / check-out dates
        if self.check_in_date.data and self.check_out_date.data:
            # check-out must be after check-in
            if self.check_out_date.data <= self.check_in_date.data:
                self.check_out_date.errors.append('Check-out date must be after check-in date.')
                return False
            # check-in should not be in the past
            if self.check_in_date.data < date.today():
                self.check_in_date.errors.append('Check-in date cannot be in the past.')
                return False
        # If only one of the two dates is provided, require both
        elif self.check_in_date.data and not self.check_out_date.data:
            self.check_out_date.errors.append('Please enter a check-out date.')
            return False
        elif not self.check_in_date.data and self.check_out_date.data:
            self.check_in_date.errors.append('Please enter a check-in date.')
            return False
        
        if self.min_price.data is not None and self.max_price.data is not None:
            if self.min_price.data > self.max_price.data:
                self.max_price.errors.append('Max price must be greater than or equal to min price.')
                return False
        return True