from mirror_calculator.core.database.database import Database


class Reader(Database):
    def __init__(self) -> None:
        super().__init__()

    def getInvoiceIdByPeriod(self, period: str) -> list:
        self.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.invoice_information
                    WHERE period = '{period}';
                    '''
        self.cursor.execute(command)
        result = self.cursor.fetchone()  # Read the database
        self.connection.commit()
        return result

    def getAllServiceCenterData(self) -> list[list]:
        self.connection.start_transaction()
        command = f'''
                    SELECT service_center, daily_payment_condition, pay_per_stop_checker, pay_per_stop_condition
                    FROM move_smart.hub
                    '''
        self.cursor.execute(command)
        result = self.cursor.fetchall()  # Read the database
        self.connection.commit()
        return result

    # ? Daily payment data
    def getAllDailyPaymentsData(self, invoice: int) -> list | list[list]:
        self.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.invoice_payment
                    WHERE invoice = {invoice};
                    '''
        self.cursor.execute(command)
        result = self.cursor.fetchall()  # Read the database
        self.connection.commit()
        return result

    # ? Additional payment data
    def getAllAdditionalPaymentsData(self, invoice: int) -> list | list[list]:
        self.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.invoice_additional_payment
                    WHERE invoice = {invoice};
                    '''
        self.cursor.execute(command)
        result = self.cursor.fetchall()  # Read the database
        self.connection.commit()
        return result

    # ? Discount payment data
    def getAllPaymentsDiscountsData(self, invoice: int) -> list | list[list]:
        self.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.invoice_discount
                    WHERE invoice = {invoice};
                    '''
        self.cursor.execute(command)
        result = self.cursor.fetchall()  # Read the database
        self.connection.commit()
        return result

    # ? Route data

    def getRouteDataById(self, id: int) -> list:
        self.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.route
                    WHERE route_number = {id};
                    '''
        self.cursor.execute(command)
        result = self.cursor.fetchone()  # Read the database
        self.connection.commit()
        return result

    # ? Calculed values

    def getCalculedValueFromDatabase(self, id: int, transaction_type: str) -> list:
        self.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.payment_mirrors
                    WHERE route_number = {id} AND transaction_type = {transaction_type};
                    '''
        self.cursor.execute(command)
        result = self.cursor.fetchone()  # Read the database
        self.connection.commit()
        return result

    # ? Employee data

    def getEmployeeIdByName(self, employee_name: str) -> int:
        self.connection.start_transaction()
        command = f'''
                    SELECT id FROM move_smart.employee
                    WHERE name = '{employee_name}';
                    '''
        self.cursor.execute(command)
        result = self.cursor.fetchone()  # Read the database
        self.connection.commit()
        if result:
            return result[0]
        return None

    def getAllPeriodsFromInvoiceInformation(self):
        self.connection.start_transaction()
        command = f'''
                    SELECT `period` FROM `move_smart`.`invoice_information`;
                    '''
        self.cursor.execute(command)
        result = self.cursor.fetchall()  # Read the database
        self.connection.commit()
        return result
