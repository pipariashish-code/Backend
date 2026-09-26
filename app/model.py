from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    school = db.Column(db.String(120), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    state = db.Column(db.String(80), nullable=True)
    password = db.Column(db.String(200), nullable=False)
    # role = db.Column(db.String(20), default="user")
    # college_id = db.Column(db.String(80), nullable=True)
    # college_id_proof = db.Column(db.String(120), nullable=True)
    # resume = db.Column(db.String(120), nullable=True)

