from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, DecimalField, SubmitField, SelectField
from wtforms.validators import Optional, NumberRange, ValidationError
from datetime import date

class RoomSearchForm(FlaskForm):
    check_in_date = DateField('Ngày nhận phòng', format='%Y-%m-%d', validators=[Optional()])
    check_out_date = DateField('Ngày trả phòng', format='%Y-%m-%d', validators=[Optional()])
    room_type = SelectField('Loại phòng', choices=[
        ('', 'Tất cả'),
        ('Standard', 'Standard'),
        ('Deluxe', 'Deluxe'),
        ('Suite', 'Suite'),
        ('Single', 'Single'),
        ('Double', 'Double')
    ], validators=[Optional()])
    min_price = DecimalField('Giá tối thiểu', validators=[Optional(), NumberRange(min=0)], places=0)
    max_price = DecimalField('Giá tối đa', validators=[Optional(), NumberRange(min=0)], places=0)
    min_capacity = IntegerField('Sức chứa tối thiểu', validators=[Optional(), NumberRange(min=1)])
    room_number = IntegerField('Số phòng', validators=[Optional(), NumberRange(min=1)]) 
    submit = SubmitField('Tìm kiếm')

    def validate(self, **kwargs):
        if not super().validate(**kwargs):
            return False
        
        # Validation tùy chỉnh cho ngày check-in/check-out
        if self.check_in_date.data and self.check_out_date.data:
            if self.check_out_date.data <= self.check_in_date.data:
                self.check_out_date.errors.append('Ngày trả phòng phải sau ngày nhận phòng.')
                return False
            # Kiểm tra ngày nhận phòng không được ở quá khứ chỉ khi cả hai ngày được nhập
            if self.check_in_date.data < date.today():
                self.check_in_date.errors.append('Ngày nhận phòng không thể ở trong quá khứ.')
                return False
        # Nếu chỉ có một trong hai ngày được nhập, yêu cầu nhập đủ cả hai
        elif self.check_in_date.data and not self.check_out_date.data:
            self.check_out_date.errors.append('Vui lòng nhập ngày trả phòng.')
            return False
        elif not self.check_in_date.data and self.check_out_date.data:
            self.check_in_date.errors.append('Vui lòng nhập ngày nhận phòng.')
            return False
        
        if self.min_price.data is not None and self.max_price.data is not None:
            if self.min_price.data > self.max_price.data:
                self.max_price.errors.append('Giá tối đa phải lớn hơn hoặc bằng giá tối thiểu.')
                return False
        return True