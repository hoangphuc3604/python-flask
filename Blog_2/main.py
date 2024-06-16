from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text
from forms import BlogPostForm, ckeditor, RegisterForm, LoginForm, CommentForm
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user

from datetime import datetime, date
import smtplib


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

#Loggin Manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# CONFIGURE COMMENT TABLE
class Comment(db.Model):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    post = relationship("BlogPost", back_populates="comments")
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="comments")
    date: Mapped[str] = mapped_column(String(250), nullable=False)


# CONFIGURE TABLE
class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    comments = relationship("Comment", back_populates="post")
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

#CONFIGURE USER TABLE
class User(UserMixin ,db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    avatar_img: Mapped[str] = mapped_column(String(250), nullable=False)
    exp: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Integer)

# FOLLOW TABLE
class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),)
    follower = db.relationship("User", foreign_keys=[follower_id])
    followed = db.relationship("User", foreign_keys=[followed_id])

with app.app_context():
    db.create_all()


# EMAIL CONFIG
user = "lequydonphuninhquangnam@gmail.com"
password = "hblfjqjfvlytsojk"

# Create an admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # If id is not 1 then return abort with 403 error
            if current_user.id != 1:
                return abort(403)
            # Otherwise continue with the route function
            return f(*args, **kwargs)
        except AttributeError:
            return abort(403)

    return decorated_function


@app.route('/')
def get_all_posts():
    posts = []
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=posts, logged_in=current_user.is_authenticated)

@app.route('/post/<int:post_id>', methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    current_post = db.get_or_404(BlogPost, post_id)
    if form.validate_on_submit():
        new_comment = Comment (
            text=form.comment.data,
            post=current_post,
            author=current_user,
            date=datetime.today().strftime("%B %d, %Y %I:%M %p")
        )
        db.session.add(new_comment)
        db.session.commit()
        form.comment.data = ""

    comments = db.session.execute(db.select(Comment)).scalars()
    return render_template("post.html", post=current_post, logged_in=current_user.is_authenticated, form=form, comments=comments, current_user=current_user)

@app.route('/new-post', methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = BlogPostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, is_edit=False, logged_in=current_user.is_authenticated)

@app.route('/edit-post/<int:post_id>', methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    form = BlogPostForm()
    post = db.get_or_404(BlogPost, post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.body = form.body.data
        post.img_url = form.img_url.data
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    edit_form = BlogPostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    return render_template('make-post.html', form=edit_form, is_edit=True, logged_in=current_user.is_authenticated)

# DELETE POST
@app.route('/delete/<int:post_id>')
@admin_only
def delete_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

# DELETE COMMENT
@app.route('/delete-comment/<int:comment_id>')
@admin_only
def delete_comment(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template("contact.html", header="Contact Me", logged_in=current_user.is_authenticated)
    else:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(user=user, password=password)
            smtp.sendmail(from_addr=request.form['email'],
                          to_addrs="hoangphuc3604@gmail.com",
                          msg="Subject:Contact\n\n" + request.form['message'])
        return render_template("contact.html", header="Successfully sent your message!!", logged_in=current_user.is_authenticated)


# REGISTER FEATURE
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    existing_user = None
    if form.validate_on_submit():
        existing_user = db.session.execute(db.select(User).where(form.email.data == User.email)).scalars().all()
        if len(existing_user) != 0:
            flash("You've already used this email. Try another instead !!")
        else:
            new_user = User(
                email=form.email.data,
                password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8),
                name=form.name.data,
                avatar_img=form.avatar_img.data or "https://th.bing.com/th/id/R.ed67f16becae2b6600d91217c40de612?rik=QXfa1X0r1AvcKA&pid=ImgRaw&r=0",
                exp=form.exp.data,
                rating=0,
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts'))
    return render_template('register.html', form=form, logged_in=current_user.is_authenticated)

# LOGIN FEATURE
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password=form.password.data

        # Find user by email entered.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()

        if user == None:
            flash("This email does not exist !!")
        else:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash("Wrong password. Try again.")
            
    return render_template('login.html', form=form, logged_in=current_user.is_authenticated)

# LOGOUT FEATURE
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))  

# PROFILE PAGE
@app.route('/profile/<int:user_id>')
def show_profile(user_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    user = db.get_or_404(User, user_id)
    number_of_posts = len(db.session.execute(db.select(BlogPost).where(BlogPost.author_id == user_id)).scalars().all())
    number_of_follower = Follow.query.filter_by(followed_id=user.id).count()

    follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=user.id).first()
    btn_class = ""
    if follow:
        btn_class = "fl"
    else:
        btn_class = "not-fl"

    return render_template('profile.html', user=user, num_fl=number_of_follower, num_post=number_of_posts, logged_in=current_user.is_authenticated, error=None, current_user=current_user, btn_class=btn_class)

def follow_user(follower_user_id, followed_user_id):
    follower = User.query.filter_by(id=follower_user_id).first()
    followed = User.query.filter_by(id=followed_user_id).first()

    if not follower or not followed:
        return {"error": "Follower or followed user not found."}, 404
    
    if follower.id == followed.id:
        return {"error": "User cannot follow themselves."}, 400
    
    follow = Follow.query.filter_by(follower_id=follower.id, followed_id=followed.id).first()  
    if follow:
        return {"error": "User already followed."}, 400
    
    new_follow = Follow (
        follower_id=follower_user_id,
        followed_id=followed_user_id,
    )
    db.session.add(new_follow)
    db.session.commit()

    return {"message": "Follow successful."}, 201

#FOLLOW FEATURE
@app.route('/follow', methods=['POST'])
def follow():
    data = request.get_json()
    follower_id = int(data['follower'])
    followed_id = int(data['followed'])
    
    code, message = follow_user(follower_id, followed_id)
    if code == 404 or code == 400:
        user = db.get_or_404(User, followed_id)
        number_of_posts = len(db.session.execute(db.select(BlogPost).where(BlogPost.author_id == followed_id)).scalars().all())
        number_of_follower = Follow.query.filter_by(followed_id=user.id).count()
        return render_template('profile.html', user=user, num_fl=number_of_follower, num_post=number_of_posts, logged_in=current_user.is_authenticated, error="Cannot follow this person!!")
    else:
        return redirect(url_for('show_profile', user_id=followed_id))
    
#UNFOLLOW FEATURE
@app.route('/unfollow', methods=['POST'])
def unfollow():
    data = request.get_json()
    follower_id = int(data['follower'])
    followed_id = int(data['followed'])

    follower = User.query.filter_by(id=follower_id).first()
    followed = User.query.filter_by(id=followed_id).first()
    follow = Follow.query.filter_by(follower_id=follower.id, followed_id=followed.id).first()
    db.session.delete(follow)
    db.session.commit()
    return redirect(url_for('show_profile', user_id=followed_id))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
