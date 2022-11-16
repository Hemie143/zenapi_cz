import requests

# TODO: Add logging


class zenAPISession(requests.Session):

    def __init__(self, *args, **kwargs):
        super(zenAPISession, self).__init__(*args, **kwargs)

        # TODO: Add retries (total)

        """
        retries = Retry(total=3,
                        backoff_factor=1,
                        status_forcelist=[ 500, 502, 503, 504, 405 ],
        )
        self.mount('https://',
                   HTTPAdapter(max_retries=retries)
        )
        """
        self.headers.update({
            'Accept-Charset': 'utf-8',
            'Content-Type': 'application/json',
        })
        return

    def init_api_auth(self, apikey):
        self.headers.update({
            'z-api-key': apikey
        })
