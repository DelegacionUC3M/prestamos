from flask import Flask, render_template, request
from models.connection import db

# Inicializacion del objeto Flask
app = Flask(__name__)

# Generacion del dict (diccionario) de configuracion desde fichero
app.config.from_pyfile('config.cfg')

# Enlaza la aplicacion y la base de datos
db.app = app
db.init_app(app)

# Url /
@app.route('/')
def index():
    return 'Hola mundo'

@app.route('/prestamo/create', methods=['GET','POST'])
def loan_create():
	if request.method == 'POST':
		return render_template("index.html")
	return render_template("loan_create.html")

if __name__ == '__main__':
    app.run()
