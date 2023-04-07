from flask import Flask, request, jsonify
import pyrebase
from flask_cors import CORS


api = Flask(__name__)
CORS(api)

firebaseConfig  = {
    "apiKey": "AIzaSyC-lx6ebkWgXLkS3y5hIdL-Jc_1wUEZJL4",
    "authDomain": "bibliotec-94589.firebaseapp.com",
    "databaseURL": "https://bibliotec-94589-default-rtdb.firebaseio.com",
    "projectId": "bibliotec-94589",
    "storageBucket": "bibliotec-94589.appspot.com",
    "messagingSenderId": "955644180347",
    "appId": "1:955644180347:web:19670871e208817a3eafde"
}

fb = pyrebase.initialize_app(firebaseConfig )
base = fb.database()


#This function stores a cubicle and it's related information in the DB.
#It checks first if a cubicle with the same id existed already


@api.route('/agregarCubiculo', methods=["POST"])
def agregarCubiculo():
    data = request.get_json()
    cubiculo_id = data["cubiculo_id"]
    max_personas = data["max_personas"]

    cubiculo = {
        "cubiculo_id": cubiculo_id,
        "max_personas": max_personas,
        "horario": ""
    }

    try:
        # Validates if the cubicle has already been stored
        result = base.child("cubiculo").order_by_child(
            "cubiculo_id").equal_to(cubiculo_id).get().val().keys()
        if result != []:
                return jsonify({"message": "Este cubículo ya ha sido registrado"})
        base.child("cubiculo").child(cubiculo_id).set(cubiculo)
        return jsonify({"message": "El cubículo se registró exitosamente"})
        
    except:
        return jsonify({"message": "Hubo un error al agregar el cubículo"})

@api.route("/")
def hello():
    return "Welcome to Biblio-Tec"

if __name__ == "__main__":
    api.run(debug=True)







