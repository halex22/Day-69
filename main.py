from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, CreateUser, LoginUser, CreateComment
from flask_gravatar import Gravatar
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from functools import wraps


login_manager = LoginManager()
db = SQLAlchemy()
app = Flask(__name__)

##CONNECT TO DB
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize 
gravatar = Gravatar(app=app, size=100, rating="g", default="retro",
                    force_default=False, force_lower=False, use_ssl=False, base_url=None)
ckeditor = CKEditor(app)
db.init_app(app)
login_manager.init_app(app)
Bootstrap(app)


##CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name = sa.Column(sa.String(length=25), nullable=False)
    email = sa.Column(sa.String(length=50), nullable=False, unique=True)
    password = sa.Column(sa.String(length=20), nullable=False)
    posts: Mapped[list["BlogPost"]] = relationship(back_populates="author")
    comments: Mapped[list["Comment"]] = relationship(back_populates="comment_author")

    def __repr__(self) -> str:
        return f"{self.name}"
    

class BlogPost(db.Model):
    __tablename__ = "blog_posts_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(sa.ForeignKey("users_table.id"))
    author: Mapped["User"] = relationship(back_populates="posts")
    title = sa.Column(sa.String(250), unique=True, nullable=False)
    subtitle = sa.Column(sa.String(250), nullable=False)
    date = sa.Column(sa.String(250), nullable=False)
    body = sa.Column(sa.Text, nullable=False)
    img_url = sa.Column(sa.String(250), nullable=False)
    post_comments: Mapped[list["Comment"]] = relationship(back_populates="parent_post")

    def __repr__(self) -> str:
        return f"{self.title}"


class Comment(db.Model):
    __tablename__ = "comments_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(sa.ForeignKey("users_table.id"))
    comment_author: Mapped["User"] = relationship(back_populates="comments")
    post_id: Mapped[int] = mapped_column(sa.ForeignKey("blog_posts_table.id"))
    parent_post: Mapped["BlogPost"] = relationship(back_populates="post_comments")
    body = sa.Column(sa.Text, nullable=False)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).filter_by(id=user_id)).scalar()


def admin_only(funct):
    @wraps(funct)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(code=403)
        return funct(*args, **kwargs)
    return decorated_function


@app.route('/')
def get_all_posts():
    posts = db.session.execute(db.select(BlogPost)).scalars()
    return render_template("index.html", all_posts=posts, logged_in=current_user.is_authenticated)


@app.route("/register", methods=["POST","GET"])
def register():
    form = CreateUser()
    if request.method == "POST":
        if form.validate_on_submit():           
            user = db.session.execute(db.select(User).filter_by(email=form.email.data)).scalar()
            if user: 
                flash("Email already registered")
                return redirect(url_for("login"))
            else:
                user = User(name=form.name.data, email=form.email.data,
                            password=generate_password_hash(form.passord.data, salt_length=8))
                db.session.add(user)
                db.session.commit()
                login_user(user)
                flash(f"Hello {form.name.data} ! thanks for signing in.")
                return redirect(url_for("get_all_posts"))
    else:
        return render_template("register.html", form=form)


@app.route('/login', methods=["POST", "GET"])
def login():
    error = None
    form = LoginUser()
    if request.method == "POST":
        if form.validate_on_submit():      
            user = db.session.execute(db.select(User).filter_by(email= form.email.data)).scalar()
            if user:
                if check_password_hash(pwhash=user.password, password= form.password.data):
                    login_user(user)
                    flash("You were successfully logged in")
                    return redirect(url_for("get_all_posts"))
                else:
                    error = "Wrong Password"
                    return redirect(url_for("login", error=error) )
            else:
                error = "User not found, please check what you wrote"

    else:
        return render_template("login.html", form=form, error=error)


@app.route("/post/<int:post_id>", methods=["POST", "GET"])
def show_post(post_id):
    form = CreateComment()
    if request.method == "POST":
        if form.validate_on_submit():
            new_comment = Comment(body=form.body.data,
                                  author_id=current_user.id,
                                  post_id=post_id)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for("show_post", post_id=new_comment.post_id))
    requested_post = db.get_or_404(entity=BlogPost, ident=post_id)
    return render_template("post.html", post=requested_post,
                           logged_in=current_user.is_authenticated, form=form)


@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    if request.method == "POST":
        if form.validate_on_submit():
            new_post = BlogPost(title=form.title.data, subtitle=form.subtitle.data,
                body=form.body.data, img_url=form.img_url.data, author=current_user,
                date=date.today().strftime("%B %d, %Y"))
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):

    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if request.method == "POST":
        if edit_form.validate_on_submit():
            post.title = edit_form.title.data
            post.subtitle = edit_form.subtitle.data
            post.img_url = edit_form.img_url.data
            post.body = edit_form.body.data
            db.session.commit()
            return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(entity=BlogPost, ident=post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("get_all_posts"))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
