#!/usr/bin/python
import json
import boto3
import sys
import argparse
from collections import OrderedDict
from Gateway import gateway_utils as gutils
from Lambda import lambda_utils as lutils
from Utils import naming
import lms_config

INPUT = "./"
ROLE = 'arn:aws:iam::787991150675:role/NavigatorBot'
RUNTIME = 'python3.12'
TIMEOUT = 60
VPC_CONFIG = {
                'SubnetIds': ['subnet-4b0b7c2c', 'subnet-8c6818d0',
                              'subnet-ac3d14a3', 'subnet-d65022f8',
                              'subnet-862423cc', 'subnet-5477cc6a'],
                'SecurityGroupIds': ['sg-14834a53']
             }
HANDLER='lambda_function.lambda_handler'
BASE_LAMBDA_ARN = 'arn:aws:lambda:us-east-1:787991150675:function:'

GATEWAY = boto3.client('apigateway')

API_NAME = naming.get_gateway_name(lms_config.NAME)

FUNCTION_NAME_PREFIX = naming.get_function_prefix(lms_config.NAME)

def process_resource_mapping(rest_api,
                             resource_name,
                             mappings,
                             parent_resource):
    print ('\t {}'.format(resource_name))
    
    resource = gutils.create_resource(rest_api, parent_resource, resource_name)

    rest_api['currentPath'] = resource['path']
    for key, maps in mappings.items():
        if key != "methods":
            # We have nested resource. So instantiate it depth first
            process_resource_mapping(rest_api, key, maps, resource)
        else:
            methods = maps
            # if you have methods, add options
            if methods:
                gutils.create_method(rest_api, resource, 'Dummy', 'OPTIONS')
            for method in methods:
                lambda_uri = BASE_LAMBDA_ARN + FUNCTION_NAME_PREFIX + method['function']
                authorizer = True
                try:
                    if method['authorizer'] and method['authorizer'] == 'False':
                        authorizer=False
                except:
                    pass
                response = gutils.create_method(rest_api, resource, lambda_uri, method['name'], authorizer=authorizer)
                response = lutils.add_permission_for_apigateway(rest_api, lambda_uri, method['name'])

    return


def main():
    try:
        parser = argparse.ArgumentParser(description='Setup Gateway and attach to lambda function')
        parser.add_argument('file')
        args = parser.parse_args()
        data = ''
    except Exception as e:
        print("unable to parse the arguements of the function!" + str(e))
        sys.exit(-1)
    print(args.file)

    rest_api = gutils.get_rest_api_by_name(API_NAME)
    if "lms" not in API_NAME:
        print("API name does not contain 'lms': {}".format(API_NAME))
        return
    if rest_api:
        print('API: {} with id: {} already exists!'
            .format(API_NAME, rest_api['id']))
        gutils.delete_all_resource(rest_api)

        try:
            # get existing authroizer information from the gateway
            authorizer = gutils.get_authorizers(rest_api)
            rest_api['authorizer'] = authorizer
        except:
            print('No authorizer has been defined for the gateway!')
            rest_api['authorizer'] = None
    else:
        # Create the API Gateway
        rest_api = gutils.create_rest_api(API_NAME)
        print('Created a new Gateway for Name: {} Id: {}'.format(API_NAME, rest_api['id']))
        rest_api['authorizer'] = None

    # Delete and create authorizers by default -- this will avoid the need to change the staging url
    if rest_api['authorizer']:
        # delete the existing cognito authorizer
        response = gutils.delete_authorizer(rest_api, rest_api['authorizer']['id'])

    # Add the cognito authroizer
    authorizer = gutils.create_authorizer(rest_api, 'Lms', 'COGNITO_USER_POOLS')
    rest_api['authorizer'] = authorizer

    root_resource = gutils.get_root_resource(rest_api)
    print(root_resource)

    print ('Processing resource: ')
    with open(args.file, 'r') as infile:
        data = json.load(infile, object_pairs_hook=OrderedDict)

    for resource, mappings in data.items():
        process_resource_mapping(rest_api, resource, mappings,
                                 root_resource)

    stage_name = 'Lms'
    # Needs to create a deployment to publish the API configuration
    gutils.create_deployment_resource(rest_api, stage_name)

    response = {}
    gateway_url_stub = '.execute-api.us-east-1.amazonaws.com/'
    response['invokeURL'] = 'https://' + rest_api['id']+ gateway_url_stub + stage_name
    response['restApiId'] = rest_api['id']
    print('Successfully Created {} with id: {} \n Deployed at {}'
        .format(API_NAME, response['restApiId'], response['invokeURL']))
    # Write the URL to .env
    print('Writing to ../.env file')
    out_file = open("../.env", "w")
    out_file.write('STAGING_URL={}\n'.format(response['invokeURL']))
    # Todo will need a custom domain name to map to the api url
    out_file.close()
    return response

if __name__ == '__main__':
    main()