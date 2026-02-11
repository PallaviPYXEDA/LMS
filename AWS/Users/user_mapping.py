from typing import Dict, Any

from Utils import request_utils as req_utils
from Utils import response_utils as rutils
from Utils import router
from RDS import db_utils

TABLE_NAME = 'unified_users'


def process_post_request(event: dict, context: object) -> Dict[str, Any]:
    params = event["body"]

    cognito_user_id = req_utils.get_params(params, "cognitoUserId")
    unified_user_id = req_utils.get_params(params, "unifiedUserId")
    email = req_utils.get_params(params, "email")
    
    data = {
        "unified_user_id": unified_user_id,
        "cognito_user_id": cognito_user_id,
        "email": email,
    }

    try:
        statement, sql_params = db_utils.create_parameterized_insert_statement(
            data, TABLE_NAME
        )
        db_utils.conn.cursor().execute(statement, sql_params)

    except Exception as e:
        message = (
            f"Unable to create the unified user: {unified_user_id}. Error: "
            + str(e)
        )
        error = {
            "errorCode": None,
            "message": message,
            "suggestions": ["Please contact info@aiclub.world for assistance"],
        }
        return rutils.failure_response([error])

    return rutils.success_response()



def lambda_handler(event: dict, context: object):
    print("Event:", event)

    default_route = router.path_router(
        "",
        post=process_post_request,
    )

    return router.route(
        event,
        context,
        rutils.success_method,
        None,
        rutils.unsupported_method,
        default_route,
    )