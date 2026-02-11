#!/usr/bin/python
import os
import sys
import json
import boto3
import lms_config as lms_config
from Lambda import lambda_utils as lutils
from Utils import naming

FUNCTION_NAME_PREFIX = naming.get_function_prefix(lms_config.NAME)

def invoke_functions(function):
    print ('\t{}{}'.format(FUNCTION_NAME_PREFIX, function))
    function = FUNCTION_NAME_PREFIX + function
    body = {}
    response = lutils.invoke_lambda(function,
                                    body=body,
                                    query_string_params=None,
                                    invocation_type='RequestResponse',
                                    http_method='POST')
    print(response)

def main():
    invoke_functions('dbInitLms')
    return True

if __name__ == '__main__':
    main()