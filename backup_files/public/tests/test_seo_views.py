from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase, override_settings

from public.views import seo


class SeoViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(APP_BASE_URL='', ROBOTS_DISALLOW_ALL=False, SEO_CACHE_VERSION='test-a')
    def test_robots_txt_allows_public_and_declares_sitemap(self):
        request = self.factory.get('/robots.txt', HTTP_HOST='example.com')

        response = seo.robots_txt(request)
        body = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Allow: /', body)
        self.assertIn('Disallow: /admin/', body)
        self.assertIn('Disallow: /api/', body)
        self.assertIn('Sitemap: http://example.com/sitemap.xml', body)

    @override_settings(APP_BASE_URL='https://prod.example.com', ROBOTS_DISALLOW_ALL=True, SEO_CACHE_VERSION='test-b')
    def test_robots_txt_can_disallow_all(self):
        request = self.factory.get('/robots.txt', HTTP_HOST='example.com')

        response = seo.robots_txt(request)
        body = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Disallow: /', body)
        self.assertIn('Sitemap: https://prod.example.com/sitemap.xml', body)
        self.assertEqual(response['X-Robots-Tag'], 'noindex, nofollow')

    @override_settings(APP_BASE_URL='https://prod.example.com', SEO_CACHE_VERSION='test-c')
    @patch('public.views.seo._cms_article_urls', return_value=[('https://prod.example.com/article/1', '2026-02-01')])
    @patch('public.views.seo._cms_page_urls', return_value=[('https://prod.example.com/page/test', '2026-02-01')])
    @patch('public.views.seo._post_urls', return_value=[('https://prod.example.com/blog/post', '2026-02-01')])
    @patch('public.views.seo._industry_urls', return_value=[('https://prod.example.com/industries/a', '2026-02-01')])
    @patch('public.views.seo._service_urls', return_value=[('https://prod.example.com/services/a', '2026-02-01')])
    @patch('public.views.seo._static_urls', return_value=[('https://prod.example.com/', '')])
    def test_sitemap_xml_contains_urls(
        self,
        _static_urls_mock,
        _service_urls_mock,
        _industry_urls_mock,
        _post_urls_mock,
        _cms_page_urls_mock,
        _cms_article_urls_mock,
    ):
        request = self.factory.get('/sitemap.xml', HTTP_HOST='example.com')

        response = seo.sitemap_xml(request)
        body = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertIn('<urlset', body)
        self.assertIn('<loc>https://prod.example.com/</loc>', body)
        self.assertIn('<loc>https://prod.example.com/services/a</loc>', body)
        self.assertIn('<loc>https://prod.example.com/blog/post</loc>', body)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
