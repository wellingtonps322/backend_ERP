from mirror_calculator.core.database.database import Database


class Recorder(Database):
    def __init__(self) -> None:
        super().__init__()

    def insertPaymentData(self, payment_data: dict[list]) -> None:
        try:

            self.connection.start_transaction()
            for services in payment_data.items():
                if services:
                    for service in services[1]:
                        command = f'''
                                    INSERT INTO move_smart.payment_mirrors (id_invoice, period, description, service_center, id_route, employee_id, employee_name, date, license_plate, transaction_type, receipt, stops, addition, value, stop_payment, additional, total, status, observation)
                                    VALUES (
                                        {service['invoice']},
                                        {service['period']},
                                        {service['description']},
                                        {service['serviceCenter']},
                                        {service['routeNumber']},
                                        {service['employeeId']},
                                        {service['employeeName']},
                                        {service['date']},
                                        {service['licensePlate']},
                                        {service['transactionType']},
                                        {service['receipt']},
                                        {service['stops']},
                                        {service['addition']},
                                        {service['value']},
                                        {service['stopPayment']},
                                        {service['additional']},
                                        {service['total']},
                                        {service['status']},
                                        {service['observation']});
                                    '''

                        self.cursor.execute(command)

            self.connection.commit()

            return {'message': 'Payment mirror was inserted sucessfully'}

        except Exception as e:
            print(e.__class__.__name__)
            print(e)
            self.connection.rollback()
