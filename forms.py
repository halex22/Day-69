from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class CreateUser(FlaskForm):
    name = StringField("User's name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    passord = PasswordField("User's Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginUser(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("User's Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class CreateComment(FlaskForm):
    body = CKEditorField("Add comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")

class example:
    def __init__(self) -> None:
        pass