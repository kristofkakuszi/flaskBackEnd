import os
import time
import uuid

from flask import Flask, send_from_directory, request, jsonify
from flask_login import UserMixin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from textRecognition.textDemo import findText
from faceDetection.faceDemo import findFace
from carPlateRecognition.plateDemo import findPlate

UPLOAD_FOLDER = 'uploads' #ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

expire_time = 1 * 24 * 60 * 60
tokens = {}


app.config['SECRET_KEY'] = 'plsWork'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'hello'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


def verifyToken(token):
    info = tokens[token]
    if info:
        if info['expire'] > time.time():
            return True
        else:
            tokens.pop(token) #ha lejárt kitörlöm a dictionarybol
            return False
    else:
        return False


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))
    pictures = db.relationship('Images', backref='owner', lazy=True)
    #one to many relationship egy usernek lehet több képe

    def __repr__(self):
        return '<User %r>' % self.username

    def verify_password(self, password):
        return check_password_hash(self.password, password)


class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    #data = db.Column(db.LargeBinary)
    fp = db.Column(db.String(264))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # lehet nullable nem is kell
    #ugy kell lekerni a kepeket hogy user szerint? marmint ha logged és ha van a usernek képe lekerjük


@app.route('/', methods=['GET'])
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/login')
def login():
    return send_from_directory('templates', 'index.html')

@app.route('/register')
def register():
    return send_from_directory('templates', 'index.html')

@app.route('/landing')
def landing(): #talan hogy hi %aki benne van%
    return send_from_directory('templates', 'index.html')

@app.route('/<path:filename>', methods=['GET'])
def send_path(filename):#fajlok betolteseere szolgal
    return send_from_directory('templates', filename)


@app.route('/onLogin', methods=['POST'])
def login_post():

    log_object = request.get_json()
    username = log_object['username']
    password = log_object['password']

    user = User.query.filter_by(username=username).first()

    if user and user.verify_password(password):
        token = str(uuid.uuid4())
        tokens[token] = {
            'user' : user,
            'expire' :  time.time() + expire_time,
            'token' : token
        }
        print(tokens[token])
        info = tokens[token]
        user = info['user']
        print(type(token))
        print(user)

        return jsonify({
            'result': True,
            'token': token
        }), 200
    else:
        print("nincs ilyen felh")
        return {"message": "Invalid username or password"}, 401 # nincs jogosultsága nem azonosította magát


@app.route('/onRegister', methods=['POST'])
def new_user():

    reg_object = request.get_json()
    username = reg_object['username']
    password = reg_object['inpPassword']

    signup = User(username=username, password=generate_password_hash(password, method='sha256'))

    user = User.query.filter_by(username=username).first()
    if user:
        print("letezik ilyen")
        return {"message": "Invalid username or password"}, 401
    else:
        db.session.add(signup)
        db.session.commit()
        return {"message": "sikeres reg"}, 200


@app.route('/onUpload', methods=['POST'])
def upload():

    token = request.headers.get('auth-token')
    print(token)
    if verifyToken(token):

        info = tokens[token]
        print(info)
        user = info['user'] #ezzel tudom ki tolti fel a képet
        print(user)

        file = request.files['thumbnail']

        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename) #kulon valtozoba rakom az eleresi utvonalat
        file.save(image_path)


        print(findFace(image_path))
        print(findText(image_path))
        print(findPlate(image_path))

        newFile = Images(name=file.filename, fp=os.path.abspath(UPLOAD_FOLDER),owner_id=user.id) #),owner_id=user.id)
        db.session.add(newFile)
        db.session.commit()
        #return jsonify({'result': "kepfeltoltes"})
        return {"message": "done"}, 200 # lement a kérés
    else:
        return {"message": "hiba"}, 401


@app.route("/getImage/<path:image_name>",methods = ['GET','POST']) # fájl visszaadása, ide a fájlba kell majd egy dictionaryt adni? egy másik fgv segítségével
def get_image(image_name):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename=image_name, as_attachment=True)


@app.route('/onLogout', methods=['POST'])
def logout():
    token = request.headers.get('auth-token')
    tokens.pop(token)
    print("flask oldalon login utan a token" + token)

if __name__ == '__main__':
    app.run()