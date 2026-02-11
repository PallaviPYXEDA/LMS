import os
import json
import boto3
import datetime
import traceback
from typing import Any


try:
    # grab environment variables
    FN_NAME_PREFIX = os.environ['FN_NAME_PREFIX']
except:
    FN_NAME_PREFIX = ''


def convert_timestamp(item_date_object):
    if isinstance(item_date_object, (datetime.date, datetime.datetime)):
        return item_date_object.timestamp()


def get_user_id_from_event(event):
    user_id = ''
    # For regular lambdas user will be in event['navUser']
    try:
        # NOTE: Use this to provide user_id during development
        user_id = event['navUser']
    except:
        pass
    # In cases of Lambda calling another lambda
    if not user_id:
        try:
            # NOTE: Use this to provide user_id during development
            user_id = event['body']['user']
        except:
            pass
    return user_id

def success_method(result):
    """Handle successful completion

    Arguments:
        body {String} -- String to return back from the call

    Returns:
        Dictionary -- Response to return back for the generated error
    """
    if result is None:
        result = 'Success'
    
    if not isinstance(result, str):
        # If object is not serializable, make it serializable
        result = json.dumps(result, default=convert_timestamp)
    print('Final Response: {}'.format(result))
    return {
        'statusCode': 200,
        'body': result,
        'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                   }
    }


def get_context_info(context):
    ctx_info = {}
    base_log_link = 'https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logEventViewer:group='
    try:
        ctx_info['streamName'] = context.log_stream_name
        ctx_info['logGroupName'] = context.log_group_name
        ctx_info['requestId'] = context.aws_request_id
        ctx_info['logLink'] = base_log_link + ctx_info['logGroupName'] + ';stream=' + ctx_info['streamName'] +';'
    except:
        pass
    return ctx_info


def report_error(user, request_id, error, link):
    "Not implemented yet"


def unsupported_method(event, context, error, format_output=True):
    """Handle unsupported errors

    Arguments:
        e {Exception} -- Exception that was raised

    Returns:
        Dictionary -- Response to return back for the generated error
    """
    ctx_info = get_context_info(context)
    user = get_user_id_from_event(event)

    # Print the stack trace of the error
    traceback.print_exc()

    #print('Final Response: {}'.format(json.dumps(str(e))))
    if 'requestId' in ctx_info and 'logLink' in ctx_info:
        print(ctx_info['requestId'], ctx_info['logLink'])
        report_error(user, ctx_info['requestId'], str(error), ctx_info['logLink'])
    if format_output:
        body = json.dumps(str(error))
    else:
        body = json.dumps(error)
    return {
        'statusCode': 400,
        'body': body,
        'headers': {'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                    }
    }


def failure_response(errors: list) -> dict:
    response = {
        "status": "failure",
        "data": None,
        "errors": errors
    }

    return response


def success_response(data: Any = None) -> dict:
    response = {
        'status': 'success',
        'data': data,
        'errors': []
    }

    return response
