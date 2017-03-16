from .connection import db


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    # barcode = db.Column()
    state = db.Column(db.Text, nullable=False)
    loan_days = db.Column(db.Integer, nullable=False)
    penalty_coefficient = db.Column(db.Float, nullable=False)

    def __init__(self, name=None, amount=None, type=None, penalty_coefficient=None, state=None, loan_days=None):
        self.name = name
        self.amount = amount
        self.type = type
        self.state = state
        self.loan_days = loan_days
        self.penalty_coefficient = penalty_coefficient

    def __repr__(self):
        return str({
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'type': self.type,
            'state': self.state,
            'loan_days': self.loan_days,
            'penalty_coefficient': self.penalty_coefficient
        })
