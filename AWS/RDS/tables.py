"""
All the master tables for us to track
"""

# NOTE: Please add an entry in the table map when you add a new table
TABLE_MAP = {
    "course": "course",
    "unifiedUsers": "unified_users",
}

TABLES = {}

TABLES["course"] = (
    "CREATE TABLE IF NOT EXISTS `course` ("
    "  `course_id` varchar(36) NOT NULL,"
    "  `name` varchar(36) NOT NULL,"
    "  PRIMARY KEY (`course_id`)"
    ")"
)
TABLES["UnifiedUsers"] = (
    "CREATE TABLE IF NOT EXISTS `unified_users` ("
    "  `unified_user_id` varchar(36) NOT NULL,"
    "  `cognito_user_id` varchar(36) NOT NULL,"
    "  `email` varchar(64) NOT NULL,"
    "  `timestamp` timestamp DEFAULT CURRENT_TIMESTAMP,"
    "  PRIMARY KEY (`unified_user_id`)"
    ")"
)

# List of tables and columns to be indexed
index_tables = {}


def get_actual_table_name(table_name):
    try:
        actual_name = TABLE_MAP[table_name]
    except:
        return ""
    return actual_name
