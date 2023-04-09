# Made using code adapted from: https://www.youtube.com/watch?v=sVwWEoDa_uY&list=PLs3IFJPw3G9Jwaimh5yTKot1kV5zmzupt&index=6

from flask import Flask, request, jsonify
import pyrebase
from flask_cors import CORS


api = Flask(__name__)
CORS(api)

firebaseConfig = {
    "apiKey": "AIzaSyC-lx6ebkWgXLkS3y5hIdL-Jc_1wUEZJL4",
    "authDomain": "bibliotec-94589.firebaseapp.com",
    "databaseURL": "https://bibliotec-94589-default-rtdb.firebaseio.com",
    "projectId": "bibliotec-94589",
    "storageBucket": "bibliotec-94589.appspot.com",
    "messagingSenderId": "955644180347",
    "appId": "1:955644180347:web:19670871e208817a3eafde"
}

fb = pyrebase.initialize_app(firebaseConfig)
base = fb.database()

# This function gets the information of all cubicles and returns it as a list.


@api.route('/consultarCubiculos', methods=["GET"])
def consultarCubiculos():
    try:
        cubiculos = base.child("cubiculo").get().val()
        lista_cubiculos = list(cubiculos.values())
        return jsonify({"message": lista_cubiculos})

    except:
        return jsonify({"message": "Hubo un error al consultar los cubículos"})


# This function stores a cubicle and it's related information in the DB.
# It checks first if a cubicle with the same id existed already

@api.route('/agregarCubiculo', methods=["POST"])
def agregarCubiculo():
    data = request.get_json()
    cubiculo_id = data["cubiculo_id"]
    max_personas = data["max_personas"]

    nuevo_cubiculo = {
        "cubiculo_id": cubiculo_id,
        "max_personas": max_personas,
        "horario": ""
    }

    try:
        # Validates if the cubicle has already been stored
        cubiculos = base.child("cubiculo").get()

        for cubiculo in cubiculos.each():
            print(cubiculo.val()["cubiculo_id"])
            if (cubiculo.val()["cubiculo_id"] == cubiculo_id):
                return jsonify({"message": "Este cubículo ya ha sido registrado"})

        base.child("cubiculo").push(nuevo_cubiculo)
        return jsonify({"message": "El cubículo se registró exitosamente"})

    except:
        return jsonify({"message": "Hubo un error al agregar el cubículo"})


# This function deletes a cubicle from the db

@api.route('/eliminarCubiculo', methods=["POST"])
def eliminarCubiculo():
    data = request.get_json()
    cubiculo_id = data["cubiculo_id"]

    try:
        # Validates if the cubicle has already been stored
        cubiculos = base.child("cubiculo").get()

        for cubiculo in cubiculos.each():
            if (cubiculo.val()["cubiculo_id"] == cubiculo_id):
                base.child("cubiculo").child(cubiculo.key()).remove()
                return jsonify({"message": "El cubículo se eliminó exitosamente"})

        return jsonify({"message": "El cubículo no existe"})

    except:
        return jsonify({"message": "Hubo un error al eliminar el cubículo"})


# This function updates a cubicle in the DB.

@api.route('/actualizarCubiculo', methods=["POST"])
def actualizarCubiculo():
    data = request.get_json()
    cubiculo_id = data["cubiculo_id"]
    max_personas = data["max_personas"]

    nuevo_cubiculo = {
        "cubiculo_id": cubiculo_id,
        "max_personas": max_personas,
        "horario": ""
    }

    try:
        # Validates if the cubicle has already been stored
        cubiculos = base.child("cubiculo").get()

        for cubiculo in cubiculos.each():
            if (cubiculo.val()["cubiculo_id"] == cubiculo_id):
                base.child("cubiculo").child(cubiculo.key()).update({"max_personas": max_personas})
                return jsonify({"message": "El cubículo se actualizó exitosamente"})

        return jsonify({"message": "El cubículo no existe"})

    except:
        return jsonify({"message": "Hubo un error al actualizar el cubículo"})





@api.route("/")
def hello():
    return "Welcome to Biblio-Tec"


if __name__ == "__main__":
    api.run(debug=True)
