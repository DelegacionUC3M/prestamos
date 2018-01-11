from flask import Flask, render_template, request, flash
from models import item, loan
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
        deleted_loan = loan.Loan.query.get(
            int(request.form.get('comp_select')))
        object = item.Item.query.get(deleted_loan.item_id)
        # Devuelve los objetos prestados a la db
        object.amount += deleted_loan.amount
        # Elimina el prestamo de la db
        db.session.delete(deleted_loan)
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
        # Obtiene el objeto de la db cuya id
        # corresponda con la del formulario
        object = item.Item.query.get(
            int(request.form.get('comp_select')))
        # Busca el objeto a borrar en la lista de préstamos
        loan_object = loan.Loan.query.filter_by(
            item_id=request.form.get('comp_select'))

        # Elimina el objeto de la db PERMANENTEMENTE
        if object.amount > 0:
            db.session.delete(object)
            db.session.commit()
            return render_template("index.html",
                                   items=item.Item.query.all(),
                                   loans=loan.Loan.query.all())
    else:
        return render_template('item_delete.html',
                               items=item.Item.query.all())


if __name__ == '__main__':
    app.run()
