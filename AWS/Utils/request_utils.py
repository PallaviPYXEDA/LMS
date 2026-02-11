"""Helper functions to process incoming requests via api gateway"""
import datetime
import os
from typing import Any, Dict, Mapping, TypeVar, Union

K = TypeVar("K")
V = TypeVar("V")

try:
    # grab environment variables
    FN_NAME_PREFIX = os.environ['FN_NAME_PREFIX']
except:
    FN_NAME_PREFIX = ''


_Event = Dict[str, Any]

def get_params(param: Mapping[K, V], paramName: K, escape_chars: bool=False) -> Union[V, str]:
    try:
        retval = param[paramName]
        if escape_chars:
            retval = esacape_special_charracters(retval)
    except:
        retval = ''

    return retval


def convert_timestamp(item_date_object):
    if isinstance(item_date_object, (datetime.date, datetime.datetime)):
        return item_date_object.timestamp()


def get_cognito_user_id_from_event(event: _Event) -> str:
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
    if not user_id:
        try:
            # This is done in the context of step functions
            user_id = event['Input']['body']['user']
        except:
            pass
    if not user_id:
        # User Id will be in event by default.
        try:
            user_id = event['requestContext']['authorizer']['claims']['cognito:username']
            email = event['requestContext']['authorizer']['claims']['email']
            if user_id:
                return user_id
        except:
            pass
        # In cases where a Lambda is called using another lambda it will be in context
        try:
            user_id = event['requestContext']['authorizer']['claims']['email']
            return user_id
        except:
            # print('Unable to get the user id from event')
            pass
    return user_id


def get_email_from_event(event: _Event) -> str:
    email = None
    
    # Email will be in event by default.
    try:
        email = event['requestContext']['authorizer']['claims']['email']
    except:
        print('Unable to get the email from event!')
    
    return email


# This method will help us in escaping special charracters inside strings
def esacape_special_charracters(string: V) -> Union[V, str]:
    if not isinstance(string, str):
        return string
    string = string.translate(str.maketrans({"-":  r"\-",
                                          "]":  r"\]",
                                          "\\": r"\\",
                                          "^":  r"\^",
                                          "$":  r"\$",
                                          "*":  r"\*",
                                          "'":  r"''"}))
    return string
