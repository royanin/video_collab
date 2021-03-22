#from flask_wtf import Form
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import Required


#class NameForm(Form):
class NameForm(FlaskForm):
    """Accepts a nickname and a room."""
    name = StringField('', validators=[Required()],render_kw={"placeholder": "Screen name"})
    #room = StringField('Room', validators=[Required()])
    submit = SubmitField('Join Room')
