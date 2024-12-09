from invoice_reader.core.tools.tools import Tools


class AdditionalPayments(Tools):

    def __init__(self, reader) -> None:
        super().__init__(reader=reader)

    def isAddittionalPayment(self, series_body):

        if 'Visited addresses' in series_body['Descrição']:
            return True
        return False

    def getData(self, series_body, preinvoice_header):
        row_payment_dict = {
            'invoice': 'NULL',
            'payment_type': 'NULL',
            'service_center': 'NULL',
            'data_type': '"ADDITIONAL_PAYMENT"',
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
        row_payment_dict['payment_type'] = self.getCheckingServiceType(
            series_body)
        # ? ID route
        row_payment_dict['id_route'] = self.getIDRoute(row=series_body)
        # ? Service center checking
        row_payment_dict['service_center'] = self.getCheckingServiceCenter(
            series_body, route_number=row_payment_dict['id_route'])
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
