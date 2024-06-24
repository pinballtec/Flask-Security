from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, roles_required
from flask_security.utils import hash_password, verify_password
from flask_security.forms import RegisterForm
from flask_migrate import Migrate
from flask_babel import Babel
from wtforms import StringField
import uuid
from flask_wtf import CSRFProtect
from flask_login import login_user
import os

# Initialize Flask application
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'postgresql://user:password@db:5432/mydatabase')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey')
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT', 'somesalt')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_RECOVERABLE'] = True  # Enable password recovery
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
app.config['WTF_CSRF_ENABLED'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
babel = Babel(app)
csrf = CSRFProtect(app)

# Define the association table for many-to-many relationship between users and roles
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


# Define Role model
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


# Define User model
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


# Initialize Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone = StringField('Phone Number')


# Define extended registration form
@app.route('/')
@login_required
def index() -> str:
    """Home page accessible only to logged in users."""
    return 'Home Page'


@app.route('/admin')
@roles_required('admin')
def admin() -> str:
    """Admin page accessible only to users with 'admin' role."""
    users = User.query.all()
    return render_template('admin.html', users=users)


@app.route('/admin/deactivate/<int:user_id>', methods=['POST'])
@roles_required('admin')
def deactivate_user(user_id):
    """Deactivate a user account by setting 'active' to False."""
    user = User.query.get(user_id)
    if user:
        user.active = False
        db.session.commit()
        return jsonify({"message": "User deactivated successfully."}), 200
    return jsonify({"message": "User not found."}), 40


@app.route('/admin/change_role/<int:user_id>/<role_name>', methods=['POST'])
@roles_required('admin')
def change_user_role(user_id, role_name):
    """Change the role of a user."""
    user = User.query.get(user_id)
    if user:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db.session.add(role)
            db.session.commit()
        user.roles.append(role)
        db.session.commit()
        return jsonify({"message": "User role updated successfully."}), 200
    return jsonify({"message": "User not found."}), 404


@app.route('/admin/delete_user/<int:user_id>', methods=['DELETE'])
@roles_required('admin')
def delete_user(user_id):
    """Delete a user from the database."""
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully."}), 200
    return jsonify({"message": "User not found."}), 404


@app.route('/admin/users', methods=['GET'])
# @roles_required('admin')
def get_users():
    """Get a list of all users."""
    users = User.query.all()
    users_list = [{
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'active': user.active,
        'roles': [role.name for role in user.roles]
    } for user in users]
    return jsonify(users_list), 200


@app.route('/reset_password', methods=['POST'])
@csrf.exempt
def reset_password():
    """Reset the password for a user."""
    data = request.json
    email = data.get('email')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    user = User.query.filter_by(email=email).first()
    if user:
        if verify_password(old_password, user.password):
            user.password = hash_password(new_password)
            db.session.commit()
            return jsonify({"message": "Password updated successfully."}), 200
        else:
            return jsonify({"message": "Old password is incorrect."}), 400
    else:
        return jsonify({"message": "User not found."}), 404


@app.route('/register', methods=['POST'])
@csrf.exempt
def register():
    """Register a new user."""
    data = request.json
    form = ExtendedRegisterForm(data=data)
    if form.validate_on_submit():
        user = user_datastore.create_user(
            email=form.email.data,
            password=hash_password(form.password.data),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data
        )
        role = Role.query.filter_by(name='user').first()
        if not role:
            role = Role(name='user')
            db.session.add(role)
            db.session.commit()
        user.roles.append(role)
        db.session.commit()
        return jsonify({"message": "User registered successfully."}), 200
    return jsonify({"errors": form.errors}), 400


@app.route('/signin', methods=['POST'])
@csrf.exempt
def signin():
    """Sign in an existing user."""
    data = request.json
    user = User.query.filter_by(email=data.get('email')).first()
    if user:
        if verify_password(data.get('password'), user.password):
            # Role check
            if not user.roles:
                role = Role.query.filter_by(name='user').first()
                if not role:
                    role = Role(name='user')
                    db.session.add(role)
                    db.session.commit()
                user.roles.append(role)
                db.session.commit()
            login_user(user)
            return jsonify({"message": "User logged in successfully."}), 200
        else:
            return jsonify({"message": "Wrong password."}), 400
    else:
        return jsonify({"message": "User doesn't exist."}), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

# TODO: 1) Tests update 2) Maybe frontend 3) CI\CD setup Maybe # 5) REadme
