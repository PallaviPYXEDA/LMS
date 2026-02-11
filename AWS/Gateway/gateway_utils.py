import boto3

APIGW = boto3.client('apigateway')

def get_connection(client):
    if client:
        return client
    else:
        return APIGW


def create_rest_api(name, client=None):
    """
    """
    client = get_connection(client)
    description = 'REST API:{}'.format(name)
    version = '0.1'
    endpoint_configuration = {'types': ['REGIONAL']}
    response = client.create_rest_api(name=name,
                                      description=description,
                                      version=version,
                                      endpointConfiguration=endpoint_configuration)

    rest_api = {
        'id' : response['id'],
        'name' : response['name'],
        'createdDate': response['createdDate']
    }
    return rest_api


def get_resources(rest_api, client=None):
    """
    """
    client = get_connection(client)
    response = client.get_resources(restApiId=rest_api['id'], limit=500)
    return response


def get_root_resource(rest_api, client=None):
    """
    """
    response = get_resources(rest_api, client)
    resource_items_list = response['items']
    root_item = {}
    for element in resource_items_list:
        if element['path'] == '/':
            root_item = element
            break
    return root_item


def get_resource(rest_api, name, client=None):
    """Get the resource object for a given name

    Arguments:
        rest_api {Dictionary} -- Dictionary containing the rest api object
        name {string} -- name of the resource to search

    Returns:
        resource -- Dictionary containing resource object
    """
    response = get_resources(rest_api, client)
    resource_items_list = response['items']
    print(resource_items_list)
    resource = {}
    for element in resource_items_list:
        if 'pathPart' in element and element['pathPart'] == name:
            resource = element
            break
    return resource


def create_put_method(rest_api,
                      root_resource,
                      http_method,
                      authorization_type='NONE',
                      authorizer_id='',
                      client=None):
    client =  get_connection(client)
    try:
        if http_method != 'OPTIONS':
            response = client.put_method(restApiId=rest_api['id'],
                                         resourceId=root_resource['id'],
                                         httpMethod=http_method,
                                         authorizationType=authorization_type,
                                         authorizerId=authorizer_id,
                                         apiKeyRequired=False)
        else:
            response = client.put_method(restApiId=rest_api['id'],
                                         resourceId=root_resource['id'],
                                         httpMethod=http_method,
                                         authorizationType='NONE')
        # print('Create POST Method Response: {}'.format(json.dumps(response)))
        # TODO: check for the return type
    except Exception as e:
        print('Error: {}'.format(e))
    return response


def integrate_api_with_lambda(rest_api, root_resource,
                              lambda_uri, http_method,
                              use_proxy=False, client=None,
                              credentials=None,
                              region='us-east-1'):
    client = get_connection(client)
    if not credentials:
        credentials = 'arn:aws:iam::787991150675:role/NavigatorBot'
    # Tell api gateway to call the lambda function using the internal aws API
    gatewayUri = 'arn:aws:apigateway:'+ region + ':lambda:path/2015-03-31/functions/'
    lambdaUri = lambda_uri
    uri = gatewayUri + lambdaUri + '/invocations'

    if http_method != 'OPTIONS':
        if use_proxy:
            # AWS Proxy type will pass the entire request to the lambda function
            integration_type = 'AWS_PROXY'
        else:
            integration_type = 'AWS'
        response = \
            client.put_integration(restApiId=rest_api['id'],
                                   resourceId=root_resource['id'],
                                   httpMethod=http_method,
                                   type=integration_type,
                                   integrationHttpMethod='POST',
                                   uri=uri,
                                   credentials=credentials)
    else:
        # For OPTIONS method, we use MOCK integration
        # This is used to return the CORS headers
        req_templates = {}
        req_templates['application/json'] = '{"statusCode": 200}'
        response = \
            client.put_integration(restApiId=rest_api['id'],
                                   resourceId=root_resource['id'],
                                   httpMethod=http_method,
                                   type='MOCK',
                                   requestTemplates=req_templates)
    return response


def put_method_response(rest_api, root_resource, http_method, client=None):
    client = get_connection(client)
    resp_model = {}
    resp_model['application/json'] = 'Empty'
    if http_method != 'OPTIONS':
        response_params = {'method.response.header.Access-Control-Allow-Origin': False}
        response = \
            client.put_method_response(restApiId=rest_api['id'],
                                       resourceId=root_resource['id'],
                                       httpMethod=http_method,
                                       statusCode='200',
                                       responseParameters=response_params,
                                       responseModels=resp_model)
    else:
        # OPTIONS
        response_params = {
            'method.response.header.Access-Control-Allow-Headers': False,
            'method.response.header.Access-Control-Allow-Origin': False,
            'method.response.header.Access-Control-Allow-Methods': False
        }
        response = \
            client.put_method_response(restApiId=rest_api['id'],
                                       resourceId=root_resource['id'],
                                       httpMethod=http_method,
                                       statusCode='200',
                                       responseParameters=response_params,
                                       responseModels=resp_model)
    return response


