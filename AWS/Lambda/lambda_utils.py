import boto3
from time import sleep
import json
import subprocess

LAMBDA = boto3.client('lambda')

ACCOUNT_ID = "787991150675"


def get_connection(client):
    if client:
        return client
    else:
        return LAMBDA


def get_zip_file_name(output_dir, function):
    return output_dir + function + ".zip"


def get_zipfile_bytes(function, output_dir):
    zip_file_name = get_zip_file_name(output_dir, function)
    with open(zip_file_name, "rb") as data:
        return data.read()


def add_permission(function_name,
                   principal,
                   source_arn,
                   action='lambda:InvokeFunction',
                   statement_id=None,
                   client=None):
    client = get_connection(client)
    if not statement_id:
        statement_id = function_name + 'statement1'
    try:
        # Trying to remove the existing permission if it exists
        response = client.remove_permission(FunctionName=function_name,
                                            StatementId=statement_id)
    except:
        pass
    response = client.add_permission(FunctionName=function_name,
                                     StatementId=statement_id,
                                     Action=action,
                                     Principal=principal,
                                     SourceArn=source_arn)
    return response


def add_permission_for_apigateway(rest_api, lambda_uri, http_method='POST',
                                  client=None, region='us-east-1', account='787991150675'):
    client = get_connection(client)
    rest_api_id = rest_api['id']
    statement_id = rest_api_id + '_' + http_method
    base_arn = 'arn:aws:execute-api:' + region + ':' + account + ':'
    source_arn = base_arn + rest_api_id + '/*/'+ http_method + rest_api['currentPath']
    # Example: arn:aws:execute-api:us-east-1:account_id:api_id/*/POST/resource_path
    action = 'lambda:InvokeFunction'
    principal = 'apigateway.amazonaws.com'
    response = add_permission(lambda_uri,
                              principal,
                              source_arn,
                              action,
                              statement_id,
                              client)
    return response


def is_lambda_defined(function, client=None):
    result = False
    client = get_connection(client)
    try:
        response = client.get_function(FunctionName=function)
        # print(response)
        metadata = response['ResponseMetadata']
        if metadata['HTTPStatusCode'] == 200 and response['Configuration']:
            if response['Configuration']['FunctionName'] == function:
                result = True
    except:
        pass
    return result


def delete_lambda(function, client=None):
    result = False
    client = get_connection(client)
    try:
        response = client.delete_function(FunctionName=function)
        # print(response)
        metadata = response['ResponseMetadata']
        if metadata['HTTPStatusCode'] == 200 or metadata['HTTPStatusCode'] == 204:
            # TODO: verify the results of the lambda delete response for function name
            result = True
    except Exception as e:
        print('Unable to delete lambda {}'.format(function) + str(e))
    return result


def create_lambda(function, mappings, config, client=None):
    output_dir = ''
    client = get_connection(client)
    try:
        # input_dir = config['inputDir']
        runtime = config['runtime']
        role = config['role']
        handler = config['handler']
        timeout = config['timeout']
        memory = config['memory']
        code_type = config['codeSource']
        output_dir = config['outputDir']
    except Exception as e:
        pass

    try:
        add_vpc = bool(mappings['vpc'])
        vpc_config = config['vpcConfig']
    except:
        add_vpc = False
        vpc_config = {}

    try:
        layers = mappings['layers']
    except:
        layers = []

    try:
        environment = mappings['environment']
        try:
            # Special case: we add the function prefix to help lambda call other lambdas
            if 'FN_NAME_PREFIX' in environment['Variables'].keys():
                fn_name_prefix = config['functionNamePrefix']
                environment['Variables']['FN_NAME_PREFIX'] = fn_name_prefix
        except:
            pass
        try:
            # Special case: we add the database suffix to help use private db
            if 'DB_NAME_SUFFIX' in environment['Variables'].keys():
                db_name_suffix = config['databaseNameSuffix']
                environment['Variables']['DB_NAME_SUFFIX'] = db_name_suffix
        except:
            pass
    except:
        environment = {}

    try:
        if code_type == 'local':
            code= {'ZipFile': get_zipfile_bytes(function, output_dir)}
        else:
            print('unsupported code type: {}'.format(code_type))
            code = {}
            return False
    except Exception as e:
        print('Error: ', str(e))
        pass

    retries = 0
    max_retries = 5
    response = None
    while retries < max_retries:
        try:
            response = client.create_function(FunctionName=function,
                                            Runtime=runtime,
                                            Role=role,
                                            Handler=handler,
                                            Code=code,
                                            Timeout=timeout,
                                            MemorySize=memory,
                                            VpcConfig=vpc_config,
                                            Environment=environment,
                                            Layers=layers)
            print(response)
            break

        except Exception as e:
            if 'TooManyRequestsException' in str(e):
                print(f"TooManyRequestsException: {str(e)}. Retrying with exponential backoff...")
                retries += 1
                backoff = 2**retries
                print(f'Attempting retry: {retries}, Retrying in {backoff}s......')
                sleep(backoff)    
                
            else:
                print('Unable to create lambda: {}. Error: {}'.format(function, str(e)))
                return e 
        
    if not response:
        message = "Max retries exceeded. Could not create Lambda function."
        print(message)
        return message
        
    try:
        metadata = response['ResponseMetadata']
        if metadata['HTTPStatusCode'] == 201 and response['FunctionName'] == function:
            print('Successfully created the lambda function: {} Arn: {}'.format(function, response['FunctionArn']))
            function_arn = response["FunctionArn"]
        else:
            print('Unable to create function: {} Response: {}'.format(function, response))
            return False
    except:
        return False

    return response


def update_lambda_code(function: str, output_dir: str, client=None):

    client = get_connection(client)

    zip_file = get_zipfile_bytes(function, output_dir)

    try:
        client.update_function_code(
            FunctionName=function,
            ZipFile=zip_file,
            Architectures=["x86_64"],
        )
    except Exception as exc:
        print(f"Failed to deploy {exc}")


def invoke_lambda(function_name,
                  body='',
                  query_string_params='',
                  invocation_type='RequestResponse',
                  client_context='',
                  http_method='POST',
                  client=None,
                  path=None):
    if not client:
        client = LAMBDA
    payload = {
        'body': body,
        'queryStringParameters': query_string_params,
        'httpMethod': http_method
    }
    if path:
        payload['path'] = path
    print(function_name, json.dumps(payload), invocation_type)
    try:
        response = client.invoke(FunctionName=function_name,
                             InvocationType=invocation_type,
                             LogType='Tail',
                             Payload=json.dumps(payload))
        if invocation_type == 'RequestResponse':
            response_payload = json.loads(response['Payload'].read().decode("utf-8"))
            print ("response_payload: {}".format(response_payload))
            return response_payload
        else:
            return response
    except Exception as e:
        print('Error: ', str(e))
        return None
