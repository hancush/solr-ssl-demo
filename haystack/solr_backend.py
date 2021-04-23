'''
Subclass of Solr classes enabling passing of local cert with Solr requests.
Configuration looks like:

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': '${SOME_MODULE}.solr_backend.SecureSolrEngine',
        'URL': ${SOME_URL},
        'CERT': 'ssl/test.pem',
        'KWARGS': {
            'verify': False,  # For self-signed certificates
        },
    },
}
'''
from haystack.backends.solr_backend import SolrSearchBackend, SolrEngine
from pysolr import Solr


class SecureSolr(Solr):
    '''
    https://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification
    '''
    def __init__(self, url, cert, **kwargs):
        self.cert = cert
        super().__init__(url, **kwargs)

    def _send_request(self, method, path="", body=None, headers=None, files=None):
        '''
        Had to override this entire method from source to add the cert kwarg
        to the request. Source: https://github.com/django-haystack/pysolr/blob/560a94bd16c782c6b69af6a461d4b64c38b079a2/pysolr.py#L387-L471
        '''
        url = self._create_full_url(path)
        method = method.lower()
        log_body = body

        if headers is None:
            headers = {}

        if log_body is None:
            log_body = ""
        elif not isinstance(log_body, str):
            log_body = repr(body)

        self.log.debug(
            "Starting request to '%s' (%s) with body '%s'...",
            url,
            method,
            log_body[:10],
        )
        start_time = time.time()

        session = self.get_session()

        try:
            requests_method = getattr(session, method)
        except AttributeError:
            raise SolrError("Unable to use unknown HTTP method '{0}.".format(method))

        # Everything except the body can be Unicode. The body must be
        # encoded to bytes to work properly on Py3.
        bytes_body = body

        if bytes_body is not None:
            bytes_body = force_bytes(body)
        try:
            resp = requests_method(
                url,
                data=bytes_body,
                headers=headers,
                files=files,
                timeout=self.timeout,
                auth=self.auth,
                cert=self.cert
            )
        except requests.exceptions.Timeout as err:
            error_message = "Connection to server '%s' timed out: %s"
            self.log.exception(error_message, url, err)  # NOQA: G200
            raise SolrError(error_message % (url, err))
        except requests.exceptions.ConnectionError as err:
            error_message = "Failed to connect to server at %s: %s"
            self.log.exception(error_message, url, err)  # NOQA: G200
            raise SolrError(error_message % (url, err))
        except HTTPException as err:
            error_message = "Unhandled error: %s %s: %s"
            self.log.exception(error_message, method, url, err)  # NOQA: G200
            raise SolrError(error_message % (method, url, err))

        end_time = time.time()
        self.log.info(
            "Finished '%s' (%s) with body '%s' in %0.3f seconds, with status %s",
            url,
            method,
            log_body[:10],
            end_time - start_time,
            resp.status_code,
        )

        if int(resp.status_code) != 200:
            error_message = "Solr responded with an error (HTTP %s): %s"
            solr_message = self._extract_error(resp)
            self.log.error(
                error_message,
                resp.status_code,
                solr_message,
                extra={
                    "data": {
                        "headers": resp.headers,
                        "response": resp.content,
                        "request_body": bytes_body,
                        "request_headers": headers,
                    }
                },
            )
            raise SolrError(error_message % (resp.status_code, solr_message))

        return force_unicode(resp.content)


class SecureSolrSearchBackend(SolrSearchBackend):
    '''
    Issue secure Solr requests.
    Source: https://github.com/django-haystack/django-haystack/blob/master/haystack/backends/solr_backend.py
    '''

    def __init__(self, connection_alias, **connection_options):
        super().__init__(connection_alias, **connection_options)

        self.conn = SecureSolr(
            connection_options['URL'],
            connection_options['CERT'],
            timeout=self.timeout,
            **connection_options.get("KWARGS", {})
        )


class SecureSolrEngine(SolrEngine):
    backend = SecureSolrSearchBackend
