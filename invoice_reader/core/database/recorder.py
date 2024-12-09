from invoice_reader.core.database.database import Database
from mysql.connector import IntegrityError
import sys


class Recorder(Database):

    def __init__(self) -> None:
        super().__init__()

    def setInvoiceInformation(self, invoice) -> dict:
        try:
            self.connection.start_transaction()
            command = f'''
                        INSERT INTO move_smart.invoice_information (id, product, country, shipping_company, mille, period, invoice_type, invoice_status)
                        VALUE ({invoice['id_invoice']}, {invoice['product']}, {invoice['country']}, {invoice['shipping_company']}, {
                invoice['mille']}, {invoice['period']}, {invoice['invoice_type']}, {invoice['invoice_status']});
                    '''
            self.cursor.execute(command)
            self.connection.commit()
            return {"message": "Invoice inserted successfully"}
        except IntegrityError as e:
            print('Error:', e.__class__.__name__)
            print(e)
            self.connection.rollback()
            return {"duplicity": "This invoice already inserted"}

        except e:
            print('Error:', e.__class__.__name__)
            print(e)
            self.connection.rollback()
            return {"error": "Some error to insert invoice"}

    def setInvoicePayment(self, row_payment_dict: dict):
        # try:
        self.connection.start_transaction()
        command = f'''
                        INSERT INTO move_smart.invoice_payment (invoice, id_route, service_center, data_type, service_type, kms_range, special_day, part_time_route,
                        ambulance, start_date, end_date, license_plate, driver, quantity, unit_price, total)
                        VALUES ({row_payment_dict['invoice']}, {row_payment_dict['id_route']}, {row_payment_dict['service_center']}, {row_payment_dict['data_type']},
                        {row_payment_dict['service_type']}, {row_payment_dict['kms_range']}, {
            row_payment_dict['special_day']}, {row_payment_dict['part_time_route']},
                        {row_payment_dict['ambulance']}, {row_payment_dict['start_date']}, {
            row_payment_dict['end_date']}, {row_payment_dict['license_plate']},
                        {row_payment_dict['driver']}, {row_payment_dict['quantity']}, {row_payment_dict['unit_price']}, {row_payment_dict['total']});
                    '''
        self.cursor.execute(command)
        self.connection.commit()
        # except Exception as e:
        #     print('Error:', e.__class__.__name__)
        #     print(e)
        #     self.connection.rollback()

    def setInvoiceDiscount(self, row_discount_dict: dict):
        # try:
        self.connection.start_transaction()
        command = f'''
                        INSERT INTO move_smart.invoice_discount (invoice, id_route, service_center, data_type, discount_type, id_complaint, complaint_date,
                        license_plate_complaint, start_date, end_date, license_plate, driver, quantity, unit_price, total)
                        VALUES ({row_discount_dict['invoice']}, {row_discount_dict['id_route']}, {row_discount_dict['service_center']}, {row_discount_dict['data_type']},
                        {row_discount_dict['discount_type']}, {row_discount_dict['id_complaint']}, {
            row_discount_dict['complaint_date']},
                        {row_discount_dict['license_plate_complaint']}, {
            row_discount_dict['start_date']}, {row_discount_dict['end_date']},
                        {row_discount_dict['license_plate']}, {row_discount_dict['driver']}, {
            row_discount_dict['quantity']}, {row_discount_dict['unit_price']},
                        {row_discount_dict['total']});'''
        self.cursor.execute(command)
        self.connection.commit()
        # except Exception as e:
        #     print('Error:', e.__class__.__name__)
        #     print(e)
        #     self.connection.rollback()

    def setInvoiceAdditionalPayment(self, row_payment_dict: dict):
        # try:
        self.connection.start_transaction()
        command = f'''
                        INSERT INTO move_smart.invoice_additional_payment (invoice, id_route, service_center, data_type,
                        payment_type, start_date, end_date, license_plate, driver, quantity, unit_price, total)
                        VALUES ({row_payment_dict['invoice']}, {row_payment_dict['id_route']}, {row_payment_dict['service_center']}, {row_payment_dict['data_type']},
                        {row_payment_dict['payment_type']}, {row_payment_dict['start_date']}, {
            row_payment_dict['end_date']}, {row_payment_dict['license_plate']},
                        {row_payment_dict['driver']}, {row_payment_dict['quantity']}, {row_payment_dict['unit_price']}, {row_payment_dict['total']});
                    '''
        self.cursor.execute(command)
        self.connection.commit()
        # except Exception as e:
        #     print('Error:', e.__class__.__name__)
        #     print(e)
        #     self.connection.rollback()

    def setPreInvoiceDiscountsWithoutRoute(self, row_discount_dict: dict):
        # try:
        self.connection.start_transaction()
        command = f'''
                        INSERT INTO move_smart.invoice_discount_without_route (invoice, ID_route, service_center, data_type, discount_type, ID_complaint,
                        complaint_date, license_plate_complaint, start_date, end_date, license_plate, driver, quantity, unit_price, total, discount_status)
                        VALUES ({row_discount_dict['invoice']}, {row_discount_dict['id_route']},{row_discount_dict['service_center']}, {row_discount_dict['data_type']},
                        {row_discount_dict['discount_type']}, {row_discount_dict['id_complaint']}, {
            row_discount_dict['complaint_date']},
                        {row_discount_dict['license_plate_complaint']}, {
            row_discount_dict['start_date']}, {row_discount_dict['end_date']},
                        {row_discount_dict['license_plate']}, {row_discount_dict['driver']}, {
            row_discount_dict['quantity']}, {row_discount_dict['unit_price']},
                        {row_discount_dict['total']}, "SEM STATUS");'''
        self.cursor.execute(command)
        self.connection.commit()
        # except Exception as e:
        #     print('Error:', e.__class__.__name__)
        #     print(e)
        #     self.connection.rollback()

    def setNewVehicle(self, license_plate: str, service_center: str, driver: str, last_route: str, license_plate_type: str, service_type: str):
        # try:
        self.connection.start_transaction()
        command = f'''
                        INSERT INTO move_smart.vehicle (license_plate, service_center, driver, last_route, license_plate_type, service_type)
                        VALUES ({license_plate}, {service_center}, {driver}, {last_route}, {license_plate_type}, {service_type})'''
        self.cursor.execute(command)
        self.connection.commit()
        # except Exception as e:
        #     print('Error:', e.__class__.__name__)
        #     print(e)
        #     self.connection.rollback()

    def setNewDriver(self, id_driver, driver_name, employee_sector, employee_function, service_center, license_plate, last_route):
        command = None

        if id_driver != 'NULL' and service_center != 'NULL':
            # try:
            self.connection.start_transaction()
            command = f'''
                            INSERT INTO move_smart.employee (id, name, employee_sector, employee_function, status, service_center, license_plate, last_route)
                            VALUES({id_driver}, {driver_name}, {employee_sector}, {
                employee_function}, "Ativo", {service_center},{license_plate}, {last_route});
                        '''
            if command:
                self.cursor.execute(command)
                self.connection.commit()
        # except Exception as e:
        #     print('Error:', e.__class__.__name__)
        #     print(e)
        #     self.connection.rollback()

        if id_driver == 'NULL' and service_center != 'NULL':
            # try:
            self.connection.start_transaction()
            command = f'''
                            INSERT INTO move_smart.employee (name, employee_sector, employee_function, service_center, license_plate, last_route)
                            VALUES({driver_name}, {employee_sector}, {employee_function}, {
                service_center},{license_plate}, {last_route});
                        '''
            if command:
                self.cursor.execute(command)
                self.connection.commit()
            # except Exception as e:
            #     print('Error:', e.__class__.__name__)
            #     print(e)
            #     self.connection.rollback()
        else:
            print('ATENÇÃO: ERRO NA INSERÇÃO DE DADOS DO MOTORISTA.')
            print(
                'Por falta de dados na pré-fatura, não foi possível realizar o cadastro automático do motorista')
            print('Por favor, faça o cadastro manualmente')

    def updateDriverData(self, updates: list, datas: list, driver_name: str):
        # Inform what updates will be done
        # Informe what datas will be inserted inside the database

        def updatePlate(plate: str):
            ...


if __name__ == '__main__':
    recorder = Recorder()

    recorder.test()
