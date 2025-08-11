from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/flaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'  # Needed for Flask sessions

db = SQLAlchemy(app)
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static/uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB limit
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# User table (for demo content)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

# Admin table
class AdminUser(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

# Secure Flask-Admin view
class SecureModelView(ModelView):
    def is_accessible(self):
        return session.get("admin_logged_in")
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login"))

# Custom AdminIndexView with login/logout in template
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return session.get("admin_logged_in")
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login"))

# Home page
@app.route("/")
def home():
    banner = Banner.query.first()
    users = User.query.all()
    return render_template("index.html", users=users, banner=banner)

# Add user form
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/")
    return render_template("add_user.html")

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        admin_user = AdminUser.query.filter_by(username=username).first()
        if admin_user and check_password_hash(admin_user.password_hash, password):
            session["admin_logged_in"] = True
            return redirect("/admin")
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# Register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if AdminUser.query.filter_by(username=username).first():
            return render_template("register.html", error="Username already exists")

        hashed_password = generate_password_hash(password)
        new_admin = AdminUser(username=username, password_hash=hashed_password)
        db.session.add(new_admin)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

# Logout route
@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("login"))


class Banner(db.Model):
    __tablename__ = 'banners'
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)  # stores path like 'uploads/image.jpg'
    heading = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text)
    button_text = db.Column(db.String(100))
    button_link = db.Column(db.String(255))

from flask_admin.form import FileUploadField
from werkzeug.utils import secure_filename
from wtforms import validators
class BannerAdmin(ModelView):
    form_overrides = {
        'image_url': FileUploadField
    }
    
    form_args = {
        'image_url': {
            'label': 'Banner Image',
            'base_path': UPLOAD_FOLDER,
            'allow_overwrite': False,
            'validators': [validators.DataRequired()]
        }
    }

    def _list_thumbnail(view, context, model, name):
        if not model.image_url:
            return ''
        return f'<img src="/static/uploads/{model.image_url}" style="max-height: 100px;">'

    column_formatters = {
        'image_url': _list_thumbnail
    }
    column_formatters_detail = column_formatters




# Flask-Admin setup
admin_panel = Admin(
    app,
    name="Admin Panel",
    template_mode="bootstrap3",
    index_view=MyAdminIndexView(template="admin/index.html")  # Custom template
)
admin_panel.add_view(SecureModelView(User, db.session))
admin_panel.add_view(BannerAdmin(Banner, db.session))
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
