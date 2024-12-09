from payment_voucher_creator.core.database.database import Database


class Reader(Database):
    def __init__(self) -> None:
        super().__init__()

    def getInvoiceIdByPeriod(self, period: str) -> list:
        self.connection.start_transaction()
        if period == 'last':
            # ? This command get the last register on database
            command = f'''
                    SELECT * FROM move_smart.invoice_information
                    ORDER BY id DESC
                    LIMIT 1;
                    '''
        else:
            command = f'''
                        SELECT * FROM move_smart.invoice_information
                        WHERE period = '{period}';
                        '''
        self.cursor.execute(command)
        result = self.cursor.fetchone()  # Read the database
        self.connection.commit()
        if result:
            return result[0]
        return None

    def getPaymentMirrors(self, period: str) -> list[list] | list:
        '''
            Essa função verifica que existe pagamentos já calculados referente ao período solicitado, se existir ele retorna os pagamentos do período e os pagamentos pendentes de outros períodos.
            Se não houver pagamentos do período solicitado a função irá retornar uma mensagem dizendo que não há pagamentos calculados para o período requisitado.
        '''
        invoice_id = self.getInvoiceIdByPeriod(period=period)

        self.connection.start_transaction()
        command = f'''
                SELECT * FROM move_smart.payment_mirrors
                WHERE period = '{period}';
                '''
        self.cursor.execute(command)
        result = self.cursor.fetchall()  # Read the database

        if len(result) >= 1 and invoice_id:

            # ? This command get the last register on database
            command = f'''
                    SELECT date, id_route, description, license_plate, transaction_type, value, additional, total, status
                    FROM move_smart.payment_mirrors
                    WHERE period = '{period}' AND employee_id = 10000055
                    ORDER BY (STR_TO_DATE(date, '%d/%m/%Y')) ASC, (id_route) ASC;
                    '''
            self.cursor.execute(command)
            result = self.cursor.fetchall()  # Read the database
            self.connection.commit()
            return result
        else:
            return None
