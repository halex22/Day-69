import sqlalchemy as sa
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(length=25), nullable=False)
    email = sa.Column(sa.String(length=50), nullable=False, unique=True)
    password = sa.Column(sa.String(length=20), nullable=False)

    def __init__(self, name:str, email:str, password:str):
        self.name = name,
        self.email = email,
        self.password = self.create_password()

    def __repr__(self) -> str:
        return f"{self.name}"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def create_password(self):
        return generate_password_hash(password=self.password, salt_length=8)
    



class User(UserMixin, db.Model):

    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(length=25), nullable=False)
    email = sa.Column(sa.String(length=50), nullable=False, unique=True)
    password = sa.Column(sa.String(length=20), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self) -> str:
        return f"{self.name}"