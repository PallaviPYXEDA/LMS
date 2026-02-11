from Utils import request_utils as req_utils
from Utils import response_utils as rutils
from Utils import router
from RDS import db_utils

TABLE_NAME = "unified_users"
EMAILS_TO_IGNORE = ["aiclub-user@pyxeda.ai", "info@pyxeda.ai", "support@pyxeda.ai"]


def get_unified_user_id(event: dict, context: object) -> str:
    unified_user_id = None
    email = None

    cognito_user_id = req_utils.get_cognito_user_id_from_event(event)
    print(f"Cognito User ID: {cognito_user_id}")

    email = req_utils.get_email_from_event(event)
    print(f"Email: {email}")

    if email:
        if email in EMAILS_TO_IGNORE:
            statement = f"SELECT unified_user_id FROM {TABLE_NAME} WHERE cognito_user_id = '{cognito_user_id}'"
        else:
            statement = (
                f"SELECT unified_user_id FROM {TABLE_NAME} WHERE email = '{email}'"
            )

        try:
            response = db_utils.execute_statement(statement)
        except Exception as e:
            print("Unable to execute the statement! Error: " + str(e))
            response = None

        if response:
            try:
                unified_user_id = response[0][0]
            except Exception as e:
                print(
                    "Unable to parse the response from the database! Error: " + str(e)
                )

    response = {"unifiedUserId": unified_user_id}
    return rutils.success_response(response)


def lambda_handler(event: dict, context: object):
    print("Event:", event)

    default_route = router.path_router(
        "",
        get=get_unified_user_id,
    )

    return router.route(
        event,
        context,
        rutils.success_method,
        None,
        rutils.unsupported_method,
        default_route,
    )
