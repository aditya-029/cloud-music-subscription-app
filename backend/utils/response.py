from flask import jsonify


def success_response(data=None, message="success", status_code=200):
    return (
        jsonify(
            {
                "success": True,
                "message": message,
                "data": data,
            }
        ),
        status_code,
    )


def error_response(message="error", status_code=400, data=None):
    return (
        jsonify(
            {
                "success": False,
                "message": message,
                "data": data,
            }
        ),
        status_code,
    )


def validation_error_response(missing_fields):
    return error_response(
        message="Missing required field(s)",
        status_code=400,
        data={"missing_fields": missing_fields},
    )
