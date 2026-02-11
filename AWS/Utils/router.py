from typing import Any, Callable, Dict, Union

from Utils import type_stubs as ts

Context = object
RouteFunction = Union[Callable[[ts.ApiGatewayEvent, Context], Any], None]
Router = Dict[str, Union[str, RouteFunction]]


class UnsupportedMethod(Exception):
    """ "Unsupported method"""


def path_router(
    path: str,
    *,
    get: RouteFunction = None,
    post: RouteFunction = None,
    patch: RouteFunction = None,
    delete: RouteFunction = None,
) -> Router:
    return {"path": path, "GET": get, "POST": post, "PATCH": patch, "DELETE": delete}


def route(
    event: ts.ApiGatewayEvent,
    context: Context,
    success_func,
    failure_func,
    unsupported_func,
    default_router: Router,
    *args: Router,
):
    try:
        http_method = event["httpMethod"]
    except Exception as e:
        return unsupported_func(event, context, e)

    path = event.get("path", None)
    path_router = default_router
    handler = None

    if path:
        for router in args:
            if router["path"] == path:
                path_router = router
                break

    try:
        handler = path_router[http_method]
    except KeyError:
        return unsupported_func(event, context, e)

    try:
        response = handler(event, context)
    except Exception as e:
        return unsupported_func(event, context, e)

    return success_func(response)
