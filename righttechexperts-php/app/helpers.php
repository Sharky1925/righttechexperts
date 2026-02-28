<?php
/**
 * Template Helper Functions
 * Replaces Jinja2 globals (config/jinja2_env.py) and context_processors
 */

// ─── Escaping ───────────────────────────────────────────────────────────

function e(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

// ─── URL Helpers ────────────────────────────────────────────────────────

/** Route name → path map (mirrors public/urls.py) */
function url_for(string $name, array $params = []): string
{
    static $routes = [
    'index' => '/',
    'about' => '/about',
    'services' => '/services',
    'services_it_track' => '/services/it-services',
    'services_repair_track' => '/services/repair-services',
    'service_detail' => '/services/{slug}',
    'blog' => '/blog',
    'post' => '/blog/{slug}',
    'contact' => '/contact',
    'request_quote' => '/request-quote',
    'request_quote_personal' => '/request-quote/personal',
    'remote_support' => '/remote-support',
    'ticket_search' => '/ticket-search',
    'cms_page' => '/page/{slug}',
    'cms_article' => '/article/{article_id}',
    'industries' => '/industries',
    'industry_detail' => '/industries/{slug}',
    'sitemap_xml' => '/sitemap.xml',
    'robots_txt' => '/robots.txt',
    // Legacy Flask-style names from Jinja2 templates
    'main.index' => '/',
    'main.about' => '/about',
    'main.services' => '/services',
    'main.blog' => '/blog',
    'main.contact' => '/contact',
    'main.request_quote' => '/request-quote',
    'main.request_quote_personal' => '/request-quote/personal',
    'main.remote_support' => '/remote-support',
    'main.industries' => '/industries',
    'main.sitemap_xml' => '/sitemap.xml',
    'main.robots_txt' => '/robots.txt',
    ];

    $path = $routes[$name] ?? '#';
    foreach ($params as $key => $val) {
        $path = str_replace('{' . $key . '}', rawurlencode($val), $path);
    }
    return $path;
}

function static_url(string $filename): string
{
    $v = $GLOBALS['__asset_v'] ?? '';
    $qs = $v ? "?v={$v}" : '';
    return '/' . ltrim($filename, '/') . $qs;
}

function public_url(string $path = ''): string
{
    $base = APP_BASE_URL;
    if (!$base) {
        $scheme = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https' : 'http';
        $host = $_SERVER['HTTP_HOST'] ?? 'localhost';
        $base = "{$scheme}://{$host}";
    }
    if (!$path)
        return $base;
    if (str_starts_with($path, 'http://') || str_starts_with($path, 'https://'))
        return $path;
    if (!str_starts_with($path, '/'))
        $path = '/' . $path;
    return $base . $path;
}

// ─── CSRF ───────────────────────────────────────────────────────────────

function csrf_token(): string
{
    if (empty($_SESSION['_csrf_token'])) {
        $_SESSION['_csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['_csrf_token'];
}

function csrf_input(): string
{
    $token = csrf_token();
    return '<input type="hidden" name="_csrf_token" value="' . e($token) . '">';
}

function verify_csrf(): bool
{
    $submitted = $_POST['_csrf_token'] ?? '';
    return hash_equals(csrf_token(), $submitted);
}

// ─── Flash Messages ─────────────────────────────────────────────────────

function flash(string $message, string $category = 'info'): void
{
    $_SESSION['_flash'][] = ['category' => $category, 'message' => $message];
}

function get_flashed_messages(bool $with_categories = false): array
{
    $messages = $_SESSION['_flash'] ?? [];
    unset($_SESSION['_flash']);
    if ($with_categories)
        return $messages;
    return array_column($messages, 'message');
}

// ─── CSP Nonce ──────────────────────────────────────────────────────────

function csp_nonce(): string
{
    return $GLOBALS['__csp_nonce'] ?? '';
}

// ─── Icon normalization ─────────────────────────────────────────────────

function normalize_icon_class(string $icon_class, string $fallback = 'fa-solid fa-circle'): string
{
    static $aliases = [
    'fa-ranking-star' => 'fa-chart-line',
    'fa-filter-circle-dollar' => 'fa-bullseye',
    'fa-radar' => 'fa-crosshairs',
    'fa-siren-on' => 'fa-bell',
    'fa-shield-check' => 'fa-shield-halved',
    ];
    static $validStyles = ['fa-solid', 'fa-regular', 'fa-brands'];

    $raw = trim($icon_class);
    if ($raw === '')
        return $fallback;

    $parts = preg_split('/\s+/', $raw);
    if (count($parts) === 1 && str_starts_with($parts[0], 'fa-')) {
        $style = 'fa-solid';
        $glyph = $parts[0];
    } else {
        $style = $parts[0] ?? 'fa-solid';
        $glyph = $parts[1] ?? '';
    }

    if (!in_array($style, $validStyles))
        $style = 'fa-solid';
    $glyph = $aliases[$glyph] ?? $glyph;

    $normalized = trim("{$style} {$glyph}");
    if (!preg_match('/^fa-(solid|regular|brands)\s+fa-[a-z0-9-]+$/', $normalized)) {
        return $fallback;
    }
    return $normalized;
}

function normalize_icon_items(array $items, string $fallback): array
{
    foreach ($items as &$item) {
        $item['icon_class'] = normalize_icon_class($item['icon_class'] ?? '', $fallback);
    }
    return $items;
}

// ─── Template Rendering ─────────────────────────────────────────────────

function render(string $template, array $data = []): string
{
    // Global context available in all templates
    $settings = get_site_settings();
    $theme_mode = strtolower(trim($settings['theme_mode'] ?? 'light'));
    if (!in_array($theme_mode, ['dark', 'light']))
        $theme_mode = 'light';

    $nav_professional = normalize_icon_items(get_nav_services('professional'), 'fa-solid fa-gear');
    $nav_repair = get_nav_services('repair');
    // Inject virtual laptop-repair if missing
    $hasLaptop = false;
    foreach ($nav_repair as $item) {
        if ($item['slug'] === 'laptop-repair') {
            $hasLaptop = true;
            break;
        }
    }
    if (!$hasLaptop) {
        $nav_repair[] = [
            'id' => -9001,
            'slug' => 'laptop-repair',
            'title' => 'Laptop Repair',
            'description' => 'Screen, battery, charging-port, and thermal repair workflows.',
            'icon_class' => 'fa-solid fa-laptop-medical',
        ];
    }
    $nav_repair = normalize_icon_items($nav_repair, 'fa-solid fa-wrench');
    $nav_industries = normalize_icon_items(get_nav_industries(), 'fa-solid fa-building');

    $footer_content = get_page_content('footer');
    $service_area = $footer_content['service_area'] ?? [];
    $service_area['cities'] = ORANGE_COUNTY_CA_CITIES;
    $footer_content['service_area'] = $service_area;

    $globals = [
        'site_settings' => $settings,
        'csp_nonce' => csp_nonce(),
        'asset_v' => $settings['asset_version'] ?? '',
        'public_base_url' => public_url(),
        'nav_professional' => $nav_professional,
        'nav_repair' => $nav_repair,
        'nav_industries' => $nav_industries,
        'footer_content' => $footer_content,
        'theme_mode' => $theme_mode,
        'orange_county_cities' => ORANGE_COUNTY_CA_CITIES,
        'google_fonts_url' => trim($settings['google_fonts_url'] ?? ''),
        'request_path' => $_SERVER['REQUEST_URI'] ?? '/',
    ];

    $GLOBALS['__asset_v'] = $globals['asset_v'];

    // Merge template-specific data over globals
    $vars = array_merge($globals, $data);

    // Render template into $content
    extract($vars);
    ob_start();
    require VIEWS_DIR . '/' . $template . '.php';
    $content = ob_get_clean();

    return $content;
}

function render_page(string $template, array $data = []): void
{
    echo render($template, $data);
}

function render_with_layout(string $template, array $data = []): void
{
    // Render the child template first to capture $content
    $settings = get_site_settings();
    $theme_mode = strtolower(trim($settings['theme_mode'] ?? 'light'));
    if (!in_array($theme_mode, ['dark', 'light']))
        $theme_mode = 'light';

    $nav_professional = normalize_icon_items(get_nav_services('professional'), 'fa-solid fa-gear');
    $nav_repair = get_nav_services('repair');
    $hasLaptop = false;
    foreach ($nav_repair as $item) {
        if ($item['slug'] === 'laptop-repair') {
            $hasLaptop = true;
            break;
        }
    }
    if (!$hasLaptop) {
        $nav_repair[] = [
            'id' => -9001,
            'slug' => 'laptop-repair',
            'title' => 'Laptop Repair',
            'description' => 'Screen, battery, charging-port, and thermal repair workflows.',
            'icon_class' => 'fa-solid fa-laptop-medical',
        ];
    }
    $nav_repair = normalize_icon_items($nav_repair, 'fa-solid fa-wrench');
    $nav_industries = normalize_icon_items(get_nav_industries(), 'fa-solid fa-building');

    $footer_content = get_page_content('footer');
    $service_area = $footer_content['service_area'] ?? [];
    $service_area['cities'] = ORANGE_COUNTY_CA_CITIES;
    $footer_content['service_area'] = $service_area;

    $globals = [
        'site_settings' => $settings,
        'csp_nonce' => csp_nonce(),
        'asset_v' => $settings['asset_version'] ?? '',
        'public_base_url' => public_url(),
        'nav_professional' => $nav_professional,
        'nav_repair' => $nav_repair,
        'nav_industries' => $nav_industries,
        'footer_content' => $footer_content,
        'theme_mode' => $theme_mode,
        'orange_county_cities' => ORANGE_COUNTY_CA_CITIES,
        'google_fonts_url' => trim($settings['google_fonts_url'] ?? ''),
        'request_path' => $_SERVER['REQUEST_URI'] ?? '/',
    ];
    $GLOBALS['__asset_v'] = $globals['asset_v'];

    $vars = array_merge($globals, $data);
    extract($vars);

    // Render child template
    ob_start();
    require VIEWS_DIR . '/' . $template . '.php';
    $__page_content = ob_get_clean();

    // Render layout with $__page_content available
    $vars['__page_content'] = $__page_content;
    extract($vars);
    require VIEWS_DIR . '/layouts/base.php';
}

// ─── JSON safe parsing ──────────────────────────────────────────────────

function safe_json_dict($raw): array
{
    if (is_array($raw))
        return $raw;
    if (!is_string($raw) || trim($raw) === '')
        return [];
    $decoded = json_decode($raw, true);
    return is_array($decoded) ? $decoded : [];
}

function safe_str_list($value): array
{
    if (is_array($value)) {
        return array_filter($value, 'is_string');
    }
    if (is_string($value)) {
        $decoded = json_decode($value, true);
        if (is_array($decoded))
            return array_filter($decoded, 'is_string');
    }
    return [];
}

function compact_excerpt(string $value, int $limit = 260): string
{
    $clean = trim(strip_tags($value));
    if (mb_strlen($clean) <= $limit)
        return $clean;
    return mb_substr($clean, 0, $limit) . '…';
}