def put_integration_response(rest_api, root_resource, http_method, client=None):
    client = get_connection(client)
    resp_template = {}
    resp_template['application/json'] = ''
    resp_params = {}
    resp_params['method.response.header.Access-Control-Allow-Origin'] = '\'*\''
    if http_method != 'OPTIONS':
        response_params = {'method.response.header.Access-Control-Allow-Origin': '\'*\''}
        response = \
            client.put_integration_response(restApiId=rest_api['id'],
                                            resourceId=root_resource['id'],
                                            httpMethod=http_method,
                                            statusCode='200',
                                            selectionPattern='',
                                            responseParameters=response_params,
                                            responseTemplates=resp_template)
    else:
        response_params = {
            'method.response.header.Access-Control-Allow-Headers': '\'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token\'',
            'method.response.header.Access-Control-Allow-Methods': '\'POST,OPTIONS,PATCH,GET,DELETE\'',
            'method.response.header.Access-Control-Allow-Origin': '\'*\''
        }
        response = \
            client.put_integration_response(restApiId=rest_api['id'],
                                            resourceId=root_resource['id'],
                                            httpMethod=http_method,
                                            statusCode='200',
                                            selectionPattern='',
                                            responseParameters=response_params,
                                            responseTemplates=resp_template)
    return response


def create_deployment_resource(rest_api, stage_name='test', client=None):
    client = get_connection(client)
    response = \
        client.create_deployment(restApiId=rest_api['id'],
                                 stageName=stage_name,
                                 stageDescription='testing the API',
                                 description='1st deployment')
    return response


def get_rest_api_by_name(name, client=None):
    client = get_connection(client)
    paginator = client.get_paginator('get_rest_apis')
    page_iterator = paginator.paginate()
    for page in page_iterator:
        for item in page['items']:
            try:
                if item['name'] == name:
                    rest_api = {'id' : item['id'],
                                'name' : item['name'],
                                'createdDate': item['createdDate']
                                }
                    return rest_api
            except:
                pass
    print('Rest API Name: {} was not found!'.format(name))
    return


def delete_rest_api(rest_api, client=None):
    client = get_connection(client)
    response = client.delete_rest_api(restApiId=rest_api['id'])
    # TODO: check response and return the appropriate error
    return


def create_resource(rest_api, parent_resource, name, client=None):
    client = get_connection(client)
    response = client.create_resource(restApiId=rest_api['id'],
                                     parentId=parent_resource['id'],
                                     pathPart=name)
    # TODO: Validate response
    del response['ResponseMetadata']
    return response


def delete_resource(rest_api, resource, client=None):
    client = get_connection(client)
    response = client.delete_resource(restApiId=rest_api['id'],
                                     resourceId=resource['id'])
    return response


def delete_all_resource(rest_api, client=None):
    client = get_connection(client)
    paginator = client.get_paginator('get_resources')
    response_iterator = paginator.paginate(restApiId=rest_api['id'])
    for response in response_iterator:
        #del items['ResponseMetadata']
        items = response["items"]
        for item in items:
            try:
                delete_resource(rest_api, item, client)
            except:
                pass
    # TODO: Validate response
    # print(response)
    return


def create_method(rest_api, resource, lambda_uri, method_type, authorizer=True, client=None):
    client = get_connection(client)
    try:
        if authorizer and rest_api['authorizer']:
            response = create_put_method(rest_api,
                                         resource,
                                         method_type,
                                         'COGNITO_USER_POOLS',
                                         rest_api['authorizer']['id'])
        else:
            response = create_put_method(rest_api, resource, method_type)
    except:
        # No authorizer has been defined. Configuring the method without authorization
        response = create_put_method(rest_api, resource, method_type)
    response = put_method_response(rest_api, resource, method_type)
    # print('Put Method Response: {}'.format(response))
    response = integrate_api_with_lambda(rest_api, resource, lambda_uri, method_type, use_proxy=True)
    response = put_integration_response(rest_api, resource, method_type)
    return


def create_authorizer(rest_api, name, auth_type, client=None):
    client = get_connection(client)
    provider_arns = ['arn:aws:cognito-idp:us-east-1:787991150675:userpool/us-east-1_lv776GRgS']
    identity_source = 'method.request.header.Authorization'
    response = client.create_authorizer(restApiId=rest_api['id'],
                                       name=name,
                                       type=auth_type,
                                       providerARNs=provider_arns,
                                       identitySource=identity_source
                                       )
    # TODO: validate response and error handling!
    del response['ResponseMetadata']
    # print(response)
    return response


def delete_authorizer(rest_api, authorizer_id, client=None):
    client = get_connection(client)
    response = client.delete_authorizer(restApiId=rest_api['id'], authorizerId=authorizer_id)
    return response


def get_authorizers(rest_api, client=None):
    client = get_connection(client)
    response = client.get_authorizers(restApiId=rest_api['id'])
    # TODO: Assuming one authorizer for the gateway. Need to handle this better!
    return response['items'][0]
