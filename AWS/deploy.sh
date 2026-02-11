#!/bin/bash

# deploy - A script to deploy our product across different location

deploy()
{
    echo "Deploying LMS ..."

    echo "Updating Lambda ..."
    sh update_all_lambda.sh --create

	# Initialize/Update database
    echo "Initialize/Update Database"
    python3 initialize_db_gateway.py

    # # Updating Gateway node
    echo "Updating Gateway ..."
    python3 setup_gateway.py gateway_map.json
}

# MAIN
deploy