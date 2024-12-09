from invoice_reader.core.tools.tools import Tools


class Payments(Tools):

    def __init__(self, reader) -> None:

        self.reader = reader
        self.service_type_list = [
            'Rental Utilitário com Ajudante',
            'Rental Utilitário sem Ajudante',
            'Utilitários',
            'Van Frota Fixa',
            'Van Média Elétrica',
            'Veículo de Passeio',
            'Vuc',
            'Yellow Pool Large Van',
            'Van -',
            'Rental IHDS Electric 2P',
        ]

    def isPayment(self, series_body):

        for service_type in self.service_type_list:
            if service_type in series_body['Descrição']:
                return True
        return False

    def getData(self, series_body, preinvoice_header):
        row_payment_dict = {
            'invoice': 'NULL',
            'service_type': 'NULL',
            'service_center': 'NULL',
            'data_type': '"PAYMENT"',
            'kms_range': 'NULL',
            'special_day': 'NULL',
            'part_time_route': False,
            'ambulance': False,
            'id_route': 'NULL',
            'start_date': 'NULL',
            'end_date': 'NULL',
            'license_plate': 'NULL',
            'id_driver': 'NULL',
            'driver': 'NULL',
            'quantity': 'NULL',
            'unit_price': 'NULL',
            'total': 'NULL'
        }

        # ? Invoice Number
        row_payment_dict['invoice'] = preinvoice_header['ID pré-fatura']

        # ? Service type checking
        row_payment_dict['service_type'] = self.getCheckingServiceType(
            series_body)
        # ? ID route
        row_payment_dict['id_route'] = self.getIDRoute(row=series_body)
        # ? Service center checking
        row_payment_dict['service_center'] = self.getCheckingServiceCenter(
            series_body, route_number=row_payment_dict['id_route'])
        # ? KMs range
        row_payment_dict['kms_range'] = self.getKmsRange(series_body)
        # ? Special day
        row_payment_dict['special_day'] = self.getCheckingSpecialDay(
            series_body)
        # ? Part time route
        row_payment_dict['part_time_route'] = self.getCheckingPartTimeRoute(
            self.reader, series_body)
        # ? Ambulance
        row_payment_dict['ambulance'] = self.getCheckingAmbulance(series_body)
        # ? Start date
        row_payment_dict['start_date'] = self.getDate(
            row=series_body, column='Data de início')
        # ? End date
        row_payment_dict['end_date'] = self.getDate(
            row=series_body, column='Data de término')
        # ? License plate
        if series_body['Placa']:
            row_payment_dict['license_plate'] = f'"{series_body['Placa']}"'
        # ? Driver
        if series_body['Motorista']:
            row_payment_dict['driver'] = f'"{
                series_body['Motorista'].upper()}"'
        # ? Driver ID
        if 'Visited addresses' in series_body['Descrição']:
            row_payment_dict['id_driver'] = self.getIdDriver(
                description=series_body['Descrição'])
        # ? Quantity
        if series_body['Quantidade']:
            row_payment_dict['quantity'] = int(series_body['Quantidade'])
        # ? Unit price
        if series_body['Preço unitário']:
            row_payment_dict['unit_price'] = float(
                series_body['Preço unitário'])
        # ? Total
        if series_body['Total']:
            row_payment_dict['total'] = float(series_body['Total'])

        return row_payment_dict
