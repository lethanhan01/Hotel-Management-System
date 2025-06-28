from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Optional, Length, EqualTo

class ProfileEditForm(FlaskForm):
    full_name = StringField('Họ và tên', validators=[Optional(), Length(max=100)]) 
    identification_number = StringField('Số CMND/CCCD', validators=[Optional(), Length(max=20)]) 
    phone_number = StringField('Số điện thoại', validators=[Optional(), Length(max=15)])
    email = StringField('Email', validators=[Optional(), Length(max=100)]) 
    
    current_password = PasswordField('Mật khẩu hiện tại', validators=[Optional()])
    new_password = PasswordField('Mật khẩu mới', validators=[Optional(), Length(min=6, message="Mật khẩu mới phải có ít nhất 6 ký tự.")])
    confirm_new_password = PasswordField('Xác nhận mật khẩu mới', validators=[
        Optional(),
        EqualTo('new_password', message='Mật khẩu xác nhận không khớp.')
    ])

    submit = SubmitField('Cập nhật thông tin')

    def validate(self, **kwargs):
        if not super().validate(**kwargs):
            return False

        if self.new_password.data or self.confirm_new_password.data:
            if not self.current_password.data:
                self.current_password.errors.append('Vui lòng nhập mật khẩu hiện tại để thay đổi mật khẩu.')
                return False
            if self.new_password.data and not self.confirm_new_password.data:
                self.confirm_new_password.errors.append('Vui lòng xác nhận mật khẩu mới.')
                return False
            if not self.new_password.data and self.confirm_new_password.data:
                self.new_password.errors.append('Vui lòng nhập mật khẩu mới.')
                return False
        
        return True