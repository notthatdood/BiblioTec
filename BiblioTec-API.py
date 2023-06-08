# Made using code adapted from: https://www.youtube.com/watch?v=sVwWEoDa_uY&list=PLs3IFJPw3G9Jwaimh5yTKot1kV5zmzupt&index=6
# Made using code adapted from: https://github.com/The-Intrigued-Engineer/python_emails/blob/main/text_email.py
# Made using code adapted from: https://www.codeitbro.com/send-email-using-python/

from flask import Flask, request, jsonify
import pyrebase
from flask_cors import CORS
import smtplib
import ssl
import qrcode
############################################# DB and API configs############################################


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


############################################# SMTP ############################################


def enviarCorreoATodos(message):
    print("bbbbbbbbbbbbbbbbbbb")
    try:
        estudiantes = base.child("estudiante").get()

        for estudiante in estudiantes.each():
            print(estudiante.val())
            enviarCorreo(estudiante.val()["correo"], message)
    except Exception as e:
        print(e)


def enviarCorreo(email_to, message):
    img = qrcode.make('Some data here')
    type(img)  # qrcode.image.pil.PilImage
    img.save("qrcode.png")

    smtp_port = 587                 # Standard secure SMTP port
    smtp_server = "smtp.gmail.com"  # Google SMTP Server

    email_from = "bibliotecmail@gmail.com"
    # email_to = "xxxxxxxxxx@gmail.com"

    pswd = "pubrnylofjmuqmff"

    # Create context
    simple_email_context = ssl.create_default_context()

    try:
        # Connect to the server
        print("Connecting to server...")
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls(context=simple_email_context)
        TIE_server.login(email_from, pswd)
        print("Connected to server :-)")

        # Send the actual email
        print()
        print(f"Sending email to - {email_to}")
        TIE_server.sendmail(email_from, email_to, message)
        print(f"Email successfully sent to - {email_to}")

    # If there's an error, print it out
    except Exception as e:
        print(e)
        print("Error al enviar correo a: ", email_to)

    # Close the port
    finally:
        TIE_server.quit()


############################################# Cubicle ############################################


# This function gets the information of all cubicles and returns it as a list.
@api.route('/consultarCubiculos', methods=["POST"])
def consultarCubiculos():
    try:
        cubiculos = base.child("cubiculo").get().val()
        lista_cubiculos = list(cubiculos.values())
        return jsonify(lista_cubiculos)

    except:
        return jsonify({"Hubo un error al consultar los cubículos"})

# This function gets the information of cubicles matching the desired state.
@api.route('/filtrarCubiculosDisponibilidad', methods=["POST"])
def filtrarCubiculosDisponibilidad():
    data = request.get_json()
    estado = data["estado"]

    try:
        lista_cubiculos=[]
        cubiculos = base.child("cubiculo").get()
        for cubiculo in cubiculos.each():
            if (cubiculo.val()["estado"] == estado):
                lista_cubiculos += cubiculo.val()

        return jsonify(lista_cubiculos)

    except:
        return "Hubo un error al buscar los cubiculos"
    
# This function gets the information of cubicles matching the desired capacity.
@api.route('/filtrarCubiculosCapacidad', methods=["POST"])
def filtrarCubiculosCapacidad():
    data = request.get_json()
    max_personas = data["max_personas"]

    try:
        lista_cubiculos=[]
        cubiculos = base.child("cubiculo").get()
        for cubiculo in cubiculos.each():
            if (cubiculo.val()["max_personas"] == max_personas):
                lista_cubiculos += cubiculo.val()

        return jsonify({"message": lista_cubiculos})

    except:
        return jsonify({"message": "Hubo un error al buscar los cubiculos"})


# This function registers a cubicle and it's related information in the DB.
# It checks first if a cubicle with the same id existed already
@api.route('/agregarCubiculo', methods=["POST"])
def agregarCubiculo():
    data = request.get_json()
    cubiculo_id = data["cubiculo_id"]
    max_personas = data["max_personas"]
    esEspecial = data["esEspecial"]

    nuevo_cubiculo = {
        "cubiculo_id": cubiculo_id,
        "max_personas": max_personas,
        "estado": "libre",
        "historial": {},
        "asignado": " ",
        "tiempo": "0",
        "esEspecial": esEspecial
    }

    try:
        # Validates if the cubicle has already been registered
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
    estado = data["estado"]
    asignado = data["asignado"]
    esEspecial = data["esEspecial"]
    tiempo = data["tiempo"]

    nuevo_cubiculo = {
        "cubiculo_id": cubiculo_id,
        "max_personas": max_personas,
        "estado": estado,
        "asignado": asignado,
        "tiempo": tiempo
    }

    try:
        cubiculos = base.child("cubiculo").get()
        for cubiculo in cubiculos.each():
            if (cubiculo.val()["cubiculo_id"] == cubiculo_id):
                if (max_personas != ""):
                    base.child("cubiculo").child(cubiculo.key()).update(
                        {"max_personas": max_personas})
                if (estado != ""):
                    base.child("cubiculo").child(
                        cubiculo.key()).update({"estado": estado})
                if (asignado != ""):
                    base.child("cubiculo").child(cubiculo.key()).update({"asignado": asignado})
                if (tiempo != ""):
                    base.child("cubiculo").child(cubiculo.key()).update({"tiempo": tiempo})
                
                message = "Se actualizaron los datos del cubiculo: "
                message = message + str(nuevo_cubiculo["cubiculo_id"])
                enviarCorreoATodos(message.encode('utf-8'))
                return jsonify({"message": "El cubículo se actualizó exitosamente"})

        return jsonify({"message": "El cubículo no existe"})

    except:
        return jsonify({"message": "Hubo un error al actualizar el cubículo"})

