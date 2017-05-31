import datetime
import kadabra

from mock import call, Mock, patch

from django.conf import settings
from django.test import SimpleTestCase
from django.test.utils import override_settings

from django_kadabra.middleware import KadabraMiddleware


NOW = datetime.datetime.utcnow()


@patch('django_kadabra.middleware.kadabra')
class MiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.get_response = Mock()
        self.request = Mock()

    def get_middleware(self):
        return KadabraMiddleware(self.get_response)

    def get_metrics_mock(self, middleware):
        middleware.kadabra.metrics.return_value = Mock(
            spec=['add_count', 'set_timer', 'close']
        )
        return middleware.kadabra.metrics.return_value

    def test_ctor_kadabra_called_with_no_config(self, mock_kadabra):
        middleware = self.get_middleware()
        mock_kadabra.Kadabra.assert_called_once_with({})
        self.assertEqual(middleware.kadabra, mock_kadabra.Kadabra.return_value)

    @override_settings(KADABRA_CONFIG=Mock())
    def test_ctor_kadabra_called_with_config(self, mock_kadabra):
        middleware = self.get_middleware()
        mock_kadabra.Kadabra.assert_called_once_with(settings.KADABRA_CONFIG)
        self.assertEqual(middleware.kadabra, mock_kadabra.Kadabra.return_value)

    @patch('django_kadabra.middleware._get_now')
    def test_call_no_failure(self, mock_now, mock_kadabra):
        mock_now.side_effect = [
            NOW,
            NOW + datetime.timedelta(seconds=3)
        ]
        self.get_response.return_value.status_code = 200

        middleware = self.get_middleware()
        metrics = self.get_metrics_mock(middleware)
        response = middleware(self.request)

        self.assertEqual(response, self.get_response.return_value)
        metrics.add_count.assert_has_calls([
            call("Failure", 0),
            call("ClientError", 0),
        ])
        metrics.set_timer.assert_called_once_with(
            "RequestTime",
            NOW + datetime.timedelta(seconds=3) - NOW,
            mock_kadabra.Units.MILLISECONDS
        )
        metrics.close.assert_called_once_with()
        middleware.kadabra.send.assert_called_once_with(metrics.close.return_value)

    @patch('django_kadabra.middleware._get_now')
    def test_call_failure(self, mock_now, mock_kadabra):
        mock_now.side_effect = [
            NOW,
            NOW + datetime.timedelta(seconds=3)
        ]
        self.get_response.return_value.status_code = 500

        middleware = self.get_middleware()
        metrics = self.get_metrics_mock(middleware)
        response = middleware(self.request)

        self.assertEqual(response, self.get_response.return_value)
        metrics.add_count.assert_has_calls([
            call("Failure", 1),
            call("ClientError", 0),
        ])
        metrics.set_timer.assert_called_once_with(
            "RequestTime",
            NOW + datetime.timedelta(seconds=3) - NOW,
            mock_kadabra.Units.MILLISECONDS
        )
        metrics.close.assert_called_once_with()
        middleware.kadabra.send.assert_called_once_with(metrics.close.return_value)

    @patch('django_kadabra.middleware._get_now')
    def test_call_client_error(self, mock_now, mock_kadabra):
        mock_now.side_effect = [
            NOW,
            NOW + datetime.timedelta(seconds=3)
        ]
        self.get_response.return_value.status_code = 400

        middleware = self.get_middleware()
        metrics = self.get_metrics_mock(middleware)
        response = middleware(self.request)

        self.assertEqual(response, self.get_response.return_value)
        metrics.add_count.assert_has_calls([
            call("Failure", 0),
            call("ClientError", 1),
        ])
        metrics.set_timer.assert_called_once_with(
            "RequestTime",
            NOW + datetime.timedelta(seconds=3) - NOW,
            mock_kadabra.Units.MILLISECONDS
        )
        metrics.close.assert_called_once_with()
        middleware.kadabra.send.assert_called_once_with(metrics.close.return_value)

    @override_settings(DISABLE_KADABRA=True)
    @patch('django_kadabra.middleware._get_now')
    def test_call_metrics_not_sent_when_kadabra_disabled(self, mock_now, mock_kadabra):
        mock_now.side_effect = [
            NOW,
            NOW + datetime.timedelta(seconds=3)
        ]
        self.get_response.return_value.status_code = 400

        middleware = self.get_middleware()
        metrics = self.get_metrics_mock(middleware)
        response = middleware(self.request)

        metrics.close.assert_called_once_with()
        self.assertFalse(middleware.kadabra.send.called)

