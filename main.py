from datetime import datetime, timedelta

from flask import Flask, render_template, request
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
two_time_objects = ['electronico', 'electrico']


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html",
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())


@app.route('/loan/create', methods=['GET', 'POST'])
def loan_create():
    if request.method == 'POST':
        # Usuario que ha hecho el prestamos para comprobar
        usuario = request.form['user']
        # Objeto que ha sido prestado
        db_objeto = item.Item.query.get(request.form.getlist("objeto"))

        # Prestamos realizados por ese usuario
        prestamos_especiales = prestamos_normales = 0
        for prestamo in loan.Loan.query.filter_by(user=usuario):
            objeto = item.Item.query.get(prestamo.item_id)
            # Filtra los objetos dependiendo de si se pueden prestar varias veces o solo una
            if objeto.type in two_time_objects:
                prestamos_especiales += 1
            elif objeto.name == db_objeto.name:
                prestamos_normales += prestamo.amount

        # Sancion del usuario si existe
        sancion = penalty.Penalty.query.filter_by(user=int(usuario),
                                                  penalty_date=None)

        cantidad = int(request.form['amount'])
        # El usuario está sancionado
        if sancion.count() >= 1:
            error = 'El usuario está sancionado'
            return render_template("index.html",
                                   items=item.Item.query.all(),
                                   loans=loan.Loan.query.all(),
                                   error=error)

        # Si se le ha prestado dos veces el mismo objeto o ha pedido dos prestamos
        # de los prestamos unicos
        if (db_objeto.type not in two_time_objects and prestamos_normales >= 2
                or db_objeto.type in two_time_objects and prestamos_especiales >= 2):
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
            return render_template("index.html",
                                   items=item.Item.query.all(),
                                   loans=loan.Loan.query.all())
    # GET request
    else:
        free_items = item.Item.query.filter(item.Item.amount > 0)
        return render_template("loan_create.html",
                               items=free_items)


@app.route('/loan/list', methods=['GET'])
def loan_list():
    return render_template('loan_list.html',
                           loans=loan.Loan.query.all(),
                           items=item.Item.query.all())


@app.route('/loan/delete', methods=['GET', 'POST'])
def loan_delete():
    if request.method == 'POST':
        current_date = datetime.date(datetime.now())  # Fecha actual
        # Ids de los prestamos que se han seleccionado para borrar
        deleted_loans = request.form.getlist("prestamos")
        for prestamo in deleted_loans:
            db_prestamo = loan.Loan.query.get(int(prestamo))
            objeto = item.Item.query.get(db_prestamo.item_id)
            # Devuelve los objetos prestados a la db y
            objeto.amount += db_prestamo.amount
            # Marca el objeto como devuelto
            db_prestamo.refund_date = current_date
            db.session.commit()
        return render_template("index.html",
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())
    else:
        # Devuelve las dos listas en vez de una como debería ser

        # porque jinja no devuelve bien los valores al estar las dos
        # listas en un zip
        return render_template('loan_delete.html',
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.filter_by(refund_date=None))


@app.route('/object/create', methods=['GET', 'POST'])
def item_create():
    if request.method == 'POST':
        loan_item = item.Item(str(request.form['name']).lower(),
                              int(request.form['amount']),
                              str(request.form['type']).lower(),
                              str(request.form['state']).lower(),
                              int(request.form['loan_days']),
                              float(request.form['penalty_coefficient']))
        # Añade el objeto a la db
        db.session.add(loan_item)
        db.session.commit()
        return render_template("index.html",
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())
    else:
        return render_template('item_create.html')


@app.route('/object/list', methods=['GET'])
def item_list():
    return render_template('item_list.html',
                           items=item.Item.query.all())


@app.route('/object/edit', methods=['GET', 'POST'])
def item_edit():
    if request.method == 'POST':
        # Obtiene la lista de objetos para editar
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
        db_object.penalty_coefficient = float(
            coeficiente) if coeficiente else db_object.penalty_coefficient

        db.session.commit()
        return render_template('index.html',
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())
    else:
        return render_template('item_edit.html',
                               items=item.Item.query.all())


@app.route('/object/delete', methods=['GET', 'POST'])
def item_delete():
    if request.method == 'POST':
        # Obtiene la lista de objetos seleccionados
        # Es una lista con los id de los objetos
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
        # Lista para guardar los id de los objetos prestados no devueltos
        # y los objetos que estan libres
        id_prestamos = []
        free_items = []
        for prestamo in loan.Loan.query.filter_by(refund_date=None):
            id_prestamos.append(prestamo.item_id)
        # Si el objeto no está prestado se mostrará
        # free_items = item.Item.query.filter(~item.Item.id.in_(id_prestamos))
        for objeto in item.Item.query.filter(item.Item.amount > 0):
            if objeto.id not in id_prestamos:
                free_items.append(objeto)
        return render_template('item_delete.html', items=free_items)


@app.route('/penalty/create', methods=['GET', 'POST'])
def penalty_create():
    if request.method == 'POST':
        usuario = request.form['user']
        prestamo = loan.Loan.query.filter_by(user=usuario)
        sancion = penalty.Penalty.query.filter_by(user=usuario)
        # El usuario no esta en la base de datos
        if prestamo.count() == 0:
            error = "El usuario no se encuentra en la base de datos"
            return render_template("index.html",
                                   items=item.Item.query.all(),
                                   loans=loan.Loan.query.all(),
                                   error=error)
        else:
            fecha_sancion = datetime.date(datetime.now())  # Fecha actual
            fecha_final = fecha_sancion + timedelta(days=(150))
            # Si el usuario existe, actualizar la fecha final
            if sancion.count() > 0:
                sancion[0].sanction_date = fecha_sancion
                sancion[0].penalty_date = fecha_final
                db.session.commit()

            # Se crea una sancion para el usuario
            else:
                # El usuario no puede coger ningún objeto más en el cuatrimestre
                sancion = penalty.Penalty(usuario,
                                          prestamo[0].id,
                                          fecha_sancion,
                                          fecha_final)
                db.session.add(sancion)
                db.session.commit()
            return render_template("index.html",
                                   items=item.Item.query.all(),
                                   loans=loan.Loan.query.all())
    # GET request
    else:
        return render_template('penalty_create.html')


@app.route('/penalty/list', methods=['GET'])
def penalty_list():
    # Obtiene los prestamos de las sanciones
    return render_template('penalty_list.html',
                           penalties=penalty.Penalty.query.all())


@app.route('/penalty/delete', methods=['GET', 'POST'])
def penalty_delete():
    current_date = datetime.date(datetime.now())  # Fecha actual
    if request.method == 'POST':
        # Itera sobre las sacciones enviadas
        for sancion in request.form.getlist('penalties'):
            db_penalty = penalty.Penalty.query.get(sancion)
            # Marca la sanción como terminada
            db_penalty.penalty_date = current_date
        db.session.commit()
        return render_template("index.html",
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())
    else:
        return render_template('penalty_delete.html',
                               penalties=penalty.Penalty.query.filter(penalty.Penalty.penalty_date > current_date))


if __name__ == '__main__':
    app.run()
