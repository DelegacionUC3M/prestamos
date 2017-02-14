from .connection import db

class loan (db.Model):

    id = db.Column(db.Integer,primary_Key=True,autoincrement=1)
    item_id = db.Column(db.Integer, db.ForeignKey ('item.id'))
    user = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    loan_date = db.Column(db.Date, nullable=False)
    refund_date = db.Column(db.Date)

    def __init__(self, id, item_id, user, amount, loan_date, refund_date=None):
        self.id = id
        self.item_id = item_id
        self.user = user
        self.amount = amount
        self.loan_date = loan_date
        self.refund_date = refund_date

    def __repr__(self):
        return "Loan id=%s, item_id=%s, user=%s, amount=%s, loan_date=%s, refund_date=%s" % 
                (self.id, self.item_id, self.user, self.amount, self.loan_date, self.refund_date)