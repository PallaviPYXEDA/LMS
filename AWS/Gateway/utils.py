import boto3

APIGW = boto3.client('apigateway')


def create_rest_api(name, region='us-east-1'):
    """Create a gateway REST API endpoint

    Arguments:
        name {string} -- Name of the gateway REST API

    Keyword Arguments:
        region {string} -- Region to create the REST API
                           (default: {'us-east-1'})

    Returns:
        Dict -- Dictionary of the REST API object
    """
    description = 'REST API endpoint for the AI services'
    version = '0.1'
    endpointConfiguration = {'types': ['EDGE']}
    response = APIGW.create_rest_api(name=name, description=description,
                                     version=version)
    # TODO: check if the endpoint already exists

    # TODO: check for status code 201 (created)

    rest_api = {'id': response['id'],
                'name': response['name'],
                'createdDate': response['createdDate']
                }
    return rest_api


def get_resources(rest_api):
    """Returns the list of resources available under REST API

    Arguments:
        rest_api {Dict} -- Dictionary object containing the rest api object

    Returns:
        Dict -- dictionary of the resouces under the gateway REST API
    """
    response = APIGW.get_resources(restApiId=rest_api['id'])
    return response


def get_root_resource(rest_api):
    """[Returns the root resource of the REST API]

    Arguments:
        rest_api {[Dict]} -- [the gateway REST API object]

    Returns:
        [Dict] -- [the dictionary object with the root resource]
    """
    response = get_resources(rest_api)
    resource_items_list = response['items']
    root_item = {}
    for element in resource_items_list:
        if element['path'] == '/':
            root_item = element
            break
    return root_item


def create_put_method(rest_api, root_resource):
    """ Creates a POST method under the root resource
    Arguments:
        rest_api {[Dict]} -- [the gateway rest api object]
        root_resource {[Dict]} -- [the root resource of the rest api]

    Returns:
        [None]
    """
    # TODO: check if already exists
    try:
        response = APIGW.put_method(restApiId=rest_api['id'],
                                    resourceId=root_resource['id'],
                                    httpMethod='POST',
                                    authorizationType='NONE',
                                    operationName='Predict',
                                    apiKeyRequired=False)
        # print('Create POST Method Response: {}'.format(json.dumps(response)))
        # TODO: check for the return type
    except Exception as e:
        print('Error: {}'.format(e))
    return


def integrate_api_with_lambda(rest_api, root_resource, lambda_uri):
    """Integrate the API gateway with the passed Lambda URI

    Arguments:
        rest_api {Dict} -- Dictionary containing the REST API object
        root_resource {Dict} -- Dictionary containing the root resource
        lambda_uri {string} -- String containing the uri of the lambda function

    Returns:
        [Dict] -- response from the API gateway call
    """
    # URI: arn:aws:apigateway:{region}:{subdomain.service|service}:path|action/{service_api}
    gatewayUri = 'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/'
    # Invoke the passed lambda to do predictions
    lambdaUri = lambda_uri
    # Using the credentials to the NavigatorBot
    credentials = 'arn:aws:iam::787991150675:role/NavigatorBot'
    uri = gatewayUri + lambdaUri + '/invocations'
    print('Uri: {}'.format(uri))
    response = \
        APIGW.put_integration(restApiId=rest_api['id'],
                              resourceId=root_resource['id'],
                              httpMethod='POST',
                              type='AWS',
                              integrationHttpMethod='POST',
                              uri=uri,
                              credentials=credentials)
    return response


def put_method_response(rest_api, root_resource):
    """Configures the put method response to the REST API endpoint

    Arguments:
        rest_api {Dict} -- Dictionary containing the gateway REST API
        root_resource {Dict} -- Dictionary containing the root resource

    Returns:
        Dict -- Dictionary containing the response from the API gateway call
    """
    resp_model = {}
    resp_model['application/json'] = 'Empty'
    response = \
        APIGW.put_method_response(restApiId=rest_api['id'],
                                  resourceId=root_resource['id'],
                                  httpMethod='POST',
                                  statusCode='200',
                                  responseModels=resp_model)
    return response


def put_integration_response(rest_api, root_resource):
    """Configures the put method integration response

    Arguments:
        rest_api {Dict} -- Dictionary containing the gateway REST API
        root_resource {Dict} -- Dictionary containing the root resource

    Returns:
        Dict -- Dictionary containing the response from the API gateway call
    """
    resp_template = {}
    resp_template['application/json'] = ''
    response = APIGW.put_integration_response(restApiId=rest_api['id'],
                                              resourceId=root_resource['id'],
                                              httpMethod='POST',
                                              statusCode='200',
                                              selectionPattern='',
                                              responseTemplates=resp_template)
    return response


def create_deployment_resource(rest_api, stage_name='test'):
    """Deploys the gateway REST API to be accessible from outside

    Arguments:
        rest_api {Dict} -- Dictionary containing the gateway REST API
        stage_name {String} -- Stage name to use when deploying the REST API

    Returns:
        Dict -- Dictionary containing the response from the API gateway call
    """
    response = \
        APIGW.create_deployment(restApiId=rest_api['id'],
                                stageName=stage_name,
                                stageDescription='testing the API',
                                description='1st deployment')
    return response