#This function makes a reservation for the specified cubicle
@api.route('/reservarCubiculo', methods=["POST"])
def reservarCubiculo():
    data = request.get_json()
    cubiculo_id = data["cubiculo_id"]
    asignado = data["asignado"]
    tiempo = data["tiempo"]

    reserva_cubiculo = {
        "cubiculo_id": cubiculo_id,
        "estado": "ocupado",
        "asignado": asignado,
        "tiempo": tiempo
    }

    try:
        cubiculos = base.child("cubiculo").get()
        for cubiculo in cubiculos.each():
            if (cubiculo.val()["cubiculo_id"] == cubiculo_id):
                if (cubiculo.val()["estado"] == "ocupado"):
                    return "El cubiculo "+cubiculo.val()["estado"] +cubiculo.val()["cubiculo_id"]+ "ya estaba ocupado"
                if (asignado != ""):
                    base.child("cubiculo").child(cubiculo.key()).update({"asignado": asignado})
                    base.child("cubiculo").child(cubiculo.key()).update({"estado": "ocupado"})
                    base.child("cubiculo").child(cubiculo.key()).update({"tiempo": tiempo})
                    base.child("cubiculo").child(cubiculo.key()).child("historial").push({"asignado": asignado})

                message = "Se reservó el cubiculo: "
                message = message + str(reserva_cubiculo["cubiculo_id"])
                print("oli")
                enviarCorreo(asignado, message.encode('utf-8'))
                return "El cubiculo se reservo exitosamente"

        return "El cubiculo no existe"

    except:
        return "Error durante la reservación"




############################################# Student ############################################


# This function gets the information of all students and returns it as a list.
@api.route('/consultarEstudiantes', methods=["POST"])
def consultarEstudiantes():
    try:
        estudiantes = base.child("estudiante").get().val()
        lista_estudiantes = list(estudiantes.values())
        print(lista_estudiantes)
        admins = base.child("administrador").get().val()
        lista_admins = list(admins.values())
        print(lista_admins)
        lista_estudiantes += lista_admins
        return jsonify(lista_estudiantes)

    except:
        return jsonify({"message": "Hubo un error al consultar los estudiantes"})


# This function registers a student and it's related information in the DB.
# It checks first if a student with the same id existed already
@api.route('/agregarEstudiante', methods=["POST"])
def agregarEstudiante():
    data = request.get_json()
    estudiante_id = data["estudiante_id"]
    nombre = data["nombre"]
    primer_apellido = data["primer_apellido"]
    segundo_apellido = data["segundo_apellido"]
    correo = data["correo"]
    contrasena = data["contrasena"]

    nuevo_estudiante = {
        "estudiante_id": estudiante_id,
        "nombre": nombre,
        "primer_apellido": primer_apellido,
        "segundo_apellido": segundo_apellido,
        "correo": correo,
        "contrasena": contrasena
    }

    try:
        # Validates if the student has already been registered
        estudiantes = base.child("estudiante").get()
        for estudiante in estudiantes.each():
            print(estudiante.val()["estudiante_id"])
            if (estudiante.val()["estudiante_id"] == estudiante_id):
                return jsonify({"message": "Este estudiante ya ha sido registrado"})

        base.child("estudiante").push(nuevo_estudiante)
        return jsonify({"message": "El estudiante se registro exitosamente"})

    except:
        return jsonify({"message": "Hubo un error al agregar al estudiante"})


# This function updates a student's information
@api.route('/actualizarEstudiante', methods=["POST"])
def actualizarEstudiante():
    data = request.get_json()
    estudiante_id = data["estudiante_id"]
    nombre = data["nombre"]
    primer_apellido = data["primer_apellido"]
    segundo_apellido = data["segundo_apellido"]
    correo = data["correo"]
    contrasena = data["contrasena"]

    nuevo_estudiante = {
        "estudiante_id": estudiante_id,
        "nombre": nombre,
        "primer_apellido": primer_apellido,
        "segundo_apellido": segundo_apellido,
        "correo": correo,
        "contrasena": contrasena
    }

    try:
        estudiantes = base.child("estudiante").get()
        for estudiante in estudiantes.each():
            print(estudiante.val()["estudiante_id"])
            if (estudiante.val()["estudiante_id"] == estudiante_id):
                if (nombre != ""):
                    base.child("estudiante").child(
                        estudiante.key()).update({"nombre": nombre})
                if (primer_apellido != ""):
                    base.child("estudiante").child(estudiante.key()).update(
                        {"primer_apellido": primer_apellido})
                if (segundo_apellido != ""):
                    base.child("estudiante").child(estudiante.key()).update(
                        {"segundo_apellido": segundo_apellido})
                if (correo != ""):
                    base.child("estudiante").child(
                        estudiante.key()).update({"correo": correo})
                if (contrasena != ""):
                    base.child("estudiante").child(estudiante.key()).update({"contrasena": contrasena})
                return jsonify({"message": "El estudiante se editó exitosamente"})

        return jsonify({"message": "Este estudiante no se ha encontrado"})

    except:
        return jsonify({"message": "Hubo un error al editar al estudiante"})


