import datetime
import json
import logging
import os
from typing import Any, Dict, List, Union, Tuple
import uuid

from RDS import rds_config, rds_data_api, tables
from Utils import request_utils as req_utils

try:
    # grab environment variables
    DB_NAME_SUFFIX = os.environ["DB_NAME_SUFFIX"]
except:
    DB_NAME_SUFFIX = ""


# rds settings
if "PRODUCTION" in DB_NAME_SUFFIX:
    DB_NAME = rds_config.prod_db_name
    CLUSTER_ARN = rds_config.prod_db_cluster_arn
    SECRETS_MANAGER_ARN = rds_config.prod_db_secret_arn
else:
    DB_NAME = rds_config.others_db_name
    CLUSTER_ARN = rds_config.others_db_cluster_arn
    SECRETS_MANAGER_ARN = rds_config.others_db_secret_arn

if DB_NAME_SUFFIX:
    DB_NAME = DB_NAME + DB_NAME_SUFFIX
    print("Using DB: {}".format(DB_NAME))

logger = logging.getLogger()
logger.setLevel(logging.INFO)

USE_RDS_DATA_API = True


def initialize_connection(use_data_api=True):
    # Change the global variable
    global USE_RDS_DATA_API

    USE_RDS_DATA_API = use_data_api

    if USE_RDS_DATA_API:
        try:
            db_conn = rds_data_api.Connection(DB_NAME, CLUSTER_ARN, SECRETS_MANAGER_ARN)
            # Test if data api is enable and a connection can be established for new db instances or else fall back to pymysql
            statement = "SELECT version()"
            db_conn.cursor().execute(statement)
            return db_conn
        except Exception as e:
            USE_RDS_DATA_API = False
            print("Unable to use data api. Error:", str(e))


conn = initialize_connection()


def to_camel_case(snake_str):
    try:
        components = snake_str.split("_")
        # We capitalize the first letter of each component except the first one
        # with the 'title' method and join them together.
        return components[0] + "".join(x.title() for x in components[1:])
    except Exception as e:
        print("Error: ", str(e))
        return snake_str


def convert_timestamp(item_date_object):
    if isinstance(item_date_object, (datetime.date, datetime.datetime)):
        return item_date_object.timestamp()


def get_connection(new_db=False):
    if not new_db:
        return conn
    # This is a new db creation
    global USE_RDS_DATA_API

    if USE_RDS_DATA_API:
        try:
            # Test if data api is enable and a connection can be established for new db instances
            statement = "SELECT version()"
            conn.cursor().execute(statement)
            return conn
        except Exception as e:
            print(
                "Could not establish a RDS Data API connection, Check if data api is enabled. Error:",
                str(e),
            )
            # Turn off using rds data api for this lambda
            USE_RDS_DATA_API = False


def execute_statement(
    statement: str, db_conn=None, sql_params: Union[rds_data_api.SqlParams, None] = None
):
    """Execute the statement in the database

    Arguments:
        statement {string} -- DB Statement to execute

    Returns:
        Object -- Respose from execution of the statement
    """
    if USE_RDS_DATA_API or not db_conn:
        # Use the global db connection
        myconn = conn
    else:
        # Use the provided db connection if it exists
        myconn = db_conn["connection"]

    print('logging statement inside execute_statement(): ', statement)
    args = [statement, sql_params] if sql_params else [statement]

    # Execute the statement using the determinted connection
    try:
        cur = myconn.cursor()
        cur.execute(*args)
        response = cur.fetchall()
    except Exception as e:
        print("Unable to execute the statement! Error: " + str(e))
        return None

    print(response)
    return response


def fetch_col_names(table_name):
    col_names = []
    actual_table_name = tables.get_actual_table_name(table_name)
    stmt = "desc " + actual_table_name
    table_desc = execute_statement(stmt)
    for col_desc in table_desc:
        col_names.append(col_desc[0])
    print(table_name, "col names: ", col_names)
    return col_names

def extract_id(event, param_name, multi_value=False) -> str:
    """Extract the service id from the event

    Arguments:
        event {Dict} -- Dictionary containing event information

    Returns:
        String -- AI Service identifier
    """
    id = ""
    try:
        if multi_value:
            id = event["multiValueQueryStringParameters"][param_name]
        else:
            id = event["queryStringParameters"][param_name]
    except Exception as e:
        print("Warning: Unable to extract id " + str(e))
    return id


def prepare_get_response(table_name, select_response, col_names=None, camel_case=False):
    try:
        if not col_names:
            col_names = fetch_col_names(table_name)
        if camel_case:
            for index, col in enumerate(col_names):
                col_names[index] = to_camel_case(col)
        response = {}
        for lines in select_response:
            row = {}
            for index in range(len(col_names)):
                if isinstance(lines[index], (datetime.datetime, datetime.date)):
                    row[col_names[index]] = lines[index].isoformat()
                else:
                    row[col_names[index]] = lines[index]
                if index == 0:
                    key = lines[index]
                response[key] = row
        return response
    except Exception as e:
        print("Unable to prepare response!")
        print(table_name, select_response, str(e))
        return {}


