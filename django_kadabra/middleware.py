import kadabra

from django.conf import settings

from django_kadabra.utils import _get_now


class KadabraMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

        config = getattr(settings, 'KADABRA_CONFIG', {})
        self.kadabra = kadabra.Kadabra(config)

    def __call__(self, request):
        request.metrics = self.kadabra.metrics()
        start_time = _get_now()

        response = self.get_response(request)

        failure = 0
        client_error = 0
        if response.status_code >= 500:
            failure = 1
        elif response.status_code >= 400:
            client_error = 1

        request.metrics.set_timer(
            "RequestTime",
            _get_now() - start_time,
            kadabra.Units.MILLISECONDS
        )
        request.metrics.add_count("Failure", failure)
        request.metrics.add_count("ClientError", client_error)
        closed = request.metrics.close()
        if not getattr(settings, 'DISABLE_KADABRA', False):
            self.kadabra.send(closed)

        return response

