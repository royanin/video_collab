#from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
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
