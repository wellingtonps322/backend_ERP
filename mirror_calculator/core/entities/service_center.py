import json
from operator import neg


class ServiceCenter():

    def __init__(
            self,
            id,
            daily_payment_condition,
            pay_per_stop_checker,
            pay_per_stop_condition
    ) -> None:
        self.id = id
        self.daily_payment_condition = json.loads(
            daily_payment_condition) if daily_payment_condition else None
        self.pay_per_stop_checker = pay_per_stop_checker

        # ! Criar uma função construtora que crie funções com os parâmetros vindos do banco de dados para calcular as paradas
        if self.pay_per_stop_checker:
            self. payStopCalculator = self.payStopCalculatorGenerator(
                pay_per_stop_condition)

    def is_valid_number(self, number):
        try:
            float(number)
            return True
        except ValueError:
            return False

    def getServiceValue(self, reader: object, employee_id: int, service: list, invoice_period: str, route_data: list, services_value_data: dict[list]) -> dict:
        ''' Essa função retorna o cálculo do serviço em um dicionário com todos os valores necessários para compor o espelho de pagamento do colaborador
        '''
        if service and len(service) > 1:
            # O tipo de transação está na posição 4 da lista
            match service[4]:
                case 'PAYMENT':
                    service_value = self.dailyPaymentCalculator(employee_id,
                                                                service, invoice_period, route_data)
                    return service_value

                case 'ADDITIONAL_PAYMENT':
                    return 'PRODUCAO'
                case 'DISCOUNT':
                    service_value = self.dailyDiscountFormatter(reader, employee_id,
                                                                service, invoice_period, route_data, services_value_data)
                    return service_value
                case _:
                    print('Invalid option')
                    return 'PRODUCAO'

    # * PAYMENT

    def dailyPaymentCalculator(self, employee_id: int, service: list, invoice_period: str, route_data: list) -> dict:

        serviceValue = {
            'invoice': service[0],
            'period': invoice_period,
            'description': service[3],
            'serviceCenter': service[2],
            'routeNumber': service[1],
            'employeeId': employee_id,
            'employeeName': service[12],
            'date': service[9],
            'licensePlate': service[11],
            'transactionType': 'PAGAMENTO',
            'receipt': float(service[15]),
            'stops': route_data[16] if route_data else 0,
            'addition': 0,
            'value': 0,
            'stopPayment': 0,
            'additional': 0,
            'total': 0,
            'status': 'PENDENTE',
            'observation': 'NULL',
            'lastTopArgument': 0
        }

        if self.daily_payment_condition and len(self.daily_payment_condition) > 1:

            for condition in self.daily_payment_condition:

                # * A posição 3 tem o tipo de serviço que foi executado
                if not condition['serviceType'] in service[3]:
                    # ? Se o tipo de serviço não for igual a condição corrente, irá passar para a próxima condição até que a condição e o tipo de serviços coincidam
                    continue

                if service[8]:
                    if condition['ambulanceChecker'] == 'Sim':
                        serviceValue['description'] += f' - AMBULÂNCIA'
                    else:
                        continue
                else:
                    # TODO Se a condição for para ambulância passar para próxima condição
                    if condition['ambulanceChecker'] == 'Sim':
                        continue

                    kmRange = self.kmRangeFormater(service[5])

                    # ? Validação do range de quilômetros
                    if not (kmRange['initialKm'] >= int(condition['initialKm']) and kmRange['endKm'] <= int(condition['endKm'])):
                        # ? Se o range de quilometragem não for igual a condição corrente, irá passar para a próxima condição até que a condição e o range de quilometros coincidam
                        continue

                    if service[5]:
                        serviceValue['description'] += f' - KM range: ' + service[5]

                # * A posição 7 da lista quer diser que a rota foi feita no período da tarde
                # ? Cálculo de rotas PM
                if service[7]:

                    serviceValue['description'] += f' - PM'
                    serviceValue['value'] = float(
                        condition['pmValue']) if self.is_valid_number(condition['pmValue']) else 0

                    # ? Cálculo do adicional para domingos e feriados
                    if service[6] and service[6] == 'HOLIDAY DAY ROUTE':
                        serviceValue['description'] += f' - DOMINGO/FERIADO'
                        serviceValue['addition'] = (serviceValue['value'] * int(condition['additionalPmValue'])) / \
                            100 if condition['additionalAmValue'] and self.is_valid_number(
                                condition['additionalPmValue']) else 0

                    if service[6] and service[6] == 'SATURDAY DAY ROUTE':
                        serviceValue['description'] += f' - SÁBADO'

                    serviceValue['total'] = serviceValue['value'] + \
                        (serviceValue['value'] *
                            serviceValue['addition'] / 100)

                # ? Cálculo de rotas AM
                else:
                    serviceValue['description'] += f' - AM'
                    serviceValue['value'] = float(
                        condition['amValue']) if self.is_valid_number(condition['amValue']) else 0

                    # ? Cálculo do adicional para domingos e feriados
                    if service[6] and service[6] == 'HOLIDAY DAY ROUTE':
                        serviceValue['description'] += f' - DOMINGO/FERIADO'
                        serviceValue['addition'] = (serviceValue['value'] * int(condition['additionalAmValue'])) / \
                            100 if condition['additionalAmValue'] and self.is_valid_number(
                                condition['additionalAmValue']) else 0

                    if service[6] and service[6] == 'SATURDAY DAY ROUTE':
                        serviceValue['description'] += f' - SÁBADO'

                # TODO Se chegou até aqui o cálculo já foi realizado, não há necessidade de uma nova verificação
                break

            # ? Cálculo de paradas
            if self.pay_per_stop_checker:

                if self.payStopCalculator:
                    stop_payment = self.payStopCalculator(
                        serviceValue)
                    serviceValue['stopPayment'] = round(
                        stop_payment['stopPayment'], 2)
                    serviceValue['additional'] = round(
                        stop_payment['additional'], 2)

            serviceValue['total'] = round(serviceValue['value'] + serviceValue['addition'] +
                                          serviceValue['additional'] + serviceValue['stopPayment'], 2)

            return {
                'invoice': f'"{serviceValue['invoice']}"',
                'period': f'"{serviceValue['period']}"',
                'description': f'"{serviceValue['description']}"',
                'serviceCenter': f'"{serviceValue['serviceCenter']}"',
                'routeNumber': serviceValue['routeNumber'],
                'employeeId': serviceValue['employeeId'],
                'employeeName': f'"{serviceValue['employeeName']}"',
                'date': f'"{serviceValue['date']}"',
                'licensePlate': f'"{serviceValue['licensePlate']}"',
                'transactionType': f'"{serviceValue['transactionType']}"',
                'receipt': serviceValue['receipt'] if serviceValue['receipt'] else 'NULL',
                'stops': serviceValue['stops'] if serviceValue['stops'] else 'NULL',
                'addition': serviceValue['addition'] if serviceValue['addition'] else 'NULL',
                'value': serviceValue['value'] if serviceValue['value'] else 'NULL',
                'stopPayment': serviceValue['stopPayment'] if serviceValue['stopPayment'] else 'NULL',
                'additional': serviceValue['additional'] if serviceValue['additional'] else 'NULL',
                'total': serviceValue['total'] if serviceValue['total'] else 'NULL',
                'status': f'"{serviceValue['status']}"',
                'observation': 'NULL',
            }

        return {
            'invoice': f'"{serviceValue['invoice']}"',
            'period': f'"{serviceValue['period']}"',
            'description': f'"{serviceValue['description']}"',
            'serviceCenter': f'"{serviceValue['serviceCenter']}"',
            'routeNumber': serviceValue['routeNumber'],
            'employeeId': serviceValue['employeeId'],
            'employeeName': f'"{serviceValue['employeeName']}"',
            'date': f'"{serviceValue['date']}"',
            'licensePlate': f'"{serviceValue['licensePlate']}"',
            'transactionType': f'"{serviceValue['transactionType']}"',
            'receipt': serviceValue['receipt'] if serviceValue['receipt'] else 'NULL',
            'stops': serviceValue['stops'] if serviceValue['stops'] else 'NULL',
            'addition': serviceValue['addition'] if serviceValue['addition'] else 'NULL',
            'value': serviceValue['value'] if serviceValue['value'] else 'NULL',
            'stopPayment': serviceValue['stopPayment'] if serviceValue['stopPayment'] else 'NULL',
            'additional': serviceValue['additional'] if serviceValue['additional'] else 'NULL',
            'total': serviceValue['total'] if serviceValue['total'] else 'NULL',
            'status': f'"{serviceValue['status']}"',
            'observation': 'NULL',
        }

    def kmRangeFormater(self, kmRange) -> dict:
        '''
            Esse método retorna o range de km em um dicionário separado em quilômetro inicial e quilômetro final
        '''

        if kmRange:
            kmRangeList = kmRange.split(sep='/')
            kmRangeFormated = {
                'initialKm': int(kmRangeList[0]),
                'endKm': int(kmRangeList[1])
            }
        else:
            kmRangeFormated = {
                'initialKm': 0,
                'endKm': 99999
            }
        return kmRangeFormated

    def simpleCondition(self, condition: dict, service: dict) -> float:
        '''
            Essa função realiza o cálculo de uma condição simples com os argumentos especificados e retorna o valor calculado.
        '''
        operator = condition['operator']
        argument = condition['argument']
        value = condition['value']

        logic = f'{service['stops']} {operator} {argument}'

        if eval(logic):
            stops = service['stops'] - int(service['lastTopArgument'])  # noqa #* O cálculo é a quantidade total de paradas menos o argumento máximo de paradas, resultando no valor excedente para cálculo
            result = stops * float(value)
            service['lastTopArgument'] = argument  # noqa # TODO Passagem por referência
            return round(result, 2)
        return 0

    def compositeCondition(self, condition: dict, service: dict) -> float:
        '''
            Essa função realiza o cálculo de uma condição composta com os argumentos especificados e retorna o valor calculado.
        '''
        operator1 = condition['condition1']['operator']
        argument1 = condition['condition1']['argument']
        operator2 = condition['condition2']['operator']
        argument2 = condition['condition2']['argument']
        value = condition['value']

        # logic = f'{service['stops']} {operator1} {argument1} and {
        #     service['stops']} {operator2} {argument2}'

        # if eval(logic):
        #     stops = service['stops'] - service['lastTopArgument']
        #     result = stops * float(value)

        # * O cálculo é a quantidade total de paradas menos o argumento máximo de paradas, resultando no valor excedente para cálculo
        initial_logic = f'{service['stops']} {operator1} {argument1}'
        if eval(initial_logic):

            end_logic = f'{service['stops']} {operator2} {argument2}'

            if eval(end_logic):

                stops = service['stops'] - int(service['lastTopArgument'])

                result = stops * float(value)

            else:

                stops = float(argument2) - float(argument1) + 1

                result = stops * float(value)

            service['lastTopArgument'] = argument2  # noqa # TODO Passagem por referência
            return round(result, 2)
        return 0

    def limitedCondition(self, condition):
        return 0

    def bonusCondition(self, condition: dict, service: dict) -> float:
        '''
            Essa função realiza o cálculo de uma bonificação com os argumentos especificados e retorna o valor calculado.
            A bonificação retorna o valor especificado quando um determinado parâmetro especificadao é atingido
        '''
        operator = condition['operator']
        argument = condition['argument']
        value = condition['value']
        period = condition['period']

        if not period in service['description']:
            return 0

        logic = f'{service['stops']} {operator} {argument}'

        if eval(logic):
            return float(value)
        return 0

    def payStopCalculatorGenerator(self, conditions_json) -> callable:

        if conditions_json:
            conditions = json.loads(conditions_json)

            # closure

            def calculatorByCondition(service) -> float:

                value = {
                    'stopPayment': 0,
                    'additional': 0
                }

                for condition in conditions:

                    if not condition['serviceType'] in service['description']:
                        # ? Se o tipo de serviço não for igual a condição corrente, irá passar para a próxima condição até que a condição e o tipo de serviços coincidam
                        continue

                    match condition['conditionType']:

                        case 'Condição simples':
                            value['stopPayment'] += self.simpleCondition(
                                condition, service)
                            continue
                        case 'Condição composta':
                            value['stopPayment'] += self.compositeCondition(
                                condition, service)
                            continue
                        case 'Condição limitada':
                            value['stopPayment'] += self.limitedCondition(
                                condition, service)
                            continue
                        case 'Bonificação':
                            value['additional'] += self.bonusCondition(
                                condition, service)
                            continue

                return value
                # Criar as opções aqui dentro

            return calculatorByCondition

    # * DISCOUNT
    def dailyDiscountFormatter(self, reader: object, employee_id: int, service: list, invoice_period: str, route_data: list, services_value_data: dict[list]) -> dict:
        ''' Essa função retorna o desconto do serviço em um dicionário com todos os valores necessários para compor o espelho de pagamento do colaborador
        '''

        serviceValue = {
            'invoice': service[0],
            'period': invoice_period,
            'description': service[3],
            'serviceCenter': service[2],
            'routeNumber': service[1],
            'employeeId': employee_id,
            'employeeName': service[11],
            'date': service[8],
            'licensePlate': service[10],
            'transactionType': 'DESCONTO',
            'receipt': float(service[14]),
            'stops': route_data[16] if route_data else 0,
            'addition': 0,
            'value': 0,
            'stopPayment': 0,
            'additional': 0,
            'total': 0,
            'status': 'PENDENTE',
            'observation': 'NULL',
            'lastTopArgument': 0
        }

        if service[3] == 'Lost packages penalty':
            serviceValue['description'] = 'PACOTE PERDIDO'
            serviceValue['description'] += f' {service[5]
                                               }' if service[5] else ''
            serviceValue['description'] += f' {service[6]
                                               }' if service[6] else ''
            serviceValue['value'] = float(service[14])
            serviceValue['total'] = float(service[14])

            return {
                'invoice': f'"{serviceValue['invoice']}"',
                'period': f'"{serviceValue['period']}"',
                'description': f'"{serviceValue['description']}"',
                'serviceCenter': f'"{serviceValue['serviceCenter']}"',
                'routeNumber': serviceValue['routeNumber'],
                'employeeId': serviceValue['employeeId'],
                'employeeName': f'"{serviceValue['employeeName']}"',
                'date': f'"{serviceValue['date']}"',
                'licensePlate': f'"{serviceValue['licensePlate']}"',
                'transactionType': f'"{serviceValue['transactionType']}"',
                'receipt': serviceValue['receipt'] if serviceValue['receipt'] else 'NULL',
                'stops': serviceValue['stops'] if serviceValue['stops'] else 'NULL',
                'addition': serviceValue['addition'] if serviceValue['addition'] else 'NULL',
                'value': serviceValue['value'] if serviceValue['value'] else 'NULL',
                'stopPayment': serviceValue['stopPayment'] if serviceValue['stopPayment'] else 'NULL',
                'additional': serviceValue['additional'] if serviceValue['additional'] else 'NULL',
                'total': serviceValue['total'] if serviceValue['total'] else 'NULL',
                'status': f'"{serviceValue['status']}"',
                'observation': 'NULL',
            }

        if service[3] == 'Vehicle daily not visited':
            serviceValue['description'] = 'ROTA NÃO CONCLUÍDA'
            for calculedValue in services_value_data['calculedValues']:

                if serviceValue['routeNumber'] == calculedValue['routeNumber']:
                    additionAux = float(
                        calculedValue['addition']) if calculedValue['addition'] != 'NULL' else 0
                    valueAux = float(
                        calculedValue['value']) if calculedValue['value'] != 'NULL' else 0
                    additionalAux = float(
                        calculedValue['additional']) if calculedValue['additional'] != 'NULL' else 0
                    stopPaymentAux = float(
                        calculedValue['stopPayment']) if calculedValue['stopPayment'] != 'NULL' else 0
                    totalAux = float(
                        calculedValue['total']) if calculedValue['total'] != 'NULL' else 0
                    serviceValue['addition'] = neg(additionAux)
                    serviceValue['value'] = neg(valueAux)
                    serviceValue['additional'] = neg(additionalAux)
                    serviceValue['stopPayment'] = neg(stopPaymentAux)
                    serviceValue['total'] = neg(totalAux)

                    return {
                        'invoice': f'"{serviceValue['invoice']}"',
                        'period': f'"{serviceValue['period']}"',
                        'description': f'"{serviceValue['description']}"',
                        'serviceCenter': f'"{serviceValue['serviceCenter']}"',
                        'routeNumber': serviceValue['routeNumber'],
                        'employeeId': serviceValue['employeeId'],
                        'employeeName': f'"{serviceValue['employeeName']}"',
                        'date': f'"{serviceValue['date']}"',
                        'licensePlate': f'"{serviceValue['licensePlate']}"',
                        'transactionType': f'"{serviceValue['transactionType']}"',
                        'receipt': serviceValue['receipt'] if serviceValue['receipt'] else 'NULL',
                        'stops': serviceValue['stops'] if serviceValue['stops'] else 'NULL',
                        'addition': serviceValue['addition'] if serviceValue['addition'] else 'NULL',
                        'value': serviceValue['value'] if serviceValue['value'] else 'NULL',
                        'stopPayment': serviceValue['stopPayment'] if serviceValue['stopPayment'] else 'NULL',
                        'additional': serviceValue['additional'] if serviceValue['additional'] else 'NULL',
                        'total': serviceValue['total'] if serviceValue['total'] else 'NULL',
                        'status': f'"{serviceValue['status']}"',
                        'observation': 'NULL',
                    }

            # * Quando não for localizada a rota nos calculos feitos nessa requisição de cálculo, o sistema irá buscar em cálculos feitos antes, no código abaixo
            calculedValue = self.getOlderCalculedValue(reader,
                                                       serviceValue['routeNumber'])
            if calculedValue and len(calculedValue) > 1:
                serviceValue['addition'] = neg(calculedValue['addition'])
                serviceValue['value'] = neg(calculedValue['value'])
                serviceValue['stopPayment'] = neg(
                    calculedValue['stopPayment'])
                serviceValue['total'] = neg(calculedValue['total'])

            #! Se não for encontrado nenhum espelho dessa rota, o desconto será 0 e deverá ser modificado ou analisado na página de Espelhos de pagamento
            return {
                'invoice': f'"{serviceValue['invoice']}"',
                'period': f'"{serviceValue['period']}"',
                'description': f'"{serviceValue['description']}"',
                'serviceCenter': f'"{serviceValue['serviceCenter']}"',
                'routeNumber': serviceValue['routeNumber'],
                'employeeId': serviceValue['employeeId'],
                'employeeName': f'"{serviceValue['employeeName']}"',
                'date': f'"{serviceValue['date']}"',
                'licensePlate': f'"{serviceValue['licensePlate']}"',
                'transactionType': f'"{serviceValue['transactionType']}"',
                'receipt': serviceValue['receipt'] if serviceValue['receipt'] else 'NULL',
                'stops': serviceValue['stops'] if serviceValue['stops'] else 'NULL',
                'addition': serviceValue['addition'] if serviceValue['addition'] else 'NULL',
                'value': serviceValue['value'] if serviceValue['value'] else 'NULL',
                'stopPayment': serviceValue['stopPayment'] if serviceValue['stopPayment'] else 'NULL',
                'additional': serviceValue['additional'] if serviceValue['additional'] else 'NULL',
                'total': serviceValue['total'] if serviceValue['total'] else 'NULL',
                'status': f'"{serviceValue['status']}"',
                'observation': 'NULL',
            }

        if service[3] == 'Pnr packages penalty':
            serviceValue['description'] = 'PNR'
            serviceValue['description'] += f' {service[5]
                                               }' if service[5] else ''
            serviceValue['description'] += f' {service[6]
                                               }' if service[6] else ''
            serviceValue['value'] = float(service[14])
            serviceValue['total'] = float(service[14])

            return {
                'invoice': f'"{serviceValue['invoice']}"',
                'period': f'"{serviceValue['period']}"',
                'description': f'"{serviceValue['description']}"',
                'serviceCenter': f'"{serviceValue['serviceCenter']}"',
                'routeNumber': serviceValue['routeNumber'],
                'employeeId': serviceValue['employeeId'],
                'employeeName': f'"{serviceValue['employeeName']}"',
                'date': f'"{serviceValue['date']}"',
                'licensePlate': f'"{serviceValue['licensePlate']}"',
                'transactionType': f'"{serviceValue['transactionType']}"',
                'receipt': serviceValue['receipt'] if serviceValue['receipt'] else 'NULL',
                'stops': serviceValue['stops'] if serviceValue['stops'] else 'NULL',
                'addition': serviceValue['addition'] if serviceValue['addition'] else 'NULL',
                'value': serviceValue['value'] if serviceValue['value'] else 'NULL',
                'stopPayment': serviceValue['stopPayment'] if serviceValue['stopPayment'] else 'NULL',
                'additional': serviceValue['additional'] if serviceValue['additional'] else 'NULL',
                'total': serviceValue['total'] if serviceValue['total'] else 'NULL',
                'status': f'"{serviceValue['status']}"',
                'observation': 'NULL',
            }

        return {
            'invoice': f'"{serviceValue['invoice']}"',
            'period': f'"{serviceValue['period']}"',
            'description': f'"{serviceValue['description']}"',
            'serviceCenter': f'"{serviceValue['serviceCenter']}"',
            'routeNumber': serviceValue['routeNumber'],
            'employeeId': serviceValue['employeeId'],
            'employeeName': f'"{serviceValue['employeeName']}"',
            'date': f'"{serviceValue['date']}"',
            'licensePlate': f'"{serviceValue['licensePlate']}"',
            'transactionType': f'"{serviceValue['transactionType']}"',
            'receipt': serviceValue['receipt'] if serviceValue['receipt'] else 'NULL',
            'stops': serviceValue['stops'] if serviceValue['stops'] else 'NULL',
            'addition': serviceValue['addition'] if serviceValue['addition'] else 'NULL',
            'value': serviceValue['value'] if serviceValue['value'] else 'NULL',
            'stopPayment': serviceValue['stopPayment'] if serviceValue['stopPayment'] else 'NULL',
            'additional': serviceValue['additional'] if serviceValue['additional'] else 'NULL',
            'total': serviceValue['total'] if serviceValue['total'] else 'NULL',
            'status': f'"{serviceValue['status']}"',
            'observation': 'NULL',
        }

    def getOlderCalculedValue(self, reader: object, route_number: int) -> dict:
        calculed_values = reader.getCalculedValueFromDatabase(
            route_number, '"PAGAMENTO"')

        return {
            'invoice': calculed_values[0],
            'period': calculed_values[1],
            'description': calculed_values[2],
            'serviceCenter': calculed_values[3],
            'routeNumber': calculed_values[4],
            'employeeId': calculed_values[5],
            'employeeName': calculed_values[6],
            'date': calculed_values[7],
            'licensePlate': calculed_values[8],
            'transactionType': calculed_values[9],
            'receipt': calculed_values[10],
            'stops': calculed_values[11],
            'addition': calculed_values[12],
            'value': calculed_values[13],
            'stopPayment': calculed_values[14],
            'additional': calculed_values[15],
            'total': calculed_values[16],
            'status': calculed_values[17],
            'observation': calculed_values[18],
        }
