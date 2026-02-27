from unittest.mock import patch

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, SimpleTestCase

from public.views import contact


def _attach_session_and_messages(request):
    session_middleware = SessionMiddleware(lambda req: None)
    session_middleware.process_request(request)
    request.session.save()
    request._messages = FallbackStorage(request)
    return request


class ContactFlowTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('public.views.contact._create_submission', return_value=True)
    def test_contact_post_redirects_on_success(self, create_submission_mock):
        request = self.factory.post(
            '/contact',
            {
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '+15555550000',
                'subject': 'Need help',
                'message': 'Please contact me about managed services.',
            },
        )
        _attach_session_and_messages(request)

        response = contact.contact(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/contact')
        create_submission_mock.assert_called_once()

    @patch('public.views.contact._create_submission', return_value=True)
    def test_business_quote_post_redirects_on_success(self, create_submission_mock):
        request = self.factory.post(
            '/request-quote',
            {
                'full_name': 'Business Owner',
                'email': 'owner@example.com',
                'phone': '+15555550001',
                'company': 'Example Co',
                'primary_service_slug': 'managed-it-services',
                'preferred_contact': 'email',
                'business_goals': 'Reduce downtime and improve SLA outcomes.',
                'pain_points': 'Reactive support model and repeated incidents.',
            },
        )
        _attach_session_and_messages(request)

        response = contact.request_quote(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/request-quote')
        create_submission_mock.assert_called_once()

    @patch('public.views.contact._create_submission', return_value=True)
    def test_personal_quote_post_redirects_on_success(self, create_submission_mock):
        request = self.factory.post(
            '/request-quote/personal',
            {
                'full_name': 'Home User',
                'email': 'home@example.com',
                'phone': '+15555550002',
                'service_slug': 'computer-repair',
                'preferred_contact': 'phone',
                'issue_description': 'Laptop overheats and shuts down under load.',
            },
        )
        _attach_session_and_messages(request)

        response = contact.request_quote_personal(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/request-quote/personal')
        create_submission_mock.assert_called_once()
