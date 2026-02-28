<?php
/**
 * URL Router
 * Replaces Django urlpatterns (public/urls.py, config/urls.py)
 */

function route(string $method, string $path): void
{
    // Normalize path
    $path = '/' . trim($path, '/');
    if ($path !== '/' && str_ends_with($path, '/')) {
        $path = rtrim($path, '/');
    }

    // Static files — let the web server handle them
    if (preg_match('#^/(css|js|favicon\.svg|icon\.png)#', $path)) {
        return;
    }

    // ─── Routes ─────────────────────────────────────────────────────
    $routes = [
        'GET' => [],
        'POST' => [],
    ];

    // Public pages
    $routes['GET']['/'] = ['PagesController', 'index'];
    $routes['GET']['/about'] = ['PagesController', 'about'];
    $routes['GET']['/services'] = ['PagesController', 'services'];
    $routes['GET']['/services/it-services'] = ['PagesController', 'services_it_track'];
    $routes['GET']['/services/repair-services'] = ['PagesController', 'services_repair_track'];
    $routes['GET']['/blog'] = ['PagesController', 'blog'];
    $routes['GET']['/contact'] = ['PagesController', 'contact'];
    $routes['GET']['/request-quote'] = ['PagesController', 'request_quote'];
    $routes['GET']['/request-quote/personal'] = ['PagesController', 'request_quote_personal'];
    $routes['GET']['/remote-support'] = ['PagesController', 'remote_support'];
    $routes['GET']['/ticket-search'] = ['PagesController', 'ticket_search'];
    $routes['GET']['/industries'] = ['PagesController', 'industries'];
    $routes['GET']['/sitemap.xml'] = ['SeoController', 'sitemap_xml'];
    $routes['GET']['/robots.txt'] = ['SeoController', 'robots_txt'];

    // POST routes
    $routes['POST']['/contact'] = ['ContactController', 'contact_submit'];
    $routes['POST']['/request-quote'] = ['ContactController', 'request_quote_submit'];
    $routes['POST']['/request-quote/personal'] = ['ContactController', 'request_quote_personal_submit'];
    $routes['POST']['/remote-support'] = ['SupportController', 'remote_support_submit'];

    // ─── Exact match ────────────────────────────────────────────────
    if (isset($routes[$method][$path])) {
        [$controller, $action] = $routes[$method][$path];
        require_once APP_DIR . '/controllers/' . $controller . '.php';
        call_user_func($controller . '::' . $action);
        return;
    }

    // ─── Dynamic slug routes ────────────────────────────────────────
    $dynamicRoutes = [
        '#^/services/([a-z0-9-]+)$#' => ['PagesController', 'service_detail', 'slug'],
        '#^/blog/([a-z0-9-]+)$#' => ['PagesController', 'post', 'slug'],
        '#^/page/([a-z0-9-]+)$#' => ['PagesController', 'cms_page', 'slug'],
        '#^/article/(\d+)$#' => ['PagesController', 'cms_article', 'article_id'],
        '#^/industries/([a-z0-9-]+)$#' => ['PagesController', 'industry_detail', 'slug'],
    ];

    if ($method === 'GET') {
        foreach ($dynamicRoutes as $pattern => [$controller, $action, $paramName]) {
            if (preg_match($pattern, $path, $matches)) {
                require_once APP_DIR . '/controllers/' . $controller . '.php';
                call_user_func($controller . '::' . $action, $matches[1]);
                return;
            }
        }
    }

    // ─── 404 ────────────────────────────────────────────────────────
    http_response_code(404);
    require_once APP_DIR . '/controllers/PagesController.php';
    PagesController::not_found();
}
