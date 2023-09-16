from http import HTTPStatus

from apps.errors import blueprint
from apps.errors.errors import APIError


@blueprint.app_errorhandler(APIError)
def invalid_api_usage(error):
    return error.to_dict(), error.status_code


@blueprint.app_errorhandler(Exception)
def unknown_error(error):
    error_response = {
        "status": "error",
        "description": str(error)
    }
    return error_response, HTTPStatus.BAD_REQUEST