def create_parameterized_update_statement(event, table_column, table_name):
    user_id = req_utils.get_user_id_from_event(event)
    try:
        id_value = event["queryStringParameters"][table_column]
    except Exception as e:
        print(f"Exception: unable to fetch the parameters: {table_column}")
        return None

    actual_table_name = tables.get_actual_table_name(table_name)
    if not actual_table_name:
        print("Table not found!")
        return None

    try:
        params = event["body"]
    except KeyError:
        print("Bad request: Parameter body is missing.")
        return None

    if not params:
        print("Bad request: No values to update!")
        return None

    col_names = fetch_col_names(table_name)
    statement = "UPDATE " + actual_table_name + " SET "

    sql_params = []
    for key, value in params.items():
        if value is None or key == "user":
            continue
        if isinstance(value, list):
            value = convert_list_to_string(value)
        elif isinstance(value, int) or isinstance(value, float):
            value = str(value)

        # NOTE: consider skipping or creating a versioned key for duplicates
        statement += f"{key} = :{key} ,"
        sql_params.append(create_param(key, value))

    # Strip the last comma
    statement = statement[:-2]

    id_name = col_names[0]
    statement += f" WHERE {id_name} = :{id_name}"
    sql_params.append(create_param(id_name, id_value))

    if table_name == "additionalAccounts":
        statement += f" AND owner_id=:auth_owner_id"
        sql_params.append(create_param("auth_owner_id", user_id))
    if table_name not in tables.tables_without_user and (
        "path" in event and event["path"] != "/aiclub/user-profiles"
    ):
        statement += f" AND user_id = :auth_user_id"
        sql_params.append(create_param("auth_user_id", user_id))

    print(f"Statement: {statement}")
    return statement, sql_params


def create_update_query_from_event_params(event, table_column, table_name):
    # print('Event: {}'.format(event))
    user_id = req_utils.get_user_id_from_event(event)
    try:
        id_value = event["queryStringParameters"][table_column]
    except Exception as e:
        print("Exception: unable to fetch the parameters: {}".format(table_column))
        return None
    try:
        col_names = fetch_col_names(table_name)
        try:
            # Safeguard to not replace the user_id
            del event["body"]["user"]
        except:
            pass
        params = event["body"]
        statement = "UPDATE " + tables.get_actual_table_name(table_name) + " SET "
        for key, value in params.items():
            if value is None:
                continue
            if isinstance(value, list):
                value = convert_list_to_string(value)

            if isinstance(value, (float, int)):
                value = str(value)
                statement = statement + key + " =  " + value + " , "
            else:
                statement = statement + key + ' =  "' + value + '" , '
        print(statement)
        # Strip the last comma
        statement = statement[:-2:]
        statement = statement + " WHERE " + col_names[0] + ' = "' + id_value + '"'
        if table_name == "additionalAccounts":
            statement = statement + ' and owner_id="' + user_id + '"'
        if table_name not in tables.tables_without_user and (
            "path" in event and event["path"] != "/aiclub/user-profiles"
        ):
            statement = statement + ' and user_id="' + user_id + '"'
            print("Statement: {}".format(statement))
    except Exception as e:
        print("Exception: {}".format(str(e)))
        return None
    return statement


def create_parameterized_insert_statement(
    data: Dict[str, Any], table_name: str
) -> Tuple[str, List[Dict[str, str]]]:
    columns = ""
    values = ""
    sql_params = []

    for key, value in data.items():
        columns += f"{key}, "
        values += f":{key}, "
        sql_params.append(create_param(key, str(value)))

    statement = f"INSERT INTO {table_name} ({columns[:-2]}) VALUES({values[:-2]})"

    print(f"Statement: {statement}", sql_params)
    return statement, sql_params


def create_parameterized_get_statements(
    data: Dict[str, Any], table_name: str
) -> Tuple[str, List[Dict[str, str]]]:
    statement = "select * from " + table_name

    limit = 100

    queries = []
    sql_params = []
    for key, value in data.items():
        if value:
            if key == "limit":
                limit = value
                continue
            elif key == "start_timestamp":
                queries.append(f" timestamp > :{value}")
            elif key == "end_timestamp":
                queries.append(f" timestamp <= :{value}")
            else:
                queries.append(f" {key} = :{key}")
            sql_params.append(create_param(key, str(value)))

    for index, query in enumerate(queries):
        if index == 0:
            statement += " where" + query
        else:
            statement += " and" + query

    statement += f" order by timestamp desc limit {limit}"

    print(f"Statement: {statement}", sql_params)
    return statement, sql_params


def create_param(param_name: str, param_value: str) -> Dict[str, Any]:
    if param_value is None:
        return {"name": param_name, "value": {"isNull": True}}
    elif isinstance(param_value, int):
        return {"name": param_name, "value": {"longValue": param_value}}
    return {"name": param_name, "value": {"stringValue": param_value}}
