from invoice_reader.core.tools.tools import Tools


class Vehicle(Tools):

    def __init__(self, vehicle_data, recorder: object, reader: object, updater: object) -> None:
        self.license_plate = f'{
            vehicle_data['license_plate']}' if vehicle_data['license_plate'] else None
        self.driver = f'{vehicle_data['driver']
                         }' if vehicle_data['driver'] else None
        if vehicle_data['service_center'] == 'SSP30' or vehicle_data['service_center'] == 'SSP33':
            self.service_center = "'SSP30'"
        elif vehicle_data['service_center'] == 'SSP5' or vehicle_data['service_center'] == 'SSP43':
            self.service_center = "'SSP5'"
        else:
            self.service_center = f'{vehicle_data['service_center']}'
        self.last_route = f'{
            vehicle_data['last_route']}' if vehicle_data['last_route'] else None
        self.service_type = f'{
            vehicle_data["service_type"]}' if vehicle_data["service_type"] else None

        if vehicle_data['service_type']:

            aggregateFleetChecker = 'Van agregada' in vehicle_data['service_type'] or 'Utilitário' in vehicle_data[
                'service_type'] or 'Veículo de passeio' in vehicle_data['service_type']

            if not aggregateFleetChecker:
                self.license_plate_type = '"Frota fixa"'
            else:
                self.license_plate_type = '"Frota agregada"'
        else:
            self.license_plate_type = '"Frota fixa"'

        self.recorder = recorder
        self.reader = reader
        self.updater = updater

    def isVehicleExists(self):
        vehicle_data = self.reader.getSearchVehicleData(
            license_plate=self.license_plate)

        if vehicle_data:
            self.updateVehicleData(vehicle_data)
        else:
            self.insertVehicleData()

    # ? New Inserts
    def insertVehicleData(self):
        self.recorder.setNewVehicle(
            license_plate=self.license_plate, service_center=self.service_center, driver=self.driver, last_route=self.last_route, license_plate_type=self.license_plate_type, service_type=self.service_type)

    # ? Updates
    def updateVehicleData(self, vehicle_data):
        self.updateVehicleDriver(vehicle_data[3])
        self.updateVehicleAssistant(vehicle_data[3])
        self.updateVehicleServiceType(vehicle_data[7])
        self.updateLastRoute(last_route=vehicle_data[5])

    def updateLastRoute(self, last_route: str):
        #! Check if the date is after of the last route
        if self.getIsNewDate(old_date=last_route, new_date=self.last_route):
            self.updater.setUpdateVehicleStrData(
                field_to_insert='last_route', data_to_insert=self.last_route, field_to_check='license_plate', data_to_check=self.license_plate)

    def updateVehicleDriver(self, driver: str):
        if driver is None or not driver in self.driver:
            self.updater.setUpdateVehicleStrData(field_to_insert='driver', data_to_insert=f'{
                                                 self.driver}', field_to_check='license_plate', data_to_check=f'{self.license_plate}')

    def updateVehicleAssistant(self, driver: str):
        if driver is None or not driver in self.driver:
            self.updater.setUpdateVehicleStrData(
                field_to_insert='assistant', data_to_insert=f'NULL', field_to_check='license_plate', data_to_check=f'{self.license_plate}')

    def updateVehicleServiceType(self, service_type: str):
        if service_type is None or not service_type in self.service_type:
            self.updater.setUpdateVehicleStrData(field_to_insert='service_type', data_to_insert=f'{
                                                 self.service_type}', field_to_check='license_plate', data_to_check=f'{self.license_plate}')
