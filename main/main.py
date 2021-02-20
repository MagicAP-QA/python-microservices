from bson.objectid import ObjectId
from flask import Flask, jsonify, abort
from flask_cors import CORS
from flask_pymongo import PyMongo
import requests
from bson import json_util
from producer import publish

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo:27017/main"
CORS(app)

mongo = PyMongo(app)

@app.route('/api/products')
def index():
    data = mongo.db.product.find({})
    dd = json_util.dumps(data)
    print(dd)
    return dd


@app.route('/api/products/<string:id>/like', methods=['POST'])
def like(id):
    req = requests.get('http://backendadmin:8000/api/user')
    json = req.json()
    
    try:
        productUser = mongo.db.product_user.find({"_id":ObjectId(id)})
        # db.session.add(productUser)
        # db.session.commit()
        print(productUser)
        publish('product_liked', id)
    except:
        abort(400, 'You already liked this product')

    return jsonify({
        'message': 'success'
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
