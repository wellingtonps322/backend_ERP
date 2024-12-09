from invoice_reader.core.tools.tools import Tools


class Driver(Tools):

    def __init__(self, driver_data, recorder: object, reader: object, updater: object) -> None:
        self.ID = f'{driver_data['id_driver']
                     }' if driver_data['id_driver'] else None
        self.driver_name = f'{
            driver_data['driver_name']}' if driver_data['driver_name'] else None
        if driver_data['service_center'] == '"SSP30"' or driver_data['service_center'] == '"SSP33"':
            self.service_center = "'SSP30'"
        elif driver_data['service_center'] == '"SSP5"' or driver_data['service_center'] == '"SSP43"':
            self.service_center = "'SSP5'"
        else:
            self.service_center = f'{
                driver_data['service_center']}' if driver_data['service_center'] else None
        self.last_route = f'{
            (driver_data['last_route'])}' if driver_data['last_route'] else None
        self.sector = f'"Operacional"'

        if driver_data['service_type']:

            aggregateFleetChecker = 'Van agregada' in driver_data['service_type'] or 'Utilitário' in driver_data[
                'service_type'] or 'Veículo de passeio' in driver_data['service_type']

            if not aggregateFleetChecker:
                self.function = '"Motorista"'
            else:
                self.function = '"Motorista agregado"'
        else:
            self.function = '"Motorista"'
        self.license_plate = f'{
            (driver_data['license_plate'])}' if driver_data['license_plate'] else None

        self.recorder = recorder
        self.reader = reader
        self.updater = updater

    def isDriverExists(self):
        driver_data = self.reader.getSearchDriverDataByName(
            driver_name=self.driver_name)
        if driver_data:
            if self.isTheSameDriver(driver_data=driver_data):
                self.updateDriverData(driver_data=driver_data)
            else:
                #! GENERATE A WINDOW ALERT
                print('ATENÇÃO: DIVERGÊNCIA DE CADASTRO')
                print(
                    f'Os dados do motorista {driver_data[1]} foram cadastrados na base {driver_data[9]}, \nmas a rota foi feita no service center {self.service_center}')
                self.updateDriverData(driver_data=driver_data)
        else:
            self.insertDriverData()

    # ? New inserts
    def insertDriverData(self):
        self.recorder.setNewDriver(id_driver=self.ID, driver_name=self.driver_name, employee_sector=self.sector, employee_function=self.function,
                                   service_center=self.service_center, license_plate=self.license_plate, last_route=self.last_route)

    # ? Updates
    def updateDriverData(self, driver_data: list):
        self.updateDriverID(driver_id=driver_data[0])
        self.updateEmployeeFunction(
            employee_function=driver_data[7], driver_id=driver_data[0])
        self.updateLastRoute(
            last_route=driver_data[11], driver_id=driver_data[0])

    def updateDriverID(self, driver_id: int):
        if self.ID != 'NULL':
            if self.ID is not driver_id:  # Checking ID
                self.updater.setUpdateDriverNumericData(
                    field_to_insert='ID', data_to_inserted=self.ID, ID=driver_id)

    def updateLastRoute(self, last_route: str, driver_id: int):
        if self.getIsNewDate(old_date=last_route, new_date=self.last_route):
            self.updater.setUpdateDriverStrData(
                'last_route', self.last_route, ID=driver_id)

    def updateEmployeeFunction(self, employee_function: str, driver_id: int):
        if not employee_function in self.function:
            self.updater.setUpdateDriverStrData(
                'employee_function', self.function, ID=driver_id)

    def isTheSameDriver(self, driver_data: list):
        #! The logic is wrong beacuse the driver can work in other hubs
        #! So when work in other hub, It will create a new driver register
        if driver_data[9] in self.service_center:
            return True
        else:
            return False
