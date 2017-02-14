from .connection import db

class Penalty(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = 1)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))
    sanction_date = db.Column(db.Date, nullable = False)
    penalty_date = db.Column(db.Date, nullable = False)

    def __init__(self, user=None, sanction_date=None, penalty_date=None):
        '''Constructor del objeto. Los objetos que no pueden ser nulos los ponemos en False 
	para poder crear un objeto vacio con los atributos'''
        self.user = user
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
