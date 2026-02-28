<?php
/**
 * Application Configuration
 * Replaces Django settings (config/settings/base.py + dev.py)
 */

// ─── Environment ────────────────────────────────────────────────────────
define('APP_DEBUG', (bool) ($_ENV['APP_DEBUG'] ?? true));
define('APP_BASE_URL', rtrim($_ENV['APP_BASE_URL'] ?? '', '/'));
define('SECRET_KEY', $_ENV['SECRET_KEY'] ?? 'dev-only-key-change-me');

// ─── Paths ──────────────────────────────────────────────────────────────
define('BASE_DIR', dirname(__DIR__));
define('APP_DIR', __DIR__);
define('PUBLIC_DIR', BASE_DIR . '/public');
define('VIEWS_DIR', APP_DIR . '/views');

// ─── Database ───────────────────────────────────────────────────────────
// Priority: DATABASE_URL (Postgres) > SQLITE_PATH > legacy Flask DB > fallback
$database_url  = trim($_ENV['DATABASE_URL'] ?? '');
$sqlite_path   = trim($_ENV['SQLITE_PATH'] ?? $_ENV['LEGACY_SQLITE_PATH'] ?? '');
$legacy_default = '/Users/umutdemirkapu/mylauncher/app/site.db';

if ($database_url) {
    // PostgreSQL via DATABASE_URL
    $parsed = parse_url(str_replace('postgres://', 'postgresql://', $database_url));
    define('DB_DRIVER', 'pgsql');
    define('DB_DSN', sprintf(
        'pgsql:host=%s;port=%s;dbname=%s',
        $parsed['host'] ?? 'localhost',
        $parsed['port'] ?? 5432,
        ltrim($parsed['path'] ?? '', '/')
    ));
    define('DB_USER', $parsed['user'] ?? '');
    define('DB_PASS', $parsed['pass'] ?? '');
} else {
    // SQLite
    $db_file = $sqlite_path ?: (file_exists($legacy_default) ? $legacy_default : BASE_DIR . '/db.sqlite3');
    define('DB_DRIVER', 'sqlite');
    define('DB_DSN', 'sqlite:' . $db_file);
    define('DB_USER', null);
    define('DB_PASS', null);
}

// ─── Site Defaults ──────────────────────────────────────────────────────
define('DEFAULT_SITE_SETTINGS', [
    'company_name'     => 'Right On Repair',
    'tagline'          => 'Orange County managed IT, cybersecurity, cloud, software, web, and technical repair services',
    'phone'            => '+1 (562) 542-5899',
    'email'            => 'info@rightonrepair.com',
    'address'          => '9092 Talbert Ave. Ste 4, Fountain Valley, CA 92708',
    'facebook'         => 'https://facebook.com',
    'twitter'          => 'https://twitter.com',
    'linkedin'         => 'https://linkedin.com',
    'meta_title'       => 'Right On Repair — Orange County IT Services & Computer Repair',
    'meta_description' => 'Orange County IT services and technical repair: managed IT, cybersecurity, cloud migration, software and web development, surveillance setup, and same-day device repair support for local businesses.',
    'theme_mode'       => 'light',
]);

// ─── Constants ──────────────────────────────────────────────────────────
define('WORKFLOW_PUBLISHED', 'published');

define('ORANGE_COUNTY_CA_CITIES', [
    'Aliso Viejo','Anaheim','Brea','Buena Park','Costa Mesa','Cypress',
    'Dana Point','Fountain Valley','Fullerton','Garden Grove','Huntington Beach',
    'Irvine','La Habra','La Palma','Laguna Beach','Laguna Hills','Laguna Niguel',
    'Laguna Woods','Lake Forest','Los Alamitos','Mission Viejo','Newport Beach',
    'Orange','Placentia','Rancho Santa Margarita','San Clemente',
    'San Juan Capistrano','Santa Ana','Seal Beach','Stanton','Tustin',
    'Villa Park','Westminster','Yorba Linda',
]);

// ─── Session ────────────────────────────────────────────────────────────
ini_set('session.cookie_httponly', '1');
ini_set('session.cookie_samesite', 'Lax');
ini_set('session.gc_maxlifetime', '28800');
session_start();
