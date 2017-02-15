from .connection import db

class Penalty(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = 1)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))
    sanction_date = db.Column(db.Date, nullable = False)
    penalty_date = db.Column(db.Date, nullable = False)

    def __init__(self, id, user, loan_id, sanction_date, penalty_date):
        '''Constructor del objeto. Los objetos que no pueden ser nulos los ponemos en False
	para poder crear un objeto vacio con los atributos'''
        self.id = id
        self.user = user
	self.loan_id = loan_id
        self.sanction_date = sanction_date
        self.penalty_date = penalty_date

    def __repr__(self):
        '''Imprime los datos del objeto de forma mas elegante'''
        return{
            'id':self.id,
            'user':self.user,
            'loan_id':self.loan_id,
            'sanction_date':self.sanction_date,
            'penalty_date':self.penalty_date
        }
