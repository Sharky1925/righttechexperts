from pathlib import Path
from tempfile import TemporaryDirectory

from django.http import Http404
from django.test import RequestFactory, SimpleTestCase, override_settings

from admin_panel.views.media import uploaded_file


class MediaSecurityTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(MEDIA_ROOT='/tmp')
    def test_uploaded_file_blocks_path_traversal(self):
        request = self.factory.get('/admin/uploads/../secret.txt')
        with self.assertRaises(Http404):
            uploaded_file(request, '../secret.txt')

    def test_uploaded_file_returns_file_response_for_valid_file(self):
        with TemporaryDirectory() as tmp_dir:
            media_root = Path(tmp_dir)
            file_path = media_root / 'test.txt'
            file_path.write_text('hello-media', encoding='utf-8')

            with override_settings(MEDIA_ROOT=str(media_root)):
                request = self.factory.get('/admin/uploads/test.txt')
                response = uploaded_file(request, 'test.txt')
                body = b''.join(response.streaming_content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body, b'hello-media')
