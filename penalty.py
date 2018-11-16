from datetime import datetime, timedelta

from main import db
from models import item, loan, penalty

current_day = datetime.date(datetime.now())  # Fecha actual
# Lista de prestamos que aun no se han devuelto
prestamos = loan.Loan.query.filter_by(refund_date=None)

for prestamo in prestamos:
    sancion = penalty.Penalty.query.filter_by(loan_id=prestamo.id)

    object = item.Item.query.get(prestamo.item_id)

    fecha_devolucion = prestamo.loan_date + timedelta(days=object.loan_days)

    # Si el objeto no se ha devuelto y no aparece en la lista de sanciones
    if (sancion.count() == 0 and fecha_devolucion < current_day):
        # Calculo para la fecha de penalización
        penalty_date = current_day + \
            timedelta(days=abs(current_day.day - fecha_devolucion.day)
                      * object.penalty_coefficient)

        db_penalty = penalty.Penalty(prestamo.nia,
                                     prestamo.id,
                                     current_day,
                                     penalty_date)
        db.session.add(db_penalty)
        db.session.commit()
    # Si la sanción ya existe, se recalcula la fecha
    elif (sancion.count() > 0 and fecha_devolucion < current_day):
        # Recalculo para la fecha de penalización
        new_date = current_day + \
            timedelta(days=abs(current_day.day - fecha_devolucion.day)
                      * object.penalty_coefficient)

        # Actualiza la fecha de penalización
        sancion.penalty_date = new_date
        db.session.commit()
    # Si la sancion ya ha pasado eliminarla
    else:
        sancion.penalty_date = current_day
        db.session.commit()
