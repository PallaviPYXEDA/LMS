
import uuid
import json

from Utils import response_utils as rutils
from RDS import db_utils as dbutils
from Utils import request_utils as req_utils


TABLE_NAME = 'course'

def process_get_request(event):
    """GET REST API Handler

    Arguments:
        event {Dict} -- Dictionary object containing the input arguements

    Returns:
        Dict  -- Dictionary object containing the response from the DB
    """
    course_id = dbutils.extract_id(event, 'courseId')
    statement = "select * from " + TABLE_NAME
    queries = []

    if course_id:
        queries.append("course_id = '{}'".format(course_id))
    
    for index, query in enumerate(queries):
        if index == 0:
            statement += " where" + query
        else:
            statement += " and" + query
    
    print(statement)

    stmt_response = dbutils.execute_statement(statement)
    response = dbutils.prepare_get_response('course', stmt_response, camel_case=True)
    
    return response


def process_post_request(event: dict) -> dict:
    """Process POST request

    Arguments:
        event {Dict} -- Dictionary containing the input to the REST requests

    Returns:
        Dict -- Response to the REST API request
    """
    print("event: ", event)

    if isinstance(event['body'], str):
        params = json.loads(event['body'])
    else:
        params = event['body']

    course_id = str(uuid.uuid4())
    name = req_utils.get_params(params, "name")

    data = {
        "course_id": course_id,
        "name": name
    }

    try:
        statement, sql_params = dbutils.create_parameterized_insert_statement(
            data, TABLE_NAME
        )
        dbutils.conn.cursor().execute(statement, sql_params)

    except Exception as e:
        response = "Unable to execute statement:{} err: ".format(statement) + str(e)
        print(response)
        error = {
            "errorCode": None,
            "message": response,
            "suggestions": None,
        }
        return rutils.failure_response([error])

    response = dict({"courseId": course_id})
    return rutils.success_response(response)



def lambda_handler(event : dict, context: dict) -> dict:
    """Handle the request from the API gateway

    Arguments:
        event {Dict} -- Dictionary containing the input to the REST requests
        context {Dict} -- Context object associated with the call

    Returns:
        Dict -- Response to the REST API request
    """
    try:
        if (event['httpMethod'] == "GET"):
            response = process_get_request(event)
        elif (event['httpMethod'] == "POST"):
            response = process_post_request(event)
        else:
            print('Unsupported Method: {}'.format(event['httpMethod']))
    except Exception as e:
        return rutils.unsupported_method(event, context, e)

    return rutils.success_method(response)