from RDS import db_utils as dbutils
from RDS import tables


def lambda_handler(event, context):
    """
    This function initalizes the tables for LMS
    """
    try:
        # Try creating a database if it does not exist
        db_conn = dbutils.get_connection(new_db=True)
        if not db_conn:
            raise 'Unable to create a new connection error!!'

        database_name = dbutils.DB_NAME
        if "lms" not in database_name:
            print("Database name does not contain 'lms': {}".format(database_name))
            return
        statement = 'CREATE DATABASE IF NOT EXISTS ' + database_name
    except:
        pass
    try:
        table_name = event['tableName']
    except:
        table_name = ''
        pass

    item_count = 0
    for name in tables.TABLES:
        if table_name and table_name != name:
            continue
        statement = tables.TABLES[name]
        print(statement)
        try:
            dbutils.execute_statement(statement)
            item_count += 1
        except:
            print('Unable to execute: {}'.format(statement))

    # If we need to modify a table, we can do it here,
    # for example, if we need to modify the name column in the courses table
    # After modifying tables please do the change you did in the tables.py file
    # So we have our database schema in sync
    base_statement = "ALTER TABLE courses"
    columns = " MODIFY COLUMN name varchar(72) NOT NULL"
    statement = base_statement +    columns
    dbutils.execute_statement(statement)