import os
import random
import sqlite3
import string

import passlib
from flask import Flask, send_from_directory, request, jsonify, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
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

manager = Manager(app)
manager.add_command('db', MigrateCommand)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))
    pictures = db.relationship('Images', backref='owner', lazy=True) #lehet lazy nem is kell

    #one to many relationship egy usernek lehet több képe

    def __repr__(self):
        return '<User %r>' % self.username

    def verify_password(self, password):
        return check_password_hash(password, self.password)

class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    #data = db.Column(db.LargeBinary)
    fp = db.Column(db.String(264), unique=True)
    #vmi = db.Column(db.valamiTipus, db.ForeignKey('user.id vagy token'), nullable=False) #lehet nullable nem is kell
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # lehet nullable nem is kell

    #ugy kell lekerni a kepeket hogy user szerint? marmint ha logged és ha van a usernek képe lekerjük

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

    log_object = request.get_json() #ez biztos kell
    username = log_object['username']
    password = log_object['password']

    #form = LoginForm()
    #username = form.username.data
    #password = form.password.data
    #if form.validate_on_submit():

    user = User.query.filter_by(username=username).first()

    #if user and user.verify_password(password):
    if user :
        # ha a password megegyezik a db user passwordjával (ami hashes) akkor sikeres login
        print("van ilyen felhasználó")
        #login_user(user)

        # valami miatt hibát dob
    else:
        print("nincs ilyen felhasználó vagy nem jól írtál be valamit")
        return redirect(url_for('login')) #ez miatt nem megy át
       #return jsonify({'result': "nincs ilyen felhasználó"})



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
        return redirect(url_for('register')) # nem mukodik viszont ez miatt nem megy at loginra
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
