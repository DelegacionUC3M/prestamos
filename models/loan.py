from .connection import db

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    user = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    loan_date = db.Column(db.Date, nullable=False)
    refund_date = db.Column(db.Date)

    def __init__(self, item_id, user, amount, loan_date, refund_date=None):
        self.item_id = item_id
        self.user = user
        self.amount = amount
        self.loan_date = loan_date
        self.refund_date = refund_date

    def __repr__(self):
        return str({'id':self.id, 'item_id':self.item_id, 'user':self.user,
                    'amount':self.amount, 'loan_date':self.loan_date, 'refund_date':self.refund_date})
