<?php
/**
 * Security Middleware
 * Replaces core/middleware.py (CSPNonceMiddleware, SecurityHeadersMiddleware, etc.)
 */

function run_middleware(): void
{
    // Generate CSP nonce
    $GLOBALS['__csp_nonce'] = rtrim(strtr(base64_encode(random_bytes(16)), '+/', '-_'), '=');
    $nonce = $GLOBALS['__csp_nonce'];

    // Generate request ID
    $requestId = sprintf(
        '%04x%04x-%04x-%04x-%04x-%04x%04x%04x',
        mt_rand(0, 0xffff),
        mt_rand(0, 0xffff),
        mt_rand(0, 0xffff),
        mt_rand(0, 0x0fff) | 0x4000,
        mt_rand(0, 0x3fff) | 0x8000,
        mt_rand(0, 0xffff),
        mt_rand(0, 0xffff),
        mt_rand(0, 0xffff)
    );

    // Set response headers
    header("X-Request-ID: {$requestId}");
    header('X-Frame-Options: DENY');
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: strict-origin-when-cross-origin');
    header('Cross-Origin-Resource-Policy: same-origin');
    header('Cross-Origin-Opener-Policy: same-origin');
    header('X-Permitted-Cross-Domain-Policies: none');
    header('Origin-Agent-Cluster: ?1');
    header('Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()');

    // Content Security Policy
    $csp = "default-src 'self'; ";
    $csp .= "script-src 'self' 'nonce-{$nonce}' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.tiny.cloud https://challenges.cloudflare.com; ";
    $csp .= "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.tiny.cloud; ";
    $csp .= "img-src 'self' data: https:; ";
    $csp .= "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com; ";
    $csp .= "connect-src 'self' https://cdn.tiny.cloud https://challenges.cloudflare.com; ";
    $csp .= "frame-src 'self' https://challenges.cloudflare.com; ";
    $csp .= "frame-ancestors 'none'; base-uri 'self'; form-action 'self';";
    if (!APP_DEBUG) {
        $csp .= " upgrade-insecure-requests;";
    }
    header("Content-Security-Policy: {$csp}");
}
