from old_app import db


class User(db.Model):
    __tablename__ = "Users"

    UserID = db.Column(db.Integer, primary_key=True)
    FullName = db.Column(db.String(150), nullable=False)
    Email = db.Column(db.String(150), unique=True, nullable=True)
    PhoneNumber = db.Column(db.String(30), nullable=True)
    PasswordHash = db.Column(db.String(255), nullable=False)
    Role = db.Column(db.String(30), nullable=False)
    IsActive = db.Column(db.Boolean, nullable=False, default=True)