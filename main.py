from flask import Flask, render_template, request
from models import item, loan, penalty
from models.connection import db
from datetime import datetime

# Inicializacion del objeto Flask
app = Flask(__name__)

# Generacion del dict (diccionario) de configuracion desde fichero
app.config.from_pyfile('config.cfg')

app.secret_key = 'random'

# Enlaza la aplicacion y la base de datos
db.app = app
db.init_app(app)
db.create_all()

# TODO
# Actualizar el objeto tras editarlo


@app.route('/', methods=['GET', 'POST'])


@app.route('/login', methods=['GET', 'POST'])


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
        # si se le puede prestar el objeto
        usuario = request.form['user']
        object = item.Item.query.get(request.form.getlist("objeto"))
        # Prestamos realizados por ese usuario y ese objeto
        done_loans = loan.Loan.query.filter_by(user=usuario,
                                               item_id=object.id)
        # Si se le han prestado 2 o más objetos no se puede
        # hacer el préstamo
        if done_loans.count() >= 2:
            error = 'El usuario ha alcanzado el máximo de prestamos'
            return render_template("index.html",
                                   items=item.Item.query.all(),
                                   loans=loan.Loan.query.all(),
                                   error=error)
        # Si aun no ha alcanzado el máximo de prestamos
        else:
            # Se deben prestar menos objetos de los existentes
            if object.amount >= int(request.form['amount']):
                # Fecha en la que hay que devolver el objeto
                loan_data = loan.Loan(object.id,
                                      int(usuario),
                                      int(request.form['amount']),
                                      request.form['loan_date'],
                                      None)

                object.amount -= loan_data.amount
                db.session.add(loan_data)
                db.session.commit()
                return render_template("index.html",
                                       items=item.Item.query.all(),
                                       loans=loan.Loan.query.all())
            # Se han prestamo más objetos de los existentes
            else:
                error = 'No hay tantos objetos para prestar'
                return render_template("index.html",
                                       items=item.Item.query.all(),
                                       loans=loan.Loan.query.all(),
                                       error=error)
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
        loan_item = item.Item(str(request.form['name'].lower()),
                              int(request.form['amount']),
                              str(request.form['type'].lower()),
                              str(request.form['state'].lower()),
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
        # for object in request.form.getlist("objetos"):
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
        # Es una lista con los id de las checkboxes
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
        # Lista para guardar los id de los objetos prestados
        id_prestamos = []
        free_items = []
        for prestamo in loan.Loan.query.all():
            id_prestamos.append(prestamo.item_id)

        # Si el objeto no está prestado se mostrará
        for objeto in item.Item.query.all():
            if objeto.id not in id_prestamos:
                free_items.append(objeto)

        # free_items = item.Item.query.filter(~item.Item.id.in_(id_prestamos))
        return render_template('item_delete.html', items=free_items)


@app.route('/penalty/list', methods=['GET'])
def penalty_list():
    # Obtiene los prestamos de las sanciones
    return render_template('penalty_list.html',
                           penalties=penalty.Penalty.query.all())


@app.route('/penalty/delete', methods=['GET', 'POST'])
def penalty_delete():
    if request.method == 'POST':
        sanciones = request.form.getlist('penalties')
        for sancion in sanciones:
            db_penalty = penalty.Penalty.query.get(sancion)
            db.session.delete(db_penalty)
        db.session.commit()
        return render_template("index.html",
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())
    else:
        return render_template('penalty_delete.html',
                               penalties=penalty.Penalty.query.all())


if __name__ == '__main__':
    app.run()
