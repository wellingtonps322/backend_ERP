from invoice_reader.core.database.database import Database


class Updater(Database):

    def __init__(self) -> None:
        super().__init__()

    def setUpdateDriverNumericData(self, field_to_insert: str, data_to_inserted: int, ID: str):
        # try:
        self.connection.start_transaction()
        command = f'''
                        UPDATE move_smart.employee
                        SET {field_to_insert} = {data_to_inserted}
                        WHERE ID = {ID};
                    '''
        self.cursor.execute(command)
        self.connection.commit()

        # except Exception as e:
        #     print('Error:', e.__class__.__name__)
        #     print(e)
        #     self.connection.rollback()

    # def setUpdateDriverStrData(self, field_to_insert: str, data_to_inserted: str, driver_name: str, service_center: str):
    #     # try:
    #     self.connection.start_transaction()
    #     command = f'''
    #                     UPDATE move_smart_system_db.drivers
    #                     SET {field_to_insert} = "{data_to_inserted}"
    #                     WHERE driver_name = "{driver_name}" AND service_center = "{service_center}";
    #                 '''
    #     self.cursor.execute(command)
    #     self.connection.commit()

    #     # except Exception as e:
    #     #     print('Error:', e.__class__.__name__)
    #     #     print(e)
    #     #     self.connection.rollback()

    def setUpdateDriverStrData(self, field_to_insert: str, data_to_inserted: str, ID: int):
        # try:
        self.connection.start_transaction()
        command = f'''
                        UPDATE move_smart.employee
                        SET {field_to_insert} = {data_to_inserted}
                        WHERE ID = {ID};
                    '''
        self.cursor.execute(command)
        self.connection.commit()

        # except Exception as e:
        #     print('Error:', e.__class__.__name__)
        #     print(e)
        #     self.connection.rollback()

    def setUpdateVehicleStrData(self, field_to_insert: str = 'NULL', data_to_insert: str = 'NULL', field_to_check: str = 'NULL',
                                data_to_check: str = 'NULL'):
        # try:
        self.connection.start_transaction()
        command = f'''
                    UPDATE move_smart.vehicle
                    SET {field_to_insert} = {data_to_insert}
                    WHERE {field_to_check} = {data_to_check}
                    '''
        self.cursor.execute(command)
        self.connection.commit()
        # except Exception as e:
        #     print('Error:', e.__class__.__name__)
        #     print(e)
        #     self.connection.rollback()
