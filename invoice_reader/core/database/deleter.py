from invoice_reader.core.database.database import Database
# from database import Database


class Deleter(Database):
    def __init__(self) -> None:
        super().__init__()

    def deleteAllInvoiceData(self, invoice: int) -> None | list:
        self.connection.start_transaction()
        command = ''
        command = f'''
                    DELETE FROM move_smart.invoice_discount_without_route
                    WHERE invoice = {invoice};
                    DELETE FROM move_smart.invoice_discount
                    WHERE invoice = {invoice};
                    DELETE FROM move_smart.invoice_additional_payment
                    WHERE invoice = {invoice};
                    DELETE FROM move_smart.invoice_payment
                    WHERE invoice = {invoice};
                    DELETE FROM move_smart.invoice_information
                    WHERE id = {invoice};
                '''
        self.cursor.execute(command)
        self.connection.commit()
