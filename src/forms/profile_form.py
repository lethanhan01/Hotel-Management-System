from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Optional, Length, EqualTo

class ProfileEditForm(FlaskForm):
    full_name = StringField('Full name', validators=[Optional(), Length(max=100)]) 
    identification_number = StringField('Identification number', validators=[Optional(), Length(max=20)]) 
    phone_number = StringField('Phone number', validators=[Optional(), Length(max=15)])
    email = StringField('Email', validators=[Optional(), Length(max=100)]) 
    
    current_password = PasswordField('Current password', validators=[Optional()])
    new_password = PasswordField('New password', validators=[Optional(), Length(min=6, message="New password must be at least 6 characters.")])
    confirm_new_password = PasswordField('Confirm new password', validators=[
        Optional(),
        EqualTo('new_password', message='Password confirmation does not match.')
    ])

    submit = SubmitField('Update information')

    def validate(self, **kwargs):
        if not super().validate(**kwargs):
            return False

        if self.new_password.data or self.confirm_new_password.data:
            if not self.current_password.data:
                self.current_password.errors.append('Please enter your current password to change your password.')
                return False
            if self.new_password.data and not self.confirm_new_password.data:
                self.confirm_new_password.errors.append('Please confirm the new password.')
                return False
            if not self.new_password.data and self.confirm_new_password.data:
                self.new_password.errors.append('Please enter the new password.')
                return False
        
        return True