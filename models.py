from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Banner(db.Model):
    __tablename__ = 'banners'
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    heading = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text)
    button_text = db.Column(db.String(100))
    button_link = db.Column(db.String(255))
