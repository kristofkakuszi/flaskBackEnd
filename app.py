import os
import random
import sqlite3
import string

from flask import Flask, send_from_directory, request, jsonify, url_for, redirect
from flask_login import LoginManager, UserMixin
from flask_login import login_user, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from forms import LoginForm

UPLOAD_FOLDER = 'uploads'
#ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager(app)

app.config['SECRET_KEY'] = 'plsWork'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'hello'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return '<User %r>' % self.username

class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    #data = db.Column(db.LargeBinary)
    fp = db.Column(db.String(264), unique=True)

#db.create_all()
#db.session.commit()


@app.route('/', methods=['GET']) #index
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/login') #loginSite
def login():
    return send_from_directory('templates', 'index.html')


@app.route('/onLogin', methods=['POST']) #loginPost
def login_post():

    #ezek tuti kellenek
    log_object = request.get_json()
    username = log_object['username']
    password = log_object['password']

    user = User.query.filter_by(username=username).first()

    #ide kell egy fgv ami megnezi a user valt segitsegevel hogy benne van-e + hash check

    if not user:
        return jsonify({'result': "nincs ilyen felhasználó"})



    """
    form = LoginForm()
    if form.validate_on_submit():
        conn = sqlite3.connect('app.db')
        curs = conn.cursor()
        curs.execute("SELECT * FROM user where username = (?)",)
        user = list(curs.fetchone())
        Us = load_user(user[0])


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
"""
    if(): #ha a login okes -> gen token

        length_of_string = 128

        letters_and_digits = string.ascii_lowercase + string.digits
        token = ""

        for number in range(length_of_string):
            token += random.choice(letters_and_digits)
        #print(token)


        token = User(token=token)
        user = User.query.filter_by(username=username).first()
        db.session.add(token)
        db.session.commit()
        return jsonify({'result': token})
"""

@app.route('/register') #registerSite
def register():
    return send_from_directory('templates', 'index.html')

@app.route('/onRegister', methods=['GET','POST']) #registerPost
def new_user():
    # username = request.get_json('username')
    reg_object = request.get_json()
    username = reg_object['username']
    password = reg_object['inpPassword']

    signup = User(username=username, password=generate_password_hash(password, method='sha256'))

    user = User.query.filter_by(username=username).first()
    if user:
        print("letezik ilyen")
        return redirect(url_for('register'))                                     # nem mukodik viszont ez miatt nem megy at loginra
        #return jsonify({'result': "sikeres reg"})
    else:
        db.session.add(signup)
        db.session.commit()
    return jsonify({'result': "sikeres reg"})

@app.route('/landing') #landingSite
def landing():
    # landing sitehoz kell majd egy logout gomb is, meg talan hogy hi %aki benne van%
    return send_from_directory('templates', 'index.html')

@app.route('/onUpload', methods=['POST']) #upload
def upload():

    file = request.files['thumbnail']
    #text = request.form['name']

    # ezzel azt cisnalja h elmentei azzal a nevvel csak kiterjesztes nelkul de ha a vegere odairok .jpg-t akkor okes
    #filename = text + ".jpg"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    newFile = Images(name=file.filename, fp=os.path.abspath(UPLOAD_FOLDER))
    db.session.add(newFile)
    db.session.commit()
    #return jsonify({'result': "kepfeltoltes"})


#@app.route('/logout')                                                  #token off
#def logout():
    #return send_from_directory('templates', 'index.html')
    #a db-bol a userhez tartozo tokent azt nullazom eloszor is megnezem hogy a logoutnal megkapom-e a tokent ha a token egyezik (benne van a db-be) akkor nullazom



@app.route('/<path:filename>', methods=['GET']) #fajlok betolteseere szolgal
def send_path(filename):
    return send_from_directory('templates', filename)


if __name__ == '__main__':
    app.run()