# This function deletes a student
@api.route('/eliminarEstudiante', methods=["POST"])
def eliminarEstudiante():
    data = request.get_json()
    estudiante_id = data["estudiante_id"]

    try:
        estudiantes = base.child("estudiante").get()
        for estudiante in estudiantes.each():
            if (estudiante.val()["estudiante_id"] == estudiante_id):
                base.child("estudiante").child(estudiante.key()).remove()
                return jsonify({"message": "El estudiante se elimino exitosamente"})

        return jsonify({"message": "El estudiante no existe"})

    except:
        return jsonify({"message": "Hubo un error al eliminar al estudiante"})


############################################# Reservations ############################################


# This function gets the reservation history of all cubicles
@api.route('/consultarHistorialCubiculos', methods=["POST"])
def consultarHistorialCubiculos():
    asignacion = {
        "asignado": "",
        "cubiculo_id": ""
    }
    try:
        lista_reservas = []
        cubiculos = base.child("cubiculo").get()
        for cubiculo in cubiculos.each():
            #lista_reservas += cubiculo.val()["cubiculo_id"]
            historial = base.child("cubiculo").child(cubiculo.key()).child("historial").get()
            for registro in historial.each():
                print(registro.val()["asignado"])
                asignacion["asignado"] = registro.val()["asignado"]
                asignacion["cubiculo_id"] = cubiculo.val()["cubiculo_id"]
                #lista_reservas += [registro.val()["asignado"]]
                lista_reservas += [asignacion.copy()]
        return jsonify(lista_reservas)

    except:
        return jsonify({"message": "Hubo un error al consultar el historial de reservas"})

# This function gets the reservation history of a single cubicles
@api.route('/consultarHistorialCubiculo', methods=["POST"])
def consultarHistorialCubiculo():
    data = request.get_json()
    cubiculo_id = data["cubiculo_id"]

    try:
        lista_reservas = []
        cubiculos =base.child("cubiculo").get()
        for cubiculo in cubiculos.each():
            if (cubiculo.val()["cubiculo_id"] == cubiculo_id):
                historial = base.child("cubiculo").child(cubiculo.key()).child("historial").get()
                for registro in historial.each():
                    print(registro.val()["asignado"])
                    lista_reservas += [registro.val()["asignado"]]

        return jsonify(lista_reservas)

    except:
        return jsonify({"message": "Hubo un error al consultar el historial de reservas"})

# This function clears the current reservation state of a cubicle
@api.route('/eliminarAsignacionCubiculo', methods=["POST"])
def eliminarAsignacion():
    data = request.get_json()
    cubiculo_id = data["cubiculo_id"]

    try:
        cubiculos =base.child("cubiculo").get()
        for cubiculo in cubiculos.each():
            if (cubiculo.val()["cubiculo_id"] == cubiculo_id):
                base.child("cubiculo").child(cubiculo.key()).update({"asignado": ""})
                base.child("cubiculo").child(cubiculo.key()).update({"estado": "disponible"})
                return jsonify({"message": "Asignacion eliminada"})

        return jsonify({"message": "No se ha encontrado el cubiculo"})

    except:
        return jsonify({"message": "Hubo un error al eliminar la asignacion"})

# This function modifies the current reservation state of a cubicle
@api.route('/actualizarAsignacionCubiculo', methods=["POST"])
def actualizarAsignacionCubiculo():
    data = request.get_json()
    cubiculo_id = data["cubiculo_id"]
    asignado = data["asignado"]
    estado = data["estado"]

    try:
        cubiculos =base.child("cubiculo").get()
        for cubiculo in cubiculos.each():
            if (cubiculo.val()["cubiculo_id"] == cubiculo_id):
                if (asignado != ""):
                    base.child("cubiculo").child(cubiculo.key()).update({"asignado": asignado})
                if (estado != ""):
                    base.child("cubiculo").child(cubiculo.key()).update({"estado": estado})
                return jsonify({"message": "Asignacion eliminada"})

        return jsonify({"message": "No se ha encontrado el cubiculo"})

    except:
        return jsonify({"message": "Hubo un error al eliminar la asignacion"})

@api.route("/")
def hello():
    return "Welcome to Biblio-Tec"


if __name__ == "__main__":
    api.run(debug=True)
