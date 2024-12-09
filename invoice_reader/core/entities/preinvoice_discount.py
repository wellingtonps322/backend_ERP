from invoice_reader.core.tools.tools import Tools

from operator import neg


class Discounts(Tools):

    def __init__(self, reader) -> None:
        super().__init__(reader=reader)

    def isDiscount(self, series_body):
        if 'Lost Packages Penalty' in series_body['Descrição'] or 'Pnr Packages Penalty' in series_body['Descrição'] or 'Vehicle Daily Not Visited' in series_body['Descrição']:
            return True
        return False

    def getData(self, series_body, preinvoice_header):
        row_discount_dict = {
            'invoice': 'NULL',
            'id_route': 'NULL',
            'service_center': 'NULL',
            'data_type': '"DISCOUNT"',
            'discount_type': 'NULL',
            'id_complaint': 'NULL',
            'complaint_date': 'NULL',
            'license_plate_complaint': 'NULL',
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
        row_discount_dict['invoice'] = int(preinvoice_header['ID pré-fatura'])
        # ? ID route
        row_discount_dict['id_route'] = self.getIDRoute(row=series_body)
        # ? Service center checking
        # Create the funcion that search for service_center
        row_discount_dict['service_center'] = self.getCheckingServiceCenter(
            series_body, route_number=row_discount_dict['id_route'])
        # ? Discount type checking
        row_discount_dict['discount_type'] = self.getCheckingServiceType(
            series_body)
        # ? Id complaint
        row_discount_dict['id_complaint'] = self.getIdComplaint(
            series_body, row_discount_dict['discount_type'])
        # ? Complaint date
        row_discount_dict['complaint_date'] = self.getComplaintDate(
            series_body, row_discount_dict['discount_type'])
        # ? License plate complaint
        row_discount_dict['license_plate_complaint'] = self.getLicensePlateComplaint(
            series_body, row_discount_dict['discount_type'])
        # ? Start date
        row_discount_dict['start_date'] = self.getDate(
            row=series_body, column='Data de início')
        # ? End date
        row_discount_dict['end_date'] = self.getDate(
            row=series_body, column='Data de término')
        # ? License plate
        if series_body['Placa']:
            row_discount_dict['license_plate'] = f'"{series_body['Placa']}"'
        # ? Driver
        if series_body['Motorista']:
            row_discount_dict['driver'] = f'"{
                series_body['Motorista'].upper()}"'
        # ? Driver ID
        if 'Visited addresses' in series_body['Descrição']:
            row_discount_dict['id_driver'] = self.getIdDriver(
                series_body=series_body['Descrição'])
        # ? Quantity
        if series_body['Quantidade']:
            row_discount_dict['quantity'] = int(series_body['Quantidade'])
        # ? Unit price
        if series_body['Preço unitário']:
            aux_number = 0
            aux_number = float(series_body['Preço unitário'])
            if aux_number > 0:
                row_discount_dict['unit_price'] = neg(aux_number)
            if aux_number < 0:
                row_discount_dict['unit_price'] = aux_number
        # ? Total
        if series_body['Total']:
            aux_number = 0
            aux_number = float(series_body['Total'])
            if aux_number > 0:
                row_discount_dict['total'] = neg(aux_number)
            if aux_number < 0:
                row_discount_dict['total'] = aux_number

        return row_discount_dict
