from datetime import datetime
import ldap
import psycopg2

from flask import Flask, render_template, request, redirect, url_for, make_response

from models import item, loan, penalty
from models.connection import db


# Inicializacion del objeto Flask
app = Flask(__name__)

# Generacion del dict (diccionario) de configuracion desde fichero
app.config.from_pyfile('config.cfg')

app.secret_key = 'random'

# Enlaza la aplicacion y la base de datos
db.app = app
db.init_app(app)
db.create_all()

# Objetos que se pueden prestar dos veces independientemente de la cantidad
two_time_objects = ['Electrónico', 'Eléctrico']
# Objetos que se pueden prestar una vez independientemente de la cantidad
one_time_objects = ['Laboratorio']

# Distintos roles para restringir el acceso
ROL_USER = 10
ROL_ADMIN = 50
ROL_MANAGER = 100

# Base query para la busqueda en el ldap
BASE_DN = "ou=Gente,o=Universidad Carlos III,c=es"

# Servidor para el ldap
ldap_server = None

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Autentifica a los usuarios y comprueba su rol."""
    if request.method == 'GET':
        return render_template("login.html")
    else:
        usuario = str(request.form['nia'])
        contraseña = str(request.form['password'])

        if not usuario or not contraseña:
            # Es necesario introducir algun campo
            error = "Usuario o contraseña incorrectos"
            return render_template("login.html", error=error)

        # Crea una conexion con el servidor ldap
        global ldap_server
        ldap_server = ldap.initialize('ldaps://ldap.uc3m.es')
        ldap_server.protocol_version = ldap.VERSION3
        ldap_server.set_option(ldap.OPT_REFERRALS, 0)

        username = "uid=" + usuario
        # Devuelve una lista con la informacion del alumno buscado
        result = ldap_server.search_s(BASE_DN, ldap.SCOPE_SUBTREE, username)
        # Si nos podemos conectar con esl usiario y contraseña continuamos
        # Sino se han utilizado credenciales no validos
        try:
            connect = ldap_server.simple_bind_s(str(result[0][0]), contraseña)
            delegates_db = psycopg2.connect("dbname='delegates' user='taquillas' host='localhost' password='Yotun.Taquillas.2016'")
            cur = delegates_db.cursor()
            query = "SELECT id_person FROM {} WHERE nia={};".format('person',usuario)
            cur.execute(query)
            id_user = cur.fetchone()

            if not id_user:
                error = "Usuario o contraseña incorrectos"
                return render_template("login.html", error=error)
            else:
                cur = delegates_db.cursor()
                query = "SELECT role FROM {} WHERE id_person={};".format('privilege',id_user[0])
                cur.execute(query)
                rol_user = cur.fetchone()

                if rol_user:
                    rol = str(rol_user[0])
                else:
                    rol = "10"

                # Crea una cookie con el rol del usuario valida para 2 horas
                res = make_response(render_template("index.html",
                                                    items=item.Item.query.all(),
                                                    loans=loan.Loan.query.all()))
                res.set_cookie('rol', rol, max_age=60*60*2)
                return res
        except ldap.INVALID_CREDENTIALS:
            error = "Usuario o contraseña incorrectos"
            return render_template("login.html", error=error)


@app.route('/index', methods=['GET', 'POST'])
def index():
    """ Página principal de la aplicación."""
    if request.method == 'GET':
        try:
            user_rol = int(request.cookies.get('rol'))
            if user_rol < ROL_USER:
                error = "No tiene permisos suficientes"
                res = make_response(render_template("login.html", error=error))
            else:
                res = make_response(render_template("index.html",
                                                    items=item.Item.query.all(),
                                                    loans=loan.Loan.query.all()))
            res.set_cookie('rol', str(user_rol), max_age=60*60*2)
            return res
        except TypeError:
            error = "No ha iniciado sesion"
            res = make_response(render_template("login.html",
                                                error=error))
            return res


@app.route('/loan/create', methods=['GET', 'POST'])
def loan_create():
    if request.method == 'POST':
        current_date = datetime.date(datetime.now())
        # Usuario que ha hecho el prestamos para comprobar
        usuario = request.form['user']
        # Objeto que ha sido prestado
        db_objeto = item.Item.query.get(request.form.getlist("objeto"))

        # Prestamos realizados por ese usuario
        prestamos_dos_veces = prestamos_una_vez = prestamos_normales = 0

        # Posible solucion: Comprobar si los prestamos se han hecho el mismo dia
        for prestamo in loan.Loan.query.filter_by(nia=usuario):
            objeto = item.Item.query.get(prestamo.item_id)
            # Filtra los objetos dependiendo de si se pueden prestar varias veces o solo una
            if objeto.type in two_time_objects:
                prestamos_dos_veces += 1
            elif objeto.type in one_time_objects:
                prestamos_una_vez += 1
            elif objeto.name == db_objeto.name:
                prestamos_normales += prestamo.amount

        cantidad = int(request.form['amount'])

        # Sancion del usuario si existe
        sancion = penalty.Penalty.query.filter(penalty.Penalty.penalty_date > current_date,
                                               penalty.Penalty.nia == int(usuario))

        if sancion.count() >= 1:
            error = 'El usuario está sancionado'
            return render_template("index.html",
                                   items=item.Item.query.all(),
                                   loans=loan.Loan.query.all(),
                                   error=error)

        # Si se le ha prestado dos veces el mismo objeto o ha pedido dos prestamos
        # de los prestamos unicos
        if (
                (db_objeto.type not in two_time_objects and prestamos_normales >= 2) or
                (db_objeto.type in two_time_objects and prestamos_dos_veces >= 2) or
                (db_objeto.type in one_time_objects and prestamos_una_vez >= 1)):
            error = 'Máximo número de prestamos alcanzados'
            return render_template("index.html",
                                   items=item.Item.query.all(),
                                   loans=loan.Loan.query.all(),
                                   error=error)

        # Se han prestamo más objetos de los existentes
        if cantidad > db_objeto.amount:
            error = 'No hay tantos objetos para prestar'
            return render_template("index.html",
                                   items=item.Item.query.all(),
                                   loans=loan.Loan.query.all(),
                                   error=error)

        # El usuario puede coger prestado el objeto
        else:
            loan_data = loan.Loan(db_objeto.id,
                                  int(usuario),
                                  cantidad,
                                  request.form['loan_date'],
                                  None)
            db_objeto.amount -= cantidad
            db.session.add(loan_data)
            db.session.commit()

            global ldap_server
            ldap_server = ldap.initialize('ldaps://ldap.uc3m.es')
            ldap_server.protocol_version = ldap.VERSION3
            ldap_server.set_option(ldap.OPT_REFERRALS, 0)

            username = "uid=" + str(usuario)
            result = ldap_server.search_s(BASE_DN, ldap.SCOPE_SUBTREE, username)[0][1]
            nombre = result['cn'][0].decode("utf-8")
            num_tarjeta = result['uc3midu'][0].decode("utf-8")
            return render_template("index.html",
                                   items=item.Item.query.all(),
                                   loans=loan.Loan.query.all(),
                                   name=nombre,
                                   num_tar=num_tarjeta)
        # GET request
    else:
        try:
            user_rol = int(request.cookies.get('rol'))
            if user_rol < ROL_USER:
                error = "No tiene permisos suficientes"
                res = make_response(render_template("index.html", error=error))
            else:
                free_items = item.Item.query.filter(item.Item.amount > 0)
                res = make_response(render_template("loan_create.html", items=free_items))
                res.set_cookie('rol', str(user_rol), max_age=60*60*2)
            return res
        except TypeError:
            error = "No ha iniciado sesion"
            res = make_response(render_template("login.html",
                                                error=error))
            return res


@app.route('/loan/list', methods=['GET'])
def loan_list():
    """ Muestra todos los prestamos."""
    try:
        user_rol = int(request.cookies.get('rol'))
        if user_rol < ROL_USER:
            error = "No tiene permisos suficientes"
            res = make_response(render_template("index.html",
                                                items=item.Item.query.all(),
                                                loans=loan.Loan.query.all(),
                                                error=error))
        else:
            res = make_response(render_template('loan_list.html',
                                                items=item.Item.query.all(),
                                                loans=loan.Loan.query.all()))
            res.set_cookie('rol', str(user_rol), max_age=60*60*2)
        return res
    except TypeError:
        error = "No ha iniciado sesion"
        res = make_response(render_template("login.html",
                                            error=error))
        return res


# @app.route('/loan/delete', defaults={'loan_id': None}, methods=['GET', 'POST'])
# @app.route('/loan/delete/<int:loan_id>', methods=['GET', 'POST'])
@app.route('/loan/delete', methods=['GET', 'POST'])
def loan_delete():
    """ Marca un préstamo como finalizado."""
    if request.method == 'POST':
        current_date = datetime.date(datetime.now())
        # Lista de los prestamos que se han seleccionado para borrar
        deleted_loans = request.form.getlist("prestamos")
        names_list = []

        global ldap_server
        ldap_server = ldap.initialize('ldaps://ldap.uc3m.es')
        ldap_server.protocol_version = ldap.VERSION3
        ldap_server.set_option(ldap.OPT_REFERRALS, 0)

        for prestamo in deleted_loans:
            db_prestamo = loan.Loan.query.get(int(prestamo))
            objeto = item.Item.query.get(db_prestamo.item_id)
            # Devuelve los objetos prestados a la db
            objeto.amount += db_prestamo.amount

            username = "uid=" + str(db_prestamo.nia)
            result = ldap_server.search_s(BASE_DN, ldap.SCOPE_SUBTREE, username)[0][1]
            nombre = result['cn'][0].decode("utf-8")
            num_tarjeta = result['uc3midu'][0].decode("utf-8")
            names_list.append(str(nombre))

            # Marca el objeto como devuelto
            db_prestamo.refund_date = current_date
            db.session.commit()
            
        return render_template("index.html",
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all(),
                               names_list=names_list)
    else:
        try:
            user_rol = int(request.cookies.get('rol'))
            if user_rol < ROL_USER:
                error = "No tiene permisos suficientes"
                res = make_response(render_template("index.html",
                                                    items=item.Item.query.all(),
                                                    loans=loan.Loan.query.all(),
                                                    error=error))
            else:
                res = make_response(render_template('loan_delete.html',
                                                    items=item.Item.query.all(),
                                                    loans=loan.Loan.query.filter_by(refund_date=None)))
                res.set_cookie('rol', str(user_rol), max_age=60*60*2)
            return res
        except TypeError:
            error = "No ha iniciado sesion"
            res = make_response(render_template("login.html",
                                                error=error))
            return res


@app.route('/object/create', methods=['GET', 'POST'])
def item_create():
    """ Crea un objeto y lo añade a la base de datos."""
    if request.method == 'POST':
        loan_item = item.Item(str(request.form['name']),
                              int(request.form['amount']),
                              str(request.form['type']),
                              str(request.form['state']),
                              int(request.form['loan_days']),
                              float(request.form['penalty_coefficient']))
        # Añade el objeto a la db
        db.session.add(loan_item)
        db.session.commit()
        return render_template("index.html",
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())
    else:
        try:
            user_rol = int(request.cookies.get('rol'))
            if user_rol < ROL_ADMIN:
                error = "No tiene permisos suficientes"
                res = make_response(render_template("index.html",
                                                    items=item.Item.query.all(),
                                                    loans=loan.Loan.query.all(),
                                                    error=error))
            else:
                res = make_response(render_template('item_create.html'))
                res.set_cookie('rol', str(user_rol), max_age=60*60*2)
            return res
        except TypeError:
            error = "No ha iniciado sesion"
            res = make_response(render_template("login.html",
                                                error=error))
            return res


@app.route('/object/list', methods=['GET'])
def item_list():
    """ Muestra todos los objetos que existen."""
    try:
        user_rol = int(request.cookies.get('rol'))
        if user_rol < ROL_USER:
            error = "No tiene permisos suficientes"
            res = make_response(render_template("index.html",
                                                items=item.Item.query.all(),
                                                loans=loan.Loan.query.all(),
                                                error=error))
        else:
            res = make_response(render_template('item_list.html', items=item.Item.query.all()))
            res.set_cookie('rol', str(user_rol), max_age=60*60*2)
        return res
    except TypeError:
        error = "No ha iniciado sesion"
        res = make_response(render_template("login.html",
                                            error=error))
        return res


@app.route('/object/edit', methods=['GET', 'POST'])
def item_edit():
    """ Permite editar objetos."""
    if request.method == 'POST':
        db_object = item.Item.query.get(request.form.getlist("objetos"))

        nombre = request.form['name']
        cantidad = request.form['amount']
        tipo = request.form['type']
        estado = request.form['state']
        dias = request.form['loan_days']
        coeficiente = request.form['penalty_coefficient']

        db_object.name = str(nombre) if nombre else db_object.name
        db_object.amount = int(cantidad) if cantidad else db_object.amount
        db_object.type = str(tipo) if tipo else db_object.type
        db_object.state = str(estado) if estado else db_object.state
        db_object.loan_days = int(dias) if dias else db_object.loan_days
        db_object.penalty_coefficient = float(coeficiente) if coeficiente else db_object.penalty_coefficient

        db.session.commit()
        return render_template('index.html',
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())
    else:
        try:
            user_rol = int(request.cookies.get('rol'))
            if user_rol < ROL_ADMIN:
                error = "No tiene permisos suficientes"
                res = make_response(render_template("index.html",
                                                    items=item.Item.query.all(),
                                                    loans=loan.Loan.query.all(),
                                                    error=error))
            else:
                res = make_response(render_template('item_edit.html', items=item.Item.query.all()))
                res.set_cookie('rol', str(user_rol), max_age=60*60*2)
            return res
        except TypeError:
            error = "No ha iniciado sesion"
            res = make_response(render_template("login.html",
                                                error=error))
            return res


@app.route('/object/delete', methods=['GET', 'POST'])
def item_delete():
    """ Elimina un objeto de la base de datos."""
    if request.method == 'POST':
        # Obtiene la lista de objetos seleccionados
        deleted_objects = request.form.getlist("objetos")
        # Busca los objeto/s a borrar en la db
        for object in deleted_objects:
            # Elimina el objeto de la db PERMANENTEMENTE
            db_object = item.Item.query.get(int(object))
            db.session.delete(db_object)
            db.session.commit()
        return render_template("index.html",
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())
    else:
        # Solo se pueden eliminar objetos que no están prestados
        id_prestamos_not_refund = []
        free_items = []
        for prestamo in loan.Loan.query.filter_by(refund_date=None):
            id_prestamos_not_refund.append(prestamo.item_id)
        for objeto in item.Item.query.filter(item.Item.amount > 0):
            if objeto.id not in id_prestamos_not_refund:
                free_items.append(objeto)

        try:
            user_rol = int(request.cookies.get('rol'))
            if user_rol < ROL_ADMIN:
                error = "No tiene permisos suficientes"
                res = make_response(render_template("index.html",
                                                    items=item.Item.query.all(),
                                                    loans=loan.Loan.query.all(),
                                                    error=error))
            else:
                res = make_response(render_template('item_delete.html', items=free_items))
                res.set_cookie('rol', str(user_rol), max_age=60*60*2)
            return res
        except TypeError:
            error = "No ha iniciado sesion"
            res = make_response(render_template("login.html",
                                                error=error))
            return res


@app.route('/penalty/create', methods=['GET', 'POST'])
def penalty_create():
    """ Sanciona a un usuario.
    Si el usuario ya esta sancioando se actualiza la fecha de la sancion.
    """
    if request.method == 'POST':
        user = request.form['user']
        try:
            db_loan = loan.Loan.query.filter_by(nia=user)
            loan_to_send = db_loan[0].id 
        except IndexError:
            loan_to_send = None

        sanction = penalty.Penalty.query.filter_by(nia=user)

        # Actualizar la fecha final
        fecha_sancion = request.form['initial_date']
        fecha_final = request.form['end_date']
        if sanction.count() > 0:
            sanction[0].sanction_date = fecha_sancion
            sanction[0].penalty_date = fecha_final
            db.session.commit()
        else:
            # Se crea una sancion para el usuario
            sancion = penalty.Penalty(user,
                                      loan_to_send,
                                      fecha_sancion,
                                      fecha_final)
            db.session.add(sancion)
            db.session.commit()
        return render_template("index.html",
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())
    else:
        try:
            user_rol = int(request.cookies.get('rol'))
            if user_rol < ROL_MANAGER:
                error = "No tiene permisos suficientes"
                res = make_response(render_template("index.html",
                                                    items=item.Item.query.all(),
                                                    loans=loan.Loan.query.all(),
                                                    error=error))
            else:
                res = make_response(render_template('penalty_create.html'))
                res.set_cookie('rol', str(user_rol), max_age=60*60*2)
            return res
        except TypeError:
            error = "No ha iniciado sesion"
            res = make_response(render_template("login.html",
                                                error=error))
            return res


@app.route('/penalty/list', methods=['GET'])
def penalty_list():
    """Muestra todas las sanciones."""
    res = make_response(render_template("penalty_list.html",
                                        penalties=penalty.Penalty.query.all()))
    res.set_cookie('rol', request.cookies.get('rol'), max_age=60*60*2)
    return res


@app.route('/penalty/delete', methods=['GET', 'POST'])
def penalty_delete():
    """Elimina una sanción."""
    current_date = datetime.date(datetime.now())
    if request.method == 'POST':
        # Itera sobre las sacciones enviadas
        for sanction in request.form.getlist('penalties'):
            db_penalty = penalty.Penalty.query.get(sanction)
            # Marca la sanción como terminada
            db_penalty.penalty_date = current_date
            db.session.commit()
        return render_template("index.html",
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())
    else:
        try:
            user_rol = int(request.cookies.get('rol'))
            if user_rol < ROL_MANAGER:
                error = "No tiene permisos suficientes"
                res = make_response(render_template("index.html",
                                                    items=item.Item.query.all(),
                                                    loans=loan.Loan.query.all(),
                                                    error=error))
            else:
                res = make_response(render_template('penalty_delete.html',
                                                    penalties=penalty.Penalty.query.filter(penalty.Penalty.penalty_date > current_date)))
                res.set_cookie('rol', str(user_rol), max_age=60*60*2)
            return res
        except TypeError:
            error = "No ha iniciado sesion"
            res = make_response(render_template("login.html",
                                                error=error))
            return res
        


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """Cierra la sesión del usuario. """
    # Eliminates the cookie and returns to login
    res = make_response(render_template('login.html'))
    res.set_cookie('rol', request.cookies.get('rol'), max_age=0)
    return res


if __name__ == '__main__':
    app.run(host='0.0.0.0')
