#!/usr/bin/python
import os
import sys
import json
import argparse
from collections import OrderedDict

import boto3
import lms_config
from Lambda import lambda_utils as lutils
from Lambda import lambda_packager
from Utils import naming

INPUT_DIR = "./"
OUTPUT_DIR = "build/"
# This is the role used for navigator lambda functions
ROLE = 'arn:aws:iam::787991150675:role/NavigatorBot'
RUNTIME = 'python3.12'
TIMEOUT = 60
MEMORY = 128
# Need to change vpc config?
# Is it ok to use same vpc and subnets for lms?
# How does route tables, ACLs gets configured
# These are same vpcs used for navigator as well, do not delete
VPC_CONFIG = {
                'SubnetIds': ['subnet-4b0b7c2c', 'subnet-8c6818d0',
                              'subnet-ac3d14a3', 'subnet-d65022f8',
                              'subnet-862423cc', 'subnet-5477cc6a'],
                'SecurityGroupIds': ['sg-14834a53']
             }
HANDLER = 'lambda_function.lambda_handler'

FUNCTION_NAME_PREFIX = naming.get_function_prefix(lms_config.NAME)
DATABASE_NAME_SUFFIX = naming.get_db_suffix(lms_config.LOCATION)

LAMBDA = boto3.client('lambda')


def add_env_variables(mappings):
    """Add environment variables to all functions

    Arguments:
        mapping {Dictionary} -- Containing the function requirement
    Return:
        None -- mapping now contains env variables added
    """
    if 'environment' not in mappings:
        mappings['environment'] = {
            'Variables': {
                'FN_NAME_PREFIX': '',
                'DB_NAME_SUFFIX': ''
            }
        }
    else:
        # Keep the existing values intact
        mappings['environment']['Variables']['FN_NAME_PREFIX'] = ''
        mappings['environment']['Variables']['FN_NAME_PREFIX'] = ''

def process_function(base_function_name: str, mappings, config, args):
    print ('\t{}{}'.format(FUNCTION_NAME_PREFIX, base_function_name))
    # Add FN_NAME_PREFIX environment variable to all lambda functions
    add_env_variables(mappings)
    print('Adding environment variables to function: {}'.format(base_function_name))
    function = FUNCTION_NAME_PREFIX + base_function_name
    if not function.startswith('lms'):
        print('Function name does not start with lms: {}'.format(function))
        return 'Function name does not start with lms: {}'.format(function)
    if 'skip' in mappings and mappings['skip'] == 'True':
        print('Skipping function: ', function)
        return
    if args.create:
        lutils.delete_lambda(function)
    print('Preparing zip file for function: {}'.format(function))
    lambda_packager.prepare_zip_file(function, mappings, INPUT_DIR, OUTPUT_DIR)
    is_defined = lutils.is_lambda_defined(function)
    if is_defined:
        lutils.update_lambda_code(function, OUTPUT_DIR)
    else:
        # Check and overwrite the memory and timeout parameters
        if 'timeout' in mappings or \
            'memory' in mappings:
            my_config = config.copy()
            if 'timeout' in mappings:
                my_config['timeout'] = mappings['timeout']
            if 'memory' in mappings:
                my_config['memory'] = mappings['memory']
            config = my_config
        lutils.create_lambda(function, mappings, config)

def main():
    try:
        parser = argparse.ArgumentParser(description='Upload lambda files to the aws lambda function')
        parser.add_argument('--function', action='store', dest='selected_function', default='')
        parser.add_argument('--create', action='store_true', dest='create')
        # parser.add_argument("-d", "--dry_run", type=bool, help="don't update but do everything else", default=False)
        args = parser.parse_args()
        data = ''
    except Exception as e:
        print("unable to parse the arguements of the function!" + str(e))
        sys.exit(-1)

    config = {
        'inputDir': INPUT_DIR,
        'outputDir': OUTPUT_DIR,
        'runtime': RUNTIME,
        'role': ROLE,
        'handler': HANDLER,
        'timeout': TIMEOUT,
        'memory': MEMORY,
        'vpcConfig': VPC_CONFIG,
        'functionNamePrefix': FUNCTION_NAME_PREFIX,
        'codeSource': 'local',
        'databaseNameSuffix': DATABASE_NAME_SUFFIX
    }
    
    # Get the mapping.json files from all the folders
    mapping_files = []
    folders = [name for name in os.listdir(".") if os.path.isdir(name)]
    for folder in folders:
        filename = folder + '/'+ 'mapping.json'
        if os.path.exists(filename):
            mapping_files.append(filename)


    # Going over all the mapping.json files
    for filename in mapping_files:
        print('Working on functions in file: {}'.format(filename))
        with open(filename, 'r') as infile:
            data = json.load(infile, object_pairs_hook=OrderedDict)

        if args.selected_function:
            mappings = data.get(args.selected_function)
            if mappings:
                print('Processing function:')
                process_function(args.selected_function, mappings, config, args)
                return True
        else:
            print('Processing function:')
            for function, mappings in data.items():
                process_function(function, mappings, config, args)
    return True

if __name__ == '__main__':
    main()