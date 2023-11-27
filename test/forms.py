# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, BooleanField, TextAreaField, DateField, TimeField, SelectField
from wtforms.validators import DataRequired, Email
from wtforms.validators import DataRequired, ValidationError, Optional

class LocationForm(FlaskForm):
    location_name = StringField('Location Name', validators=[DataRequired()])
    floor = SelectField('Floor', choices=[(str(i), str(i)) for i in range(1, 11)])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class LogoutForm(FlaskForm):
    submit = SubmitField('ログアウト')

class AdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Add Submit')

class SettingsForm(FlaskForm):
    username = StringField('New Username')
    new_password = PasswordField('New Password')
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password')
    icon = FileField('Upload Icon')
    dark_mode = BooleanField('Dark Mode')
    submit = SubmitField('Save Changes')

class ReservationForm(FlaskForm):
    start_date = DateField('開始日', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('開始時間', format='%H:%M', validators=[Optional()])
    end_date = DateField('終了日', format='%Y-%m-%d', validators=[Optional()])
    end_time = TimeField('終了時間', format='%H:%M', validators=[Optional()])
    is_all_day = BooleanField('終日予約')
    title = StringField('予約タイトル', validators=[DataRequired()])
    submit = SubmitField('予約する')

    # バリデーションの追加
    def validate_end_date(form, field):
        if form.is_all_day.data and field.data:
            raise ValidationError('終日予約の場合、終了日は指定不要です。')

    def validate_end_time(form, field):
        if form.is_all_day.data and field.data:
            raise ValidationError('終日予約の場合、終了時間は指定不要です。')
