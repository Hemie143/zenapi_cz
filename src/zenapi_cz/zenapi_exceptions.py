# Take a HTTP response object and translate it into an Exception
# instance.
def handle_error_response(resp):
    # Mapping of API response codes to exception classes
    codes = {
        -1: ZenossCZAPIError,
    }

    error = resp.json().get('error', {})
    message = error.get('message')
    code = error.get('code', -1)
    data = error.get('data', {})

    # Build the appropriate exception class with as much
    # data as we can pull from the API response and raise
    # it.
    raise codes[code](message=message, code=code, data=data, response=resp)


class ZenossCZAPIError(Exception):
    response = None
    data = {}
    code = -1
    message = "An unknown error occurred"

    def __init__(self, message=None, code=None, data={}, response=None):
        self.response = response
        if message:
            self.message = message
        if code:
            self.code = code
        if data:
            self.data = data

    def __str__(self):
        if self.code:
            return '{}: {}'.format(self.code, self.message)
        return self.message

# Specific exception classes

class ParseError(ZenossCZAPIError):
    pass


class InvalidRequest(ZenossCZAPIError):
    pass

