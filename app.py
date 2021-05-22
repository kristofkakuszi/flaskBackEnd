import io
import os
import time
import uuid
import zipfile
from zipfile import ZipFile

from flask import Flask, send_from_directory, request, jsonify, make_response
from flask_login import UserMixin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

#importált modulok
from textRecognition.textDemo import findText
from faceDetection.faceDemo import findFace
from carPlateRecognition.plateDemo import findPlate

UPLOAD_FOLDER = 'uploads'

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
            tokens.pop(token)
            return False
    else:
        return False

def get_all_file_paths(directory):

	# initializing empty file paths list
	file_paths = []

	# crawling through directory and subdirectories
	for root, directories, files in os.walk(directory):
		for filename in files:
			# join the two strings in order to form the full filepath.
			filepath = os.path.join(root, filename)
			file_paths.append(filepath)

	# returning all file paths
	return file_paths

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))
    pictures = db.relationship('Images', backref='owner', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username

    def verify_password(self, password):
        return check_password_hash(self.password, password)

class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    fp = db.Column(db.String(264))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    faceFound = db.Column(db.Boolean, default=False)
    textFound = db.Column(db.Boolean, default=False)
    plateFound = db.Column(db.Boolean, default=False)
    nothingFound = db.Column(db.Boolean, default=False)


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
def landing():
    token = request.headers.get('auth-token')

    if not token:
        print("nincs token szoval nincs feltotltes")
        return {"message": "Sikertelen"}, 401
    else:
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
        print("user id-ja: " + str(user.id))
        print(tokens)

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

    if verifyToken(token):

        info = tokens[token]
        print(info)
        user = info['user']
        print("bejelentkezett felhasznalo neve: " + str(user))

        file = request.files['thumbnail']

        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(user.id))
        os.makedirs(user_dir, exist_ok=True)

        image_path = os.path.join(user_dir, str(uuid.uuid4()) + "." + str(file.filename).split(".")[-1])
        print("kep eleresi utvonala: " + str(image_path))
        print("mappa ahova mennek: " + str(user_dir))

        file.save(image_path)

        hasText = findText(image_path)
        hasFace = findFace(image_path)
        hasPlate = findPlate(image_path)
        hasNothing = findFace(image_path) is False and findText(image_path) is False and findPlate(image_path) is False

        getFacesFrom = Images.query.filter_by(owner_id=user.id, faceFound=True).all()  # ezek listak lesznek
        getTextFrom = Images.query.filter_by(owner_id=user.id, textFound=True).all()
        getPlateFrom = Images.query.filter_by(owner_id=user.id, plateFound=True).all()
        getNothingFrom = Images.query.filter_by(owner_id=user.id, faceFound=False, textFound=False, plateFound=False).all()

        print("ezeken a kepeken talalt arcot: " + str(getFacesFrom))
        print("ezeken a kepeken talalt szoveget: " + str(getTextFrom))
        print("ezeken a kepeken talalt rendszamot: " + str(getPlateFrom))
        print("ezeken a kepeken semmit nem talalt: " + str(getNothingFrom))

        if (hasText or hasFace or hasPlate):
            newFile = Images(name=file.filename, fp=os.path.relpath(image_path), owner_id=user.id, faceFound=hasFace, textFound=hasText, plateFound=hasPlate, nothingFound=hasNothing)
            print(hasNothing)
            db.session.add(newFile)
            db.session.commit()
            return {"message": "sikeres "}, 200

        elif (hasText is False and hasFace is False and hasPlate is False):
            anotherFile = Images(name=file.filename, fp=os.path.relpath(image_path), owner_id=user.id, faceFound=False, textFound=False, plateFound=False,  nothingFound=True)
            print(hasNothing)
            db.session.add(anotherFile)
            db.session.commit()
            return {"message": "sikeres "}, 200
        else:
            return {"message": "sikertelen "}, 401


@app.route("/getImages",methods = ['GET'])
def get_images():

    token = request.headers.get('auth-token')
    print(token)
    if verifyToken(token):
        info = tokens[token]
        #print(info)
        #print(token)
        user = info['user']
        images = Images.query.filter_by(owner_id=user.id).all()
        #getNothingFrom = Images.query.filter_by(owner_id=user.id, faceFound=False, textFound=False, plateFound=False).all()
        images_alt = []
        for image in images:
            i = {}
            i["id"] = image.id
            i["name"] = image.name
            i["fp"] = image.fp
            i["owner_id"] = image.owner_id
            i["faceFound"] = image.faceFound
            i["textFound"] = image.textFound
            i["plateFound"] = image.plateFound
            i["nothingFound"] = image.nothingFound
            images_alt.append(i)
        return jsonify({
            'result' : images_alt
        }), 200
    else:
        return {"message": "Sikertelen"}, 401


@app.route('/getImage', methods=['GET'])
def get_image():
    id = request.args.get("id")
    token = request.args.get("token")
    if verifyToken(token):
        info = tokens[token]
        print(info)
        user = info['user']
        image = Images.query.filter_by(owner_id=user.id, id=id).first()
        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(user.id))
        file_name = image.fp.split("\\")[-1]
        print(user_dir)
        print(file_name)
        return send_from_directory(user_dir, filename=file_name)
    else:
        return {"message" : "Sikertelen"}, 401


@app.route('/onLogout', methods=['POST'])
def logout():
    token = request.headers.get('auth-token')
    tokens.pop(token)


@app.route('/downloadImages', methods=['POST'])
def download(imageList):

#megkapom a listat
#listaban benne lesznek a kepek
# akkor ezeknek lekerem az id-jat, és fp-jat egy valtozoba
#ezeken filter byal id alapjan rendezni


    token = request.headers.get('auth-token')

    if verifyToken(token):
        info = tokens[token]
        print(info)
        user = info['user']

       # selectedImages = Images.query.filter_by(owner_id=user.id, id= ,fp= )

        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(user.id))
        #user_dir amhol vannak a mappák

    directory = './vmi'

    file_paths = get_all_file_paths(directory)

    # printing the list of all files to be zipped
    print('Following files will be zipped:')
    for file_name in file_paths:
        print(file_name)

    # writing files to a zipfile
    with ZipFile('pictures.zip', 'w') as zip:
        # writing each file one by one
        for file in file_paths:
            zip.write(file)

    print('All files zipped successfully!')

"""
    dow_object = request.get_json()
    downloadList = dow_object['dow_object']
    print(type(downloadList))
    return jsonify({'succes' : 'result'})
#return send_from_directory(user_dir,"pictures.zip",as_attachment=True)
"""




if __name__ == '__main__':
    app.run()