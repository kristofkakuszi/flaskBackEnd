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

expire_time = 10 * 60
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
            print(info['expire'])
            return True
        else:
            print("kiment a token")
            print(type(expire_time))
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
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    faceFound = db.Column(db.Boolean, default=False)
    textFound = db.Column(db.Boolean, default=False)
    plateFound = db.Column(db.Boolean, default=False)



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
        #print(tokens[token])
        #info = tokens[token]
        #user = info['user']
        #print(type(token))
        #print(user)
        print("user id-ja: " + str(user.id))

        userImages = Images.query.filter_by(owner_id=user.id).all()
        print(userImages)

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

    if not token:
        print("nincs token szoval nincs feltotltes")
        return {"message": "Sikertelen"}, 401

    #print(token)
    if verifyToken(token):

        info = tokens[token]
        print(info)
        user = info['user'] #ezzel tudom ki tolti fel a képet
        print("felhasznalo neve: " + str(user))

        file = request.files['thumbnail']

        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(user.id))
        os.makedirs(user_dir, exist_ok=True)

        image_path = os.path.join(user_dir, str(uuid.uuid4()) + "." + str(file.filename).split(".")[-1]) #kulon valtozoba rakom az eleresi utvonalat
        print("kep eleresi utvonala: " + str(image_path))
        file.save(image_path)

        hasText = findText(image_path)
        hasFace = findFace(image_path)
        hasPlate = findPlate(image_path)

        if (hasText or hasFace or hasPlate):
            newFile = Images(name=file.filename, fp=os.path.abspath(image_path), owner_id=user.id, faceFound=hasFace, textFound=hasText, plateFound=hasPlate)
            db.session.add(newFile)
            db.session.commit()
            return {"message": "sikeres "}, 200
        else:
            return {"message": "sikertelen "}, 401



@app.route("/getImages/<path:image_name>",methods = ['POST'])
def get_image(image_name):

    #userImages = {}

    token = request.headers.get('auth-token')
    if verifyToken(token):
        info = tokens[token]
        print(info)
        user = info['user'] #kiolvasom a usert
        #print(user.id)  #user id
        #userImages = Images.query.all(owner_id = user.id)

        userImages = Images.query.filter_by(owner_id = user.id).all() # a userhez tartozo osszes kep viszont ezeknek az eleresi utvonala kell majd es ezt viszem tovabb

        # ez a userImages egy lista lesz, előtte kell deklaráljam nem?
        #azt honnan tudom hogy melyik kép arc szöveg rendsz? ezekre lefuttatom ujra a foggvenyeket? -> vagy ha true akkor
        # ugye a dictet bejarjuk uin
        #amikot talal arcokat akkor gyartok az uin linkeket html image tageket aminek megadom az urlt
        #path:image helyere egy image idt irok be es lekerem egy Images.query.filter_by(id=id) de milyen id 51:10

    else:
        return {"message": "Sikertelen"}, 401
        #return send_from_directory(app.config["UPLOAD_FOLDER"], filename=image_name, as_attachment=True)


@app.route('/onLogout', methods=['POST'])
def logout():
    token = request.headers.get('auth-token')
    tokens.pop(token)

if __name__ == '__main__':
    app.run()