from invoice_reader.core.database.database import Database
# from database import Database


class Reader(Database):
    def __init__(self) -> None:
        super().__init__()

    def getPreInvoicePaymentRoute(self, route_number: int) -> None | list:
        self.connection.start_transaction()
        command = ''
        command = f'''
                    SELECT * FROM move_smart.invoice_payment
                    WHERE ID_route = {route_number};
                '''
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        self.connection.commit()
        return result

    def getDriverDataByServiceCenter(self, driver_name: str, service_center: str):
        self.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.employee;
                    WHERE name = {driver_name} AND service_center = {service_center};
                '''
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        self.connection.commit()
        return result

    def getDriverDataByName(self, driver_name: str):
        self.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.employee;
                    WHERE name = {driver_name};
                '''
        self.cursor.execute(command)
        result = self.cursor.fetchall()
        self.connection.commit()
        return result

    def getSearchVehicleData(self, license_plate: str):
        self.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.vehicle
                    WHERE license_plate = {license_plate};
                '''
        self.cursor.execute(command)
        result = self.cursor.fetchone()
        self.connection.commit()
        return result

    def getSearchDriverDataByName(self, driver_name: str):
        command = ''
        if driver_name:
            self.connection.start_transaction()
            command = f'''
                        SELECT * FROM move_smart.employee
                        WHERE name = {driver_name};
                    '''
        if command:
            self.cursor.execute(command)
            result = self.cursor.fetchone()
            self.connection.commit()
            return result

    def getSearchDriverDataByServiceCenter(self, driver_name: str, service_center: str):
        command = ''
        if service_center == 'NULL':
            ...

        if not service_center == 'NULL':
            self.connection.start_transaction()
            command = f'''
                        SELECT * FROM move_smart.employee
                        WHERE driver_name = {driver_name} AND service_center = {service_center};
                    '''
        if command:
            self.cursor.execute(command)
            # print(command)
            result = self.cursor.fetchall()
            self.connection.commit()
            return result

    def getSearchHubFromRouteData(self, route_number: int):
        command = ''
        if route_number:
            self.connection.start_transaction()
            command = f'''
                        SELECT service_center FROM move_smart.invoice_payment
                        WHERE ID_route = {route_number};
                    '''
            self.cursor.execute(command)
            result = self.cursor.fetchall()
            self.connection.commit()
            if result:
                return result[0][0]

    def getRouteData(self, route_number: int):
        command = ''
        if route_number:
            self.connection.start_transaction()
            command = f'''
                        SELECT * FROM move_smart.route
                        WHERE route_number = {route_number};
                    '''
            self.cursor.execute(command)
            result = self.cursor.fetchone()
            self.connection.commit()
            if result:
                return result


if __name__ == '__main__':
    instance = Reader()

    # result = instance.getSearchDriverData(driver_name='Wellingt')
    result = instance.getSearchHubFromRouteData(route_number=102745133)
    print(result)
