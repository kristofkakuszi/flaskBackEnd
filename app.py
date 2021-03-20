from flask import Flask, send_from_directory, request, jsonify, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from passlib.apps import custom_app_context as pwd_context
from flask import Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
#from flask_login import login_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'plsWork'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
#migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))


db.create_all()
db.session.commit()


@app.route('/', methods=['GET'])                                        #betolteshezKell meg amugy index
def index():
    return send_from_directory('templates', 'index.html')


@app.route('/login')                                                    #loginSite
def login():
    return send_from_directory('templates', 'index.html')


#@app.route('/onLogin', methods=['POST'])                                #loginPost
#def login_post():

#return redirect(url_for('/landing'))


@app.route('/register')                                                 #registerSite
def register():
    return send_from_directory('templates', 'index.html')


@app.route('/onRegister', methods=['POST'])                             #registerPost
def new_user():

    reg_object = request.get_json()
    username = reg_object['username']
    password = reg_object['inpPassword']

    print(username)
    print(password)

    """
    username = request.get_json('username')
    password = request.get_json('inpPassword')
    """

    signup = User(username=username, password=generate_password_hash(password, method='sha256'))
    db.session.add(signup)
    db.session.commit()

    return jsonify({'result': "ok"})

    """
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username}), 201, {'Location': url_for('get_user', id=user.id, _external=True)}
    """

    #return redirect(url_for('/login'))

"""
    json_data = request.json
    user = User(
        username=json_data['username'],
        password=json_data['inpPassword']
    )
    try:
        db.session.add(user)
        db.session.commit()
        status = 'success'
    except:
        status = 'user is already registered'
    db.session.close()
    return jsonify({'result': status})
"""
#


"""landing sitehoz kell majd egy logout gomb is, meg talan hogy hi %aki benne van%"""
@app.route('/landing')                                                  #landingSite    -   @login.required?
def landing():
    return send_from_directory('templates', 'index.html')


@app.route('/upload')                                                  #upload
def upload():
    file = request.files['inputFile']
    return file.filename


@app.route('/logout')                                                  #MAJD KELL logoutSite - upd dehogy kell -> redirect
def logout():
    return redirect(url_for('/'))
    #return send_from_directory('templates', 'index.html')


@app.route('/<path:filename>', methods=['GET'])                         #fajlok betolteseere szolgal
def send_path(filename):
    return send_from_directory('templates', filename)


"""
@app.route('/onLogin', methods=['POST'])
def new_user():
    users = request.get_json()
    res = {username}
    return jsonify(res)
"""

if __name__ == '__main__':
    app.run()
