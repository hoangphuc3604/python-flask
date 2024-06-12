from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
import smtplib

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

ckeditor = CKEditor()
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor.init_app(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

class BlogPostForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    subtitle = StringField(label='Subtitile', validators=[DataRequired()])
    author = StringField(label='Your name', validators=[DataRequired()])
    img_url = StringField(label='URL of post IMG', validators=[DataRequired(), URL()])
    body = CKEditorField(label='Your blog content', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

with app.app_context():
    db.create_all()

# EMAIL CONFIG
user = "lequydonphuninhquangnam@gmail.com"
password = "hblfjqjfvlytsojk"


@app.route('/')
def get_all_posts():
    posts = []
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=posts)

@app.route('/post/<int:post_id>')
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)

@app.route('/new-post', methods=["GET", "POST"])
def add_new_post():
    form = BlogPostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=form.author.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, is_edit=False)

@app.route('/edit-post/<int:post_id>', methods=["GET", "POST"])
def edit_post(post_id):
    form = BlogPostForm()
    post = db.get_or_404(BlogPost, post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.body = form.body.data
        post.img_url = form.img_url.data
        post.author = form.author.data
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    edit_form = BlogPostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    return render_template('make-post.html', form=edit_form, is_edit=True)

@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template("contact.html", header="Contact Me")
    else:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(user=user, password=password)
            smtp.sendmail(from_addr=request.form['email'],
                          to_addrs="hoangphuc3604@gmail.com",
                          msg="Subject:Contact\n\n" + request.form['message'])
        return render_template("contact.html", header="Successfully sent your message!!")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
