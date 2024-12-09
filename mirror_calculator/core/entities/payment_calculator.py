from mirror_calculator.core.database.reader import Reader
from mirror_calculator.core.entities.service_center import ServiceCenter


class PaymentCalculator():

    def __init__(self, invoice_period) -> None:
        self.reader = Reader()
        self.invoice_period = invoice_period
        self.invoice_id = self.getInvoiceIdByPeriod(invoice_period)
        self.service_center_data = self.getAllServiceCenterData()
        self.service_centers = self.serviceCenterEntitiesCreator(
            self.service_center_data)

    def getPaymentMirror(self) -> list[dict]:
        ''' Esse método retorna uma lista de dicionários que contém os dados de pagamentos calculados mediante os parâmetros dos service centers registrados no banco de dados
        '''
        dailyPaymentData = self.reader.getAllDailyPaymentsData(self.invoice_id)
        # additionalPaymentData = self.reader.getAllAdditionalPaymentsData(
        #     self.invoice_id)

        paymentDiscountData = self.reader.getAllPaymentsDiscountsData(
            self.invoice_id)

        allPaymentsData = dailyPaymentData + paymentDiscountData
        # + additionalPaymentData
        servicesValueData = {
            'calculedValues': [],
            'servicesWithoutParameters': [],
            'serviceWithTrouble': []
        }

        for paymentData in allPaymentsData:

            # ! Parte exclusiva para testar rotas com problemas
            # if paymentData[1] == 134916545 or paymentData[1] == 134916972 or paymentData[1] == 135658727:
            #     print("stop")

            # * Percorre cada pagamento
            for service_center in self.service_centers:
                # * Percorre cada instância do service center
                if paymentData[2] in service_center.id:
                    # * Valida se a base do pagamento é a mesma da instância, se sim ele faz o cálculo do pagamento mediante os parâmetros da instância do service center

                    route_data = self.reader.getRouteDataById(paymentData[1])
                    employee_name = self.getEmployeeName(paymentData)
                    employee_id = self.reader.getEmployeeIdByName(
                        employee_name)
                    serviceValue = service_center.getServiceValue(self.reader, employee_id,
                                                                  paymentData, self.invoice_period, route_data, servicesValueData)

                    if serviceValue and serviceValue != 'PRODUCAO' and serviceValue['value'] != 0:
                        servicesValueData['calculedValues'].append(
                            serviceValue)
                        break
                    elif serviceValue != 'PRODUCAO':
                        servicesValueData['serviceWithTrouble'].append(
                            serviceValue)
                        break
                    elif serviceValue != 'PRODUCAO' and ['value'] == 0:
                        servicesValueData['servicesWithoutParameters'].append(
                            serviceValue)
                        break
        if servicesValueData['servicesWithoutParameters']:
            print('ATTENTION: ROUTES WITHOUT PARAMETERS FOR CALCULATION OF PAYMENTS')
            print(servicesValueData['servicesWithoutParameters'])
        if servicesValueData['serviceWithTrouble']:
            print('ATTENTION: ROUTES WITH TROUBLE FOR CALCULATION OF PAYMENTS')
            print(servicesValueData['serviceWithTrouble'])
        return servicesValueData

    def serviceCenterEntitiesCreator(self, service_centers_data):
        if service_centers_data:

            service_centers_list = []
            for service_center_data in service_centers_data:

                service_center = ServiceCenter(
                    service_center_data['service_center'],
                    service_center_data['daily_payment_condition'],
                    service_center_data['pay_per_stop_checker'],
                    service_center_data['pay_per_stop_condition'])

                service_centers_list.append(service_center)

            return service_centers_list
        return None

    def getInvoiceIdByPeriod(self, period) -> None | int:
        result = self.reader.getInvoiceIdByPeriod(period)

        if result and len(result) > 1:
            id = result[0]
            return id

        return None

    def getAllServiceCenterData(self):
        service_center_data = self.reader.getAllServiceCenterData()

        service_center_data = [
            {
                'service_center': hub[0],
                'daily_payment_condition': hub[1],
                'pay_per_stop_checker': hub[2],
                'pay_per_stop_condition': hub[3]
            }
            for hub in service_center_data
        ]
        return service_center_data

    def getEmployeeName(self, paymentData: list) -> str:
        if paymentData[4] == 'PAYMENT':
            return paymentData[12]
        if paymentData[4] == 'DISCOUNT':
            return paymentData[11]
