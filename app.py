from flask import Flask, send_from_directory, request, jsonify, url_for, redirect, flash, session
from flask_login import LoginManager, UserMixin, login_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from passlib.apps import custom_app_context as pwd_context
from flask import Blueprint
from sqlalchemy import engine
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
#from app import login
from werkzeug.urls import url_parse


app = Flask(__name__)
login = LoginManager(app)
login.login_view = 'login'

app.config['SECRET_KEY'] = 'plsWork'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'hello'

db = SQLAlchemy(app)
#migrate = Migrate(app, db)


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))


db.create_all()
db.session.commit()

"""
db.init_app(app)                                                    #ez kell?
login_manager = LoginManager(app)
login_manager.init_app(app)
"""


@login.user_loader                                          #ez kell?
#def load_user(user_id):
def load_user(id):
    return User.query.get(int(id))
    #return User.get(user_id)
    #return User.query.get(int(user_id))


@app.route('/', methods=['GET'])                                        #betolteshezKell meg amugy index
def index():
    return send_from_directory('templates', 'index.html')


@app.route('/login')                                                    #loginSite
def login():
    return send_from_directory('templates', 'index.html')


@app.route('/onLogin', methods=['GET', 'POST'])                         #loginPost
def login_post():

    #form = LoginForm()
    #if form.validate_on_submit():
    #    login_user(user)
    #    flask.flash('Logged in successfully.')
    #    next = flask.request.args.get('next')



    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        #user = User.query.filter_by(username=username).first()
        #if not user or not check_password_hash(user.password, password):
        #if user is None or not check_password_hash(user.password, password):
        if user is None or not user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            print("nem jok az adatok")
        else:
            print("jok az adatok")

    #login_user(user)


    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = find_user(username)

        if user and password == user.password:
            #return redirect("landing")
        else:
            flash("incorrect username or password.")
            #return redirect("login")
    """


@app.route('/register')                                                 #registerSite
def register():
    return send_from_directory('templates', 'index.html')


@app.route('/onRegister', methods=['GET','POST'])                             #registerPost
def new_user():

    reg_object = request.get_json()
    username = reg_object['username']
    password = reg_object['inpPassword']

    #username = request.get_json('username')
    #password = request.get_json('inpPassword')
    #print(username)
    #print(password)

    signup = User(username=username, password=generate_password_hash(password, method='sha256'))

    #if reg_object['username'] == db.session.quer(User).filter(User.username.data.strip()).first():
    #   return jsonify({'result': "mar letezik"})
    #"SELECT username from User"
    #c= conn.cursor()
    #c.execute()
    #cursor.fetchall()


    user = User.query.filter_by(username=username).first()
    if user:
        print("letezik ilyen")
        #flash("User already exists", "warning")
        return redirect(url_for('login'))                                     # nem mukodik
    else:
        db.session.add(signup)
        db.session.commit()

    return jsonify({'result': "ok"})


"""landing sitehoz kell majd egy logout gomb is, meg talan hogy hi %aki benne van%"""
@app.route('/landing')                                                  #landingSite    -   @login.required?
def landing():
    return send_from_directory('templates', 'index.html')


#@app.route('/upload')                                                  #upload
#def upload():
#    file = request.files['inputFile']
#    return file.filename


#@app.route('/logout')                                                  #MAJD KELL logoutSite - upd dehogy kell -> redirect
#def logout():
    #return redirect(url_for('/'))
    #return send_from_directory('templates', 'index.html')


@app.route('/<path:filename>', methods=['GET'])                         #fajlok betolteseere szolgal
def send_path(filename):
    return send_from_directory('templates', filename)


if __name__ == '__main__':
    app.run()
