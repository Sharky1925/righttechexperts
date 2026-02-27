from django.urls import path

from public.views import contact, pages, seo, support

app_name = 'public'

urlpatterns = [
    path('', pages.index, name='index'),
    path('about', pages.about, name='about'),
    path('services', pages.services, name='services'),
    path('services/it-services', pages.services_it_track, name='services_it_track'),
    path('services/repair-services', pages.services_repair_track, name='services_repair_track'),
    path('services/<slug:slug>', pages.service_detail, name='service_detail'),
    path('blog', pages.blog, name='blog'),
    path('blog/<slug:slug>', pages.post, name='post'),
    path('contact', contact.contact, name='contact'),
    path('request-quote', contact.request_quote, name='request_quote'),
    path('request-quote/personal', contact.request_quote_personal, name='request_quote_personal'),
    path('remote-support', support.remote_support, name='remote_support'),
    path('ticket-search', support.ticket_search, name='ticket_search'),
    path('page/<slug:slug>', pages.cms_page, name='cms_page'),
    path('article/<int:article_id>', pages.cms_article, name='cms_article'),
    path('industries', pages.industries, name='industries'),
    path('industries/<slug:slug>', pages.industry_detail, name='industry_detail'),
    path('sitemap.xml', seo.sitemap_xml, name='sitemap_xml'),
    path('robots.txt', seo.robots_txt, name='robots_txt'),
]
