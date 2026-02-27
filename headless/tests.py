from django.test import Client, SimpleTestCase


class HeadlessApiTests(SimpleTestCase):
    def setUp(self):
        self.client = Client()

    def test_health_endpoint_returns_ok_json(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {'ok': True, 'service': 'django', 'component': 'headless-api'},
        )

    def test_delivery_endpoint_is_available_without_token_by_default(self):
        response = self.client.get('/api/delivery')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload.get('ok'))
        self.assertEqual(payload.get('endpoint'), 'delivery_index')
