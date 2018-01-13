from models import item, loan, penalty
from main import db
from datetime import datetime, timedelta, date

current_day = datetime.date(datetime.now())

prestamos = loan.Loan.query.all()

current_penalties = penalty.Penalty.query.all()

for prestamo in prestamos:
    if (prestamo.refund_date < current_day and
            penalty.Penalty.query.filter_by(loan_id=prestamo.id) is None):
        # Objeto que se ha prestado
        object = item.Item.query.get(prestamo.item_id)
        # Calculo para la fecha de penalización
        penalty_date = current_day
        + timedelta(days=abs(current_day.day - prestamo.refund_date.day)
                    * object.penalty_coefficient)

        # Crea la sancion para almacenarla
        sancion = penalty.Penalty(prestamo.user,
                                  prestamo.id,
                                  current_day,
                                  penalty_date)
        db.session.add(sancion)
        db.session.commit()
