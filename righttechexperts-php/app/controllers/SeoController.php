<?php
/**
 * SEO Controller
 * Converts public/views/seo.py — sitemap.xml and robots.txt
 */

class SeoController
{
    public static function sitemap_xml(): void
    {
        header('Content-Type: application/xml; charset=utf-8');

        $base = public_url();
        $now = gmdate('Y-m-d');

        $urls = [
            ['loc' => '/', 'changefreq' => 'weekly', 'priority' => '1.0'],
            ['loc' => '/about', 'changefreq' => 'monthly', 'priority' => '0.8'],
            ['loc' => '/services', 'changefreq' => 'weekly', 'priority' => '0.9'],
            ['loc' => '/industries', 'changefreq' => 'weekly', 'priority' => '0.8'],
            ['loc' => '/blog', 'changefreq' => 'weekly', 'priority' => '0.7'],
            ['loc' => '/contact', 'changefreq' => 'monthly', 'priority' => '0.7'],
            ['loc' => '/request-quote', 'changefreq' => 'monthly', 'priority' => '0.7'],
            ['loc' => '/remote-support', 'changefreq' => 'monthly', 'priority' => '0.6'],
        ];

        // Services
        try {
            $services = db_query("SELECT slug FROM service WHERE " . published_clause());
            foreach ($services as $s) {
                $urls[] = ['loc' => '/services/' . $s['slug'], 'changefreq' => 'monthly', 'priority' => '0.8'];
            }
        } catch (Exception $e) {
        }

        // Industries
        try {
            $industries = db_query("SELECT slug FROM industry WHERE " . published_clause());
            foreach ($industries as $i) {
                $urls[] = ['loc' => '/industries/' . $i['slug'], 'changefreq' => 'monthly', 'priority' => '0.7'];
            }
        } catch (Exception $e) {
        }

        // Blog posts
        try {
            $posts = db_query("SELECT slug FROM post WHERE " . published_clause() . " ORDER BY created_at DESC LIMIT 100");
            foreach ($posts as $p) {
                $urls[] = ['loc' => '/blog/' . $p['slug'], 'changefreq' => 'monthly', 'priority' => '0.6'];
            }
        } catch (Exception $e) {
        }

        echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
        echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
        foreach ($urls as $url) {
            echo "  <url>\n";
            echo "    <loc>" . htmlspecialchars($base . $url['loc']) . "</loc>\n";
            echo "    <lastmod>{$now}</lastmod>\n";
            echo "    <changefreq>{$url['changefreq']}</changefreq>\n";
            echo "    <priority>{$url['priority']}</priority>\n";
            echo "  </url>\n";
        }
        echo "</urlset>\n";
    }

    public static function robots_txt(): void
    {
        header('Content-Type: text/plain; charset=utf-8');
        $base = public_url();
        echo "User-agent: *\n";
        echo "Allow: /\n";
        echo "\n";
        echo "Sitemap: {$base}/sitemap.xml\n";
    }
}
