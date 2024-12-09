from datetime import datetime


class Tools():

    def __init__(self, reader: object) -> None:
        self.reader = reader

    def str_to_date(self, date_str: str, input_format: str,):
        try:
            date = datetime.strptime(date_str, input_format)
            str_date = date.strftime('%Y-%m-%d')
            return str_date

        except ValueError as e:
            return 'NULL'

    def getIsNewDate(self, old_date: str, new_date: str):
        try:
            old_date_formated = datetime.strptime(old_date, '%d/%m/%Y')
            new_date_formated = datetime.strptime(new_date, '"%d/%m/%Y"')
            if new_date_formated > old_date_formated:
                return True
            else:
                return False
        except ValueError as e:
            return None

    def SetDataInLine(self, dataframe, line, column, row):
        dataframe.loc[line, row[column]]

    def getCheckingServiceType(self, series):
        service_type_list = [
            'Rental Utilitário com Ajudante',
            'Rental Utilitário sem Ajudante',
            'Utilitário',
            'Van Frota Fixa - Equipe dupla',
            'Van Frota Fixa - Equipe única',
            'Van Média Elétrica',
            'Yellow Pool Large Van – Equipe dupla',
            'Yellow Pool Large Van – Equipe única',
            'Veículo de Passeio',
            'Vuc',
            'Van -',
            'Rental IHDS Electric 2P',
            'Visited addresses',
            'Lost Packages Penalty',
            'Pnr Packages Penalty',
            'Vehicle Daily Not Visited'
        ]
        for service_type in service_type_list:

            if service_type in series['Descrição']:
                if service_type == 'Van -':
                    return '"Van agregada"'

                if 'Frota Fixa' in service_type:
                    service_type_formated = service_type.replace(
                        'Frota Fixa - ', '').lower().capitalize()
                    return f'"{service_type_formated}"'

                if 'Large Van' in service_type:
                    service_type_formated = service_type.replace(
                        'Large Van – ', '').lower().capitalize()
                    return f'"{service_type_formated}"'

                if 'Van Média Elétrica' in service_type:
                    return '"Van elétrica"'

                if 'Rental IHDS Electric 2P' in service_type:
                    return '"Rental IHDS Electric 2P"'

                return f'"{service_type.lower().capitalize()}"'

        return 'NULL'

    def getCheckingServiceCenter(self, series: dict, route_number: int) -> str:
        '''
            Check if the service center is in the description
            If true, the function extract the service center code

            If false, probability is a discount payment
            So it search in the routes to extract the service center code
        '''
        service_center_list = [
            'SVC: SC_ZS',
            'SVC: SSP5',
            'SVC: SSP7',
            'SVC: SSP10',
            'SVC: SSP12',
            'SVC: SSP17',
            'SVC: SSP21',
            'SVC: SSP25',
            'SVC: SSP30',
            'SVC: SSP33',
            'SVC: SSP34',
            'SVC: SSP43',
        ]
        for service_center in service_center_list:
            if service_center in series['Descrição']:
                return f'"{service_center.split()[1].strip()}"'
        service_center = ''
        service_center = self.reader.getSearchHubFromRouteData(
            route_number=route_number)
        if service_center:
            return f'"{service_center}"'

        return 'NULL'

    def getKmsRange(self, series: dict) -> str | None:
        '''
            Check if the km range is in the description
            If true, it is extracted and the function return the number
            of km range
        '''

        if 'kms range:' in series['Descrição'].lower():

            km_range = series['Descrição'].lower().split(sep='kms range:')
            km_range = km_range[1].split()

            return f'"{km_range[0]}"'

        return 'NULL'

    def getCheckingSpecialDay(self, series):
        special_day_list = [
            'HOLIDAY DAY ROUTE',
            'SATURDAY DAY ROUTE',
        ]
        for special_day in special_day_list:
            if special_day in series['Descrição']:
                return f'"{special_day}"'

        return 'NULL'

    def getCheckingPartTimeRoute(self, reader, series):
        if 'PART TIME ROUTE' in series['Descrição']:
            return True

        # route_data = reader.getRouteData(series['ID da rota'])
        # if route_data:
        #     start_route_hour = route_data[14]
        #     if start_route_hour:
        #         hour = int(start_route_hour.split(":")[0])
        #         if hour >= 12:
        #             return True

        return 'NULL'

    def getCheckingAmbulance(self, series):
        if 'AMBULANCE' in series['Descrição']:
            return True
        return 'NULL'

    def getIDRoute(self, row):
        if row['ID da rota'].isnumeric():
            id_route = int(row['ID da rota'])
            return id_route
        return 'NULL'

    def getDate(self, row, column):
        if row['Data de início']:
            date = str(row[column]).strip()
            return f'"{date}"'
        return 'NULL'

    def getLicensePlateComplaint(self, series: dict, discount_type: str):

        # ? Lost Packages Penalty
        if 'Lost packages penalty' in discount_type or 'Pnr packages penalty' in discount_type:
            license_plate = series['Descrição'].split(
                sep=':')[1].split()[0].strip()

            return f'"{license_plate}"'

        # ? Vehicle Daily Not Visited
        if 'Vehicle daily not visited' in discount_type:
            license_plate = series['Descrição'].split(
                sep='>')[1].split()[1].strip()

            return f'"{license_plate}"'

        return 'NULL'

    def getComplaintDate(self, series: dict, discount_type: str):

        # ? Lost Packages Penalty
        if 'Lost packages penalty' in discount_type or 'Pnr packages penalty' in discount_type:
            date = series['Descrição'].split(sep=':')[1].split()[1].strip()

            return f'"{date}"'

        # ? Vehicle Daily Not Visited
        if 'Vehicle daily not visited' in discount_type:
            date = series['Descrição'].split(sep='>')[1].split()[2].strip()

            return f'"{date}"'

        return 'NULL'

    def getIdComplaint(self, series: dict, discount_type: str):

        if 'Lost packages penalty' in discount_type or 'Pnr packages penalty' in discount_type:
            id_complaint = series['Descrição'].split(
                sep=':')[1].split()[2].strip()

            if id_complaint:
                return int(id_complaint)

            return 'NULL'

        return 'NULL'

    #! Check this metod, I do not test yet
    def getIdDriver(self, description):
        id_driver = description.split()[4].replace('#', '').strip()
        return int(id_driver)

    def areRouteInPaymentDB(self, route_number):
        route_data = self.reader.getPreInvoicePaymentRoute(
            route_number=route_number)

        if route_data:
            return True
        return False


if __name__ == '__main__':
    tools = Tools()
    date = tools.str_to_date('17/07/2023', '%d/%m/%Y')
    print(date)
