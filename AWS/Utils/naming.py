import sys

def get_gateway_name(name):
    gateway_name = name.lower()
    print('Using Gateway: {}'.format(gateway_name))
    return gateway_name


def get_function_prefix(name: str) -> str:
    name = name.lower()
    if name == 'production':
        fn_name_prefix = 'LMS_PRODUCTION_'
    elif name == 'staging':
        fn_name_prefix = 'LMS_Staging_'
    elif name == 'dev':
        fn_name_prefix = 'LMS_Dev_'
    elif name  == '<username>':
        print('Please enter a valid name!')
        sys.exit()
    else:
        fn_name_prefix = name + '_'
    # print('Using Function name prefix: {}'.format(fn_name_prefix))
    return fn_name_prefix


def get_pinecone_namespace(name: str) -> str:
    if "production" in name:
        return "production"
    elif "staging" in name:
        return "staging"
    else:
        return name[:-1]

def get_db_suffix(name: str) -> str:
    name = name.lower()
    if name == 'production':
        db_name_suffix = '_PRODUCTION'
    elif name == 'staging':
        db_name_suffix = '_staging'
    elif name == 'dev':
        db_name_suffix = '_dev'
    elif name  == '<username>':
        print('Please enter a valid name!')
        sys.exit()
    else:
        db_name_suffix = '_' + name
    print('Using DB name suffix: {}'.format(db_name_suffix))
    return db_name_suffix