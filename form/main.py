from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, ValidationError
from flask_bootstrap import Bootstrap5


class Length(object):
    def __init__(self, min=-1, max=-1, message=None):
        self.min = min
        self.max = max
        if not message:
            message = 'Field must be between %i and %i characters long.' % (min, max)
        self.message = message

    def __call__(self, form, field):
        l = field.data and len(field.data) or 0
        if l < self.min or self.max != -1 and l > self.max:
            raise ValidationError(self.message)

class Email(object):
    def __init__(self, message=None):
        if not message:
            message = 'Field must be an email address.'
        self.message = message

    def __call__(self, form, field):
        flag = ('.' not in field.data or '@' not in field.data)
        if flag:
            raise ValidationError(self.message)

class MyForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email(message='Field must be an email address.')])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=8, message='Password must has at least 8 characters')])
    submit = SubmitField(label='Submit')

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''


app = Flask(__name__)
app.secret_key = "I love you!!"
bootstrap = Bootstrap5(app)

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = MyForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('login.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
