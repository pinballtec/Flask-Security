from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, roles_required
from flask_security.forms import RegisterForm
from flask_migrate import Migrate
from flask_babel import Babel
from wtforms import StringField
import uuid
from flask_wtf import CSRFProtect
from flask_security.utils import hash_password, verify_password
from flask_login import login_user

# Create Flask application instance
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/mydatabase'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SECURITY_PASSWORD_SALT'] = 'somesalt'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection
app.config['WTF_CSRF_CHECK_DEFAULT'] = True  # Enable CSRF check by default

# Initialize SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)
babel = Babel(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

# Create user and role datastore
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Forms
class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone = StringField('Phone Number')

# Routes
@app.route('/')
@login_required
def index():
    return 'Home Page'

@app.route('/admin')
@roles_required('admin')
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/admin/deactivate/<int:user_id>')
@roles_required('admin')
def deactivate_user(user_id):
    user = User.query.get(user_id)
    user.active = False
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/change_role/<int:user_id>/<role_name>')
@roles_required('admin')
def change_role(user_id, role_name):
    user = User.query.get(user_id)
    role = Role.query.filter_by(name=role_name).first()
    user.roles.append(role)
    db.session.commit()
    return redirect(url_for('admin'))

# Registration and login routes without CSRF protection
@app.route('/register', methods=['POST'])
@csrf.exempt
def register():
    form = ExtendedRegisterForm(request.json)
    if form.validate_on_submit():
        user = user_datastore.create_user(
            email=form.email.data,
            password=hash_password(form.password.data),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data
        )
        db.session.commit()
        return {"message": "User registered successfully."}, 200
    return {"errors": form.errors}, 400

@app.route('/login', methods=['POST'])
@csrf.exempt
def login():
    data = request.json
    user = User.query.filter_by(email=data.get('email')).first()
    if user and verify_password(data.get('password'), user.password):
        login_user(user)
        return {"message": "User logged in successfully."}, 200
    return {"message": "Invalid credentials."}, 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
