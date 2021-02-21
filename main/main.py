import flask
from bson.objectid import ObjectId
from flask import Flask, jsonify, abort
from flask_cors import CORS
from flask_pymongo import PyMongo
import requests
from bson import json_util
from producer import publish
from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
import requests
import redis
import json 
import constants

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = "http://localhost:8001/callback"
AUTH0_CLIENT_ID = "o6jb3XdJkT4DYlgGe9B58MbwCBNp7Hfg"
AUTH0_CLIENT_SECRET = "xM8oEUTfGFscNk_Rw0njEkyYLpFQLpq9JKWbwhkOd6ISPbgsl6KWDNLNyKztc244"
AUTH0_DOMAIN = "dev-yc8qs3eb.auth0.com"
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)

app = Flask(__name__, static_url_path='/public', static_folder='./public')
app.secret_key = constants.SECRET_KEY
app.debug = True
app.config["MONGO_URI"] = "mongodb://localhost:27017/main"
CORS(app)

mongo = PyMongo(app)

redis_instance = redis.StrictRedis(host='localhost',port=6379, db=0)

@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated

@app.route('/api/products')
def index():
    data = mongo.db.product.find({})
    # dd = json_util.dumps(data)
    # data = redis_instance.get("products_list")
    return jsonify(data)

@app.route('/')
def home():
    return flask.redirect("http://localhost:3000")

@app.route('/api/products/<string:id>/like', methods=['POST'])
def like(id):
    req = requests.get('http://localhost:8000/api/user')
    json = req.json()
    
    try:
        # productUser = {"user_id": ObjectId(json["id"]), "product_id":ObjectId(id)}
        productUser = {"user_id": json["id"], "product_id":id}
        result = mongo.db.product_user.insert_one(productUser)
        print(result.inserted_id)
        publish('product_liked', id)
    except:
        abort(400, 'You already liked this product')

    return jsonify({
        'message': 'success'
    })

@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    print(userinfo)
    session[constants.JWT_PAYLOAD] = userinfo
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/dashboard')


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)

@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
