from typing import Any, Dict, List, TypeVar, TypedDict, Union

T = TypeVar("T")
U = TypeVar("U")

Optional = Union[T, None]

Headers = TypedDict(
    "Headers",
    {
        "accept": str,
        "accept-encoding": str,
        "accept-language": str,
        "Authorization": str,
        "Host": str,
        "origin": str,
        "referer": str,
        "sec-ch-ua": str,
        "sec-ch-ua-mobile": str,
        "sec-ch-ua-platform": str,
        "sec-fetch-dest": str,
        "sec-fetch-mode": str,
        "sec-fetch-site": str,
        "User-Agent": str,
        "X-Amzn-Trace-Id": str,
        "X-Forwarded-For": str,
        "X-Forwarded-Port": str,
        "X-Forwarded-Proto": str,
    },
)


MultiValueHeaders = TypedDict(
    "MultiValueHeaders",
    {
        "accept": List[str],
        "accept-encoding": List[str],
        "accept-language": List[str],
        "Authorization": List[str],
        "Host": List[str],
        "origin": List[str],
        "referer": List[str],
        "sec-ch-ua": List[str],
        "sec-ch-ua-mobile": List[str],
        "sec-ch-ua-platform": List[str],
        "sec-fetch-dest": List[str],
        "sec-fetch-mode": List[str],
        "sec-fetch-site": List[str],
        "User-Agent": List[str],
        "X-Amzn-Trace-Id": List[str],
        "X-Forwarded-For": List[str],
        "X-Forwarded-Port": List[str],
        "X-Forwarded-Proto": List[str],
    },
)


Claims = TypedDict(
    "Claims",
    {
        "at_hash": str,
        "sub": str,
        "cognito:groups": str,
        "email_verified": str,
        "iss": str,
        "custom:accountType": str,
        "cognito:username": str,
        "picture": str,
        "aud": str,
        "identities": str,
        "token_use": str,
        "auth_time": str,
        "name": str,
        "exp": str,
        "iat": str,
        "email": str,
    },
)


class Authorizer(TypedDict):
    claims: Claims


class Identity(TypedDict):
    cognitoIdentityPoolId: Optional[str]
    accountId: Optional[str]
    cognitoIdentityId: Optional[str]
    caller: Optional[str]
    sourceIp: str
    principalOrgId: Optional[str]
    accessKey: Optional[str]
    cognitoAuthenticationType: Optional[str]
    cognitoAuthenticationProvider: Optional[str]
    userArn: Optional[str]
    userAgent: str
    user: Optional[str]


class RequestContext(TypedDict):
    resourceId: str
    authorizer: Authorizer
    resourcePath: str
    # httpMethod: Literal["GET", "POST", "PATCH", "DELETE"]
    httpMethod: str
    extendedRequestId: str
    requestTime: str
    path: str
    accountId: str
    protocol: str
    stage: str
    domainPrefix: str
    requestTimeEpoch: int
    requestId: str
    identity: Identity
    domainName: str
    apiId: str


class ApiGatewayEvent(TypedDict, total=False):
# class ApiGatewayEvent(TypedDict, Generic[T, U], total=False):
    resource: str
    path: str
    # httpMethod: Literal["GET", "POST", "PATCH", "DELETE"]
    httpMethod: str
    headers: Headers
    multiValueHeaders: MultiValueHeaders
    # queryStringParameters: T
    multiValueQueryStringParameters: Optional[Dict[str, List[Any]]]
    pathParameters: Optional[Dict[str, str]]
    stageVariables: Optional[Dict[str, str]]
    requestContext: RequestContext
    # body: U
    isBase64Encoded: bool


class RequestStub(TypedDict):
    pass