from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, ValidationError
from flask_ckeditor import CKEditorField, CKEditor

ckeditor = CKEditor()

# WTForm for creating a blog post
class BlogPostForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    subtitle = StringField(label='Subtitile', validators=[DataRequired()])
    img_url = StringField(label='URL of post IMG', validators=[DataRequired(), URL()])
    body = CKEditorField(label='Your blog content', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

class Email(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if '@' not in field.data or '.' not in field.data:
            raise ValidationError(self.message or 'Invalid email address.')
        
class Length(object):
    def __init__(self, min=-1, max=-1, message=None):
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, form, field):
        if self.min != -1 and len(field.data) < self.min:
            raise ValidationError(self.message or f'Field must be at least {self.min} characters long.')
        if self.max != -1 and len(field.data) > self.max:
            raise ValidationError(self.message or f'Field must be at most {self.max} characters long.')

class RegisterForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email(message='Invalid email address.')])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=8, message='Password must be at least 8 characters long.')])
    name = StringField(label='Name', validators=[DataRequired()])
    avatar_img = StringField("Avatar URL (Not required)", validators=[])
    submit = SubmitField(label='Sign me up!')

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email(message='Invalid email address.')])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=8, message='Password must be at least 8 characters long.')])
    submit = SubmitField(label='Log me in!')

class CommentForm(FlaskForm):
    comment = StringField(label='Your comment', validators=[DataRequired()])
    submit = SubmitField(label='Submit')