# config file containing credentials for RDS MySQL instance

prod_db_name = "lms"
# credentials for rds data api
prod_db_cluster_arn = "arn:aws:rds:us-east-1:787991150675:cluster:navigator-aurora-v8-cluster"
prod_db_secret_arn = "arn:aws:secretsmanager:us-east-1:787991150675:secret:rds-db-credentials/cluster-CA32ZZXBGOIAE7GVOP6MZ7EJ3E/bot-lzSfZx"

others_db_name = "lms"
# credentials for rds data api
others_db_cluster_arn = 'arn:aws:rds:us-east-1:787991150675:cluster:navigator-others-v8-cluster'
others_db_secret_arn = 'arn:aws:secretsmanager:us-east-1:787991150675:secret:rds-db-credentials/cluster-YFSLCNCTMGOCE3I5A3SCSBQLKU/bot-67Z2c1'
