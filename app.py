import enum
import time
from flask import Flask, request, jsonify, Response, make_response
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from bson import json_util
import json
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
# For PyMongo
# app.config['MONGO_URI'] = os.environ.get('MONGODB_URI')
app.config['MONGO_URI'] =  os.getenv('MONGODB_URI')

CORS(app, support_credentials=True)
uri = os.environ.get("MONGODB_URI")
# uri = "mongodb+srv://s4yadmin:admin123@animalshelterdb.ub4xlid.mongodb.net/test"
mongoClient = MongoClient(uri)
db = mongoClient.AnimalShelterDB

print('Hello: ',uri)

@app.route("/", methods=['GET'])
@cross_origin()
def home():
    return Response("AnimalShelter, 2022", mimetype="text/plain", status=200)


@app.route("/get-all-animal", methods=['GET'])
@cross_origin()
def getAllAnimal():
    data = db.AnimalSpecies
    resultCursor = data.find().sort("name")
    json_docs = []
    for doc in resultCursor:
        json_docs.append(doc)
    return json.loads(json_util.dumps(json_docs))

@app.route("/get-animals-base-on-demand", methods=['GET'])
@cross_origin()
def getAnimalsBaseOnDemand():
    data = db.AnimalSpecies
    resultCursor = data.find().sort("name")
    data = request.args.get("demand") # format: name,Fun Fact, ... 
    demands = data.split(',')

    json_docs = []
    for doc in resultCursor:
        tmp = {}
        if len(demands) > 1:
            for item in demands:
                if item == '_id':
                    data = str(doc['_id'])
                    tmpData = { 
                        "$oid": data
                    }
                    tmp[item] = tmpData

                elif item in doc:
                    tmp[item] = doc[item]
            json_docs.append(tmp)
        elif len(demands) == 1:
            if demands[0] in doc:
                if demands[0] == '_id':
                    data = str(doc['_id'])
                    tmpData = { 
                        "$oid": data
                    }
                    tmp['_id'] = tmpData
                else:
                    tmp[demands[0]] = doc[demands[0]]
            json_docs.append(tmp)

    return json.loads(json_util.dumps(json_docs))


@app.route("/get-animal-page", methods=['GET'])
@cross_origin()
def getAnimalPage():
    data = db.AnimalSpecies
    page = int(request.args.get("page"))

    resultCursor = data.find().sort("name")
    json_docs = []
    # for doc in resultCursor:
    for i in range((page-1)*18, page*18):
        json_docs.append(resultCursor[i])
    return json.loads(json_util.dumps(json_docs))

@app.route("/search-animal", methods=['GET'])
@cross_origin()
def searchAnimal():
    data = db.AnimalSpecies
    name = request.args.get("name")

    resultCursor = data.find()
    json_docs = []
    for doc in resultCursor:
        if name.lower() in doc["name"].lower():
            json_docs.append(doc)

    return json.loads(json_util.dumps(json_docs))


@app.route("/get-map-data", methods=['GET'])
@cross_origin()
def getAnimalMapData():
    data = db.AnimalMapData
    resultCursor = data.find()
    json_docs = []
    for doc in resultCursor:
        json_docs.append(doc)
    return json.loads(json_util.dumps(json_docs))


@app.route("/get-thumbnails", methods=['GET'])
@cross_origin()
def getThumbnails():
    data = db.AnimalSpecies
    resultCursor = data.find().sort("name")
    json_docs = []
    # for doc in resultCursor:
    for i in range(22):
        tmp = {}
        data = resultCursor[i]
        if 'Gallery' in data:
            tmp['Gallery'] = data['Gallery']
        json_docs.append(tmp)
    return json.loads(json_util.dumps(json_docs))


@app.route("/animal-detail", methods=['GET'])
@cross_origin()
def animalDetail():
    data = db.AnimalSpecies
    key = request.args.get("key")

    resultCursor = data.find({"_id": ObjectId(key)})

    json_docs = []
    for doc in resultCursor:
        json_docs.append(doc)
    return json.loads(json_util.dumps(json_docs))


@app.route("/post-subscription", methods=['POST'])
@cross_origin()
def postSubscription():
    data = db.Subscription
    content = request.json

    content['timestamp'] = round(time.time())
    rec_id = data.insert_one(content)
    print("Data inserted with record ids", rec_id)
    return str(200)


# Run server
if __name__ == "__main__":
    app.run(debug=True, port=8088)
