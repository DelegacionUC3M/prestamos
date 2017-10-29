from flask import Flask, render_template, request, flash
from models import item, loan, penalty
from models.connection import db
from datetime import datetime, timedelta

# Inicializacion del objeto Flask
app = Flask(__name__)

# Generacion del dict (diccionario) de configuracion desde fichero
app.config.from_pyfile('config.cfg')

# Enlaza la aplicacion y la base de datos
db.app = app
db.init_app(app)
db.create_all()


# Url /
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/prestamo/create', methods=['GET','POST'])
def loan_create():
    if request.method == 'POST':
        object = item.Item.query.get(int(request.form.get('comp_select')))
        loan_date = datetime.strptime(request.form['loan_date'], "%Y-%m-%d")
        refund_date = loan_date + timedelta(days=object.loan_days)

        prestamo_data = loan.Loan(request.form.get('comp_select'), int(request.form['user']), int(request.form['amount']),
                                  request.form['loan_date'], refund_date)
        db.session.add(prestamo_data)
        db.session.commit()
        return render_template("index.html")
    else:
        return render_template("loan_create.html", items = item.Item.query.all())



@app.route('/objeto/crear', methods=['GET','POST'])
def item_create():
    if request.method == 'POST':
        loan_item = item.Item(str(request.form['name']), int(request.form['amount']),
                                  str(request.form['type']), str(request.form['state']),
                                  int(request.form['loan_days']), float(request.form['penalty_coefficient']))

        db.session.add(loan_item)
        db.session.commit()
        return render_template("index.html")
    else:
        return render_template('item_create.html')


if __name__ == '__main__':
    app.run()
