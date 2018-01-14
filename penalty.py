from models import item, loan, penalty
from main import db
from datetime import datetime, timedelta, date

current_day = datetime.date(datetime.now())  # Fecha actual
prestamos = loan.Loan.query.all()  # Lista de prestamos
current_penalties = penalty.Penalty.query.all()  # Lista actual de sanciones

for prestamo in prestamos:
    sancion = penalty.Penalty.query.filter_by(loan_id=prestamo.id)
    # Si el objeto no se ha devuelto y no aparece en la lista de sanciones
    if (prestamo.refund_date < current_day and sancion is None):
        # Objeto que se ha prestado para el coeficiente
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
    # Si la sanción ya existe, se recalcula la fecha
    elif sancion is not None:
        # Recalculo para la fecha de penalización
        penalty_date = current_day
        + timedelta(days=abs(current_day.day - prestamo.refund_date.day)
                    * object.penalty_coefficient)
        # Actualiza la fecha de penalización
        sancion.penalty_date = penalty_date
        db.session.commit()
