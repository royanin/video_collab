#from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, BooleanField
from wtforms.validators import Required


#class NameForm(Form):
class NewMeetingForm(FlaskForm):
    """Accepts a screenname."""
    name = StringField('', validators=[Required()],render_kw={"placeholder": "Screen name"})
    #room = StringField('Room', validators=[Required()])
    submit = SubmitField('New Meeting')

class JoinMeetingForm(FlaskForm):
    """Accepts a room url."""
    name_join_room = StringField('', validators=[Required()],render_kw={"placeholder": "Screen name"})
    url = StringField('', validators=[Required()],render_kw={"placeholder": "Room url"})
    submit = SubmitField('Join Room')

class CustomRegistrationForm(FlaskForm):
    """Accepts an email and tos acceptance. No password required"""
    email = StringField('', validators=[Required()],render_kw={"placeholder": "email"})
    coupon_code = StringField('',render_kw={"placeholder": "Coupon code if you have one"})
    tos_ok = BooleanField()
    submit = SubmitField('Sign up')

class CustomLoginForm(FlaskForm):
    """Accepts an email. No password required"""
    email = StringField('', validators=[Required()],render_kw={"placeholder": "email"})
    submit = SubmitField('Sign in')

class CustomConfirmForm(FlaskForm):
    """Accepts an email. No password required"""
    email = StringField('', validators=[Required()],render_kw={"placeholder": "email"})
    submit = SubmitField('Send confirmation link')    
