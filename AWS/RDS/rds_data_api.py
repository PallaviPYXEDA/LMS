from typing import List, TypedDict, Union
import boto3

class _SqlParamValue(TypedDict, total=False):
    isNull: bool
    booleanValue: bool
    longValue: int
    doubleValue: float
    stringValue: str
    blobValue: bytes

class _SqlParam(TypedDict):
    name: str
    value: _SqlParamValue

SqlParams = List[_SqlParam]

class Connection:
    def __init__(self, db_name, db_cluster_arn, db_secret_arn):
        self.db_cluster_arn = db_cluster_arn
        self.db_name = db_name
        self.db_secret_arn = db_secret_arn
        self.rds_client = boto3.client('rds-data')
        self.cursor_class = Cursor
        self.current_transaction_id = None

    def cursor(self):
        return self.cursor_class(self)


class Cursor:
    def __init__(self, connection):
        self.connection = connection
        self.db_cluster_arn = connection.db_cluster_arn
        self.db_secret_arn = connection.db_secret_arn
        self.db_name = connection.db_name
        self.rownumber = 0
        self.rowcount = -1
        self._rows = None

    def _get_db(self):
        if not self.connection:
            raise Exception("Boto client not defined")
        return self.connection

    def _get_row_data(self, response):
        rows = []
        if 'records' in response:
            for record in response['records']:
                # Remove type information from the response
                # col = {data_type: value}
                data = []
                for col in record:
                    for col_type, col_val in col.items():
                        if 'isNull' in col_type:
                            col_val = None
                        data.append(col_val)
                rows.append(data)
        # print('rows', rows)
        return tuple(rows)

    def _set_result(self, response) -> int:
        rows_affected = None

        if 'numberOfRecordsUpdated' in response and response['numberOfRecordsUpdated'] > 0:
            self._rows = None
            self.rowcount = 0
            rows_affected = response['numberOfRecordsUpdated']
        else:
            self._rows = self._get_row_data(response)
            self.rowcount = len(self._rows) if self._rows else 0
            rows_affected = self.rowcount
        return rows_affected

    def _clear_result(self):
        self.rownumber = 0

        self.rowcount = 0
        self._rows = None

    def execute(self, statement: str, sql_params: Union[SqlParams, None] = None) -> int:
        conn = self._get_db()
        self._clear_result()
        transaction_id = conn.current_transaction_id
        kwargs = {
            'resourceArn': self.db_cluster_arn,
            'secretArn': self.db_secret_arn,
            'database': self.db_name,
            'sql': statement
        }
        if transaction_id:
            kwargs['transactionId'] = transaction_id
        if sql_params:
            kwargs["parameters"] = sql_params
        try:
            response = conn.rds_client.execute_statement(**kwargs)
        except Exception as e:
            print("Unable to execute statement: {} Error: {}".format(
                statement, str(e)))
            # if we can't execute a statement we can create a mysql connection here just for this statement and close it
            raise
        # print(response)

        rows_affected = self._set_result(response)

        return rows_affected

    def fetchone(self):
        if self._rows is None or self.rownumber >= len(self._rows):
            return None
        result = self._rows[self.rownumber]
        self.rownumber += 1
        return result

    def fetchall(self):
        if self._rows is None:
            return ()
        if self.rownumber:
            result = self._rows[self.rownumber:]
        else:
            result = self._rows
        self.rownumber = len(self._rows)
        return result
