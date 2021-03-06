"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Todo
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)



# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/todos/<user>', methods=['GET'])
def handle_todo(user):
    todos = Todo.query.filter_by(user=user)
    response_body = list(map(lambda x: x.serialize(), todos))
    return jsonify(response_body), 200 

@app.route('/todos', methods=['POST'])
def handle_new():
    todo = request.json
    new_todo = Todo(label=todo["label"],done=todo["done"],user=todo["user"])
    db.session.add(new_todo)
    db.session.commit()
    todos = Todo.query.all()
    response_body = list(map(lambda x: x.serialize(), todos))
    return jsonify(response_body), 200 

@app.route('/todos/<int:id>', methods=['PUT'])
def handle_update(id):
    task1 = Todo.query.get(id)
    todo = request.json
    if task1 is None:
        raise APIException('Task not found', status_code=404)
    task1.label = todo['label']
    task1.done = todo['done']
    db.session.commit()
    todos = Todo.query.filter_by(user=todo['user'])
    response_body = list(map(lambda x: x.serialize(), todos))
    return jsonify(response_body), 200 

@app.route('/todos/<user>/<int:id>', methods=['DELETE'])
def handle_delete(user,id):
    remove_task = Todo.query.get(id)
    if remove_task is None:
        raise APIException('Task list not found', status_code=404)
    db.session.delete(remove_task)
    db.session.commit()
    todos = Todo.query.filter_by(user=user)
    response_body = list(map(lambda x: x.serialize(), todos))
    return jsonify(response_body), 200 


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
