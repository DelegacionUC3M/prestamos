from flask import Flask, render_template, request
from models import item, loan, penalty
from models.connection import db
from datetime import datetime, timedelta

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
# Crear un buscador para añadir objetos a los prestamos
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
        # Objeto/s que se ha prestado
        object = item.Item.query.get(int(request.form.get('comp_select')))
        # Se deben prestar menos objetos de los existentes
        if object.amount >= int(request.form['amount']):
            # Fecha en la que el objeto se ha prestado
            loan_date = datetime.strptime(request.form['loan_date'],
                                          "%Y-%m-%d")
            # Fecha en la que hay que devolver el objeto
            refund_date = loan_date + timedelta(days=object.loan_days)
            loan_data = loan.Loan(request.form.get('comp_select'),
                                  int(request.form['user']),
                                  int(request.form['amount']),
                                  request.form['loan_date'],
                                  refund_date)

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
        return render_template("loan_create.html",
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())


@app.route('/loan/list', methods=['GET'])
def loan_list():
    return render_template('loan_list.html',
                           loans=loan.Loan.query.all(),
                           items=item.Item.query.all())


@app.route('/loan/delete', methods=['GET', 'POST'])
def loan_delete():
    if request.method == 'POST':
        # Obtiene el préstamo de la base de datos
        # cuyo id corresponde con el del formulatio
        deleted_loans = request.form.getlist("prestamos")
        for id_prestamo in deleted_loans:
            prestamo = loan.Loan.query.get(id_prestamo)
            # Objeto al que referencia el prestamo
            object = item.Item.query.get(prestamo.item_id)
            # Devuelve los objetos prestados a la db
            object.amount += prestamo.amount
            # Elimina el prestamo de la db
            db.session.delete(prestamo)
        db.session.commit()
        return render_template("index.html",
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())
    else:
        return render_template('loan_delete.html',
                               items=item.Item.query.all(),
                               loans=loan.Loan.query.all())



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
        for prestamo in loan.Loan.query.all():
            id_prestamos.append(prestamo.item_id)

        # Si el objeto no está prestado se mostrará
        free_items = item.Item.query.filter(~item.Item.id.in_(id_prestamos))
        return render_template('item_delete.html', items=free_items)


@app.route('/penalty/list', methods=['GET'])
def penalty_list():
    return render_template('penalty_list.html',
                           penalties=penalty.Penalty.query.all())


@app.route('/penalty/delete', methods=['GET', 'POST'])
def penalty_delete():
    if  request.method == 'POST':
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
