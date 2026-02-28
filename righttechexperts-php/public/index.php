<?php
/**
 * Front Controller
 * All requests are routed through this file via .htaccess
 */

// Bootstrap
require_once __DIR__ . '/../app/config.php';
require_once __DIR__ . '/../app/database.php';
require_once __DIR__ . '/../app/helpers.php';
require_once __DIR__ . '/../app/middleware.php';
require_once __DIR__ . '/../app/router.php';

// Run security middleware
run_middleware();

// Dispatch request
$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

route($method, $path);
