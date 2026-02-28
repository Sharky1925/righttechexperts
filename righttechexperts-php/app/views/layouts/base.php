<?php
/**
 * Base Layout — converted from app/templates/base.html
 * Variables expected: $__page_content, $page_title, $meta_description, $meta_keywords, etc.
 */

$_title = $page_title ?? ($site_settings['meta_title'] ?? 'Right On Repair — IT Services & Computer Repair in Orange County');
$_meta_desc = $meta_description ?? ($site_settings['meta_description'] ?? '');
$_meta_kw = $meta_keywords ?? 'IT services Orange County, managed IT Orange County, cybersecurity Orange County, cloud solutions Orange County, computer repair Orange County, business IT support, software development Orange County, web development Orange County';
$_meta_robots = $meta_robots ?? 'index, follow';
$_og_title = $og_title ?? $_title;
$_og_desc = $og_description ?? $_meta_desc;
$_og_type = $og_type ?? 'website';
$_og_image = $og_image ?? public_url('/icon.png');
$_canonical = $canonical_url ?? public_url(strtok($_SERVER['REQUEST_URI'] ?? '/', '?'));
$_asset_version = $asset_v ?? 'dev';
$_nonce = csp_nonce();
$_phone_raw = preg_replace('/[\s()\-]/', '', $site_settings['phone'] ?? '');
$_phone = $site_settings['phone'] ?? '';

// Social links for structured data
$_social_links = array_filter([
    trim($site_settings['facebook'] ?? ''),
    trim($site_settings['twitter'] ?? ''),
    trim($site_settings['linkedin'] ?? ''),
]);

// Current endpoint detection
$_current_path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
$_current_path = rtrim($_current_path, '/') ?: '/';
?>
<!DOCTYPE html>
<html lang="en" data-bs-theme="<?= e($theme_mode ?? 'light') ?>" data-theme="<?= e($theme_mode ?? 'light') ?>">

<head>
    <script
        nonce="<?= e($_nonce) ?>">(function () { var root = document.documentElement; var t = ''; try { t = localStorage.getItem('theme') || '' } catch (e) { t = '' } if (t !== 'dark' && t !== 'light') { t = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light' } root.setAttribute('data-theme', t); root.setAttribute('data-bs-theme', t) })()</script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>
        <?= e($_title) ?>
    </title>
    <meta name="description" content="<?= e($_meta_desc) ?>">
    <meta name="author" content="<?= e($site_settings['company_name'] ?? 'Right On Repair') ?>">
    <meta name="keywords" content="<?= e($_meta_kw) ?>">
    <meta name="robots" content="<?= e($_meta_robots) ?>">
    <meta name="googlebot" content="index, follow, max-video-preview:-1, max-image-preview:large, max-snippet:-1">
    <meta name="format-detection" content="telephone=no, email=no">
    <link rel="canonical" href="<?= e($_canonical) ?>">
    <?= $head_meta_extra ?? '' ?>

    <!-- Open Graph -->
    <meta property="og:title" content="<?= e($_og_title) ?>">
    <meta property="og:description" content="<?= e($_og_desc) ?>">
    <meta property="og:type" content="<?= e($_og_type) ?>">
    <meta property="og:url" content="<?= e(public_url($_SERVER['REQUEST_URI'] ?? '/')) ?>">
    <meta property="og:site_name" content="<?= e($site_settings['company_name'] ?? 'Right On Repair') ?>">
    <meta property="og:locale" content="en_US">
    <meta property="og:image" content="<?= e($_og_image) ?>">
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="<?= e($_og_title) ?>">
    <meta name="twitter:description" content="<?= e($_og_desc) ?>">
    <meta name="twitter:image" content="<?= e(public_url('/icon.png')) ?>">

    <!-- Fonts & CSS -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
    <link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
    <link rel="dns-prefetch" href="//cdn.jsdelivr.net">
    <link rel="dns-prefetch" href="//cdnjs.cloudflare.com">
    <?php if (!empty($google_fonts_url)): ?>
        <link href="<?= e($google_fonts_url) ?>" rel="stylesheet">
    <?php else: ?>
        <link
            href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Orbitron:wght@600;700;800&family=Sora:wght@400;500;600;700;800&display=swap"
            rel="stylesheet">
    <?php endif; ?>
    <link rel="icon" type="image/svg+xml" href="/favicon.svg">
    <link rel="alternate icon" type="image/png" href="/icon.png">
    <link rel="shortcut icon" href="/favicon.svg">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet">
    <link href="/css/style.css?v=<?= e($_asset_version) ?>" rel="stylesheet">
    <?= $site_settings['custom_head_code'] ?? '' ?>
    <link rel="sitemap" type="application/xml" href="/sitemap.xml">
    <?= $head_extra ?? '' ?>

    <!-- Structured Data -->
    <script nonce="<?= e($_nonce) ?>" type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": <?= json_encode($site_settings['company_name'] ?? 'Right On Repair') ?>,
    "description": <?= json_encode($site_settings['meta_description'] ?? '') ?>,
    "url": <?= json_encode(public_url()) ?>,
    "image": <?= json_encode(public_url('/icon.png')) ?>,
    "telephone": <?= json_encode($site_settings['phone'] ?? '') ?>,
    "email": <?= json_encode($site_settings['email'] ?? '') ?>,
    "address": {
      "@type": "PostalAddress",
      "streetAddress": <?= json_encode($site_settings['address'] ?? '') ?>,
      "addressLocality": "Orange County",
      "addressRegion": "CA",
      "postalCode": <?= json_encode($site_settings['zip_code'] ?? '') ?>,
      "addressCountry": "US"
    },
    "geo": {
      "@type": "GeoCoordinates",
      "latitude": 33.7175,
      "longitude": -117.8311
    },
    "areaServed": {
      "@type": "AdministrativeArea",
      "name": "Orange County, CA"
    },
    "priceRange": "$$",
    "openingHoursSpecification": [
      { "@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "08:00", "closes": "18:00" },
      { "@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "09:00", "closes": "15:00" }
    ]<?php if (!empty($_social_links)): ?>,
        "sameAs": <?= json_encode(array_values($_social_links)) ?>
    <?php endif; ?>
  }
  </script>
    <?= $structured_data ?? '' ?>
</head>

<body>
    <a class="skip-link" href="#main-content">Skip to main content</a>
    <div class="scroll-progress"></div>
    <div class="ambient-orb ambient-orb--one" aria-hidden="true"></div>
    <div class="ambient-orb ambient-orb--two" aria-hidden="true"></div>
    <div class="ambient-grid" aria-hidden="true"></div>

    <header class="site-header sticky-top">
        <!-- Topbar — desktop only -->
        <div class="topbar d-none d-md-block">
            <div class="container">
                <div class="topbar-inner">
                    <div class="topbar-group">
                        <div class="topbar-item">
                            <span class="topbar-stars">
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <span>5-Star Rated</span>
                            </span>
                        </div>
                        <?php if (!empty($_phone)): ?>
                            <div class="topbar-item topbar-item-phone">
                                <a class="topbar-contact-link" href="tel:<?= e($_phone_raw) ?>"
                                    aria-label="Call <?= e($_phone) ?>">
                                    <i class="fa-solid fa-phone"></i>
                                    <?= e($_phone) ?>
                                </a>
                            </div>
                        <?php endif; ?>
                        <?php if (!empty($site_settings['email'])): ?>
                            <div class="topbar-item topbar-item-email">
                                <a class="topbar-contact-link" href="mailto:<?= e($site_settings['email']) ?>"
                                    aria-label="Email <?= e($site_settings['email']) ?>">
                                    <i class="fa-solid fa-envelope"></i>
                                    <?= e($site_settings['email']) ?>
                                </a>
                            </div>
                        <?php endif; ?>
                    </div>
                    <div class="topbar-group">
                        <?php if (!empty($site_settings['address'])): ?>
                            <div class="topbar-item topbar-item-address">
                                <i class="fa-solid fa-location-dot"></i>
                                <?= e($site_settings['address']) ?>
                            </div>
                        <?php endif; ?>
                        <form method="GET" action="<?= url_for('ticket_search') ?>" class="topbar-ticket-search"
                            role="search" aria-label="Ticket search">
                            <label class="visually-hidden" for="topbarTicketSearch">Search ticket number</label>
                            <input id="topbarTicketSearch" type="search" name="ticket_number" value=""
                                placeholder="Track Ticket #" maxlength="40" autocomplete="off">
                            <button type="submit" aria-label="Search ticket"><i
                                    class="fa-solid fa-magnifying-glass"></i></button>
                        </form>
                        <div class="topbar-item">
                            <a href="<?= url_for('request_quote') ?>">Free Consultation <i
                                    class="fa-solid fa-arrow-right topbar-arrow-icon"></i></a>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Navbar -->
        <nav class="navbar navbar-expand-lg navbar-main">
            <div class="container">
                <a class="navbar-brand brand-stack" href="<?= url_for('index') ?>"
                    aria-label="Right Tech Experts, Right On Repair">
                    <span class="brand-primary">Right Tech Experts</span>
                    <span class="brand-secondary">Right On Repair</span>
                </a>

                <!-- Desktop CTA buttons -->
                <div class="nav-cta-group d-none d-lg-flex">
                    <?php if (!empty($_phone)): ?>
                        <a class="btn btn-call btn-nav-call" href="tel:<?= e($_phone_raw) ?>"><i
                                class="fa-solid fa-phone"></i> Call Now</a>
                    <?php endif; ?>
                    <a class="btn btn-quote btn-nav-quote" href="<?= url_for('request_quote') ?>"><i
                            class="fa-solid fa-file-lines"></i> Request a Quote</a>
                    <a class="btn btn-remote-support btn-nav-remote" href="<?= url_for('remote_support') ?>"><i
                            class="fa-solid fa-life-ring"></i> Remote Support</a>
                    <a class="btn btn-danger btn-nav-cta" href="<?= url_for('contact') ?>?subject=Support+Message"><i
                            class="fa-solid fa-envelope"></i> Send Message</a>
                    <button type="button" class="theme-toggle" id="theme-toggle-desktop" aria-label="Toggle theme">
                        <i class="fa-solid fa-sun theme-icon-sun"></i>
                        <i class="fa-solid fa-moon theme-icon-moon"></i>
                    </button>
                </div>

                <!-- Mobile toggler -->
                <button class="navbar-toggler d-lg-none" type="button" aria-controls="navbarMainCollapse"
                    aria-expanded="false" aria-label="Toggle navigation" id="mobileMenuToggle">
                    <span class="toggler-bar"></span>
                    <span class="toggler-bar"></span>
                    <span class="toggler-bar"></span>
                </button>

                <!-- Nav links -->
                <div class="navbar-collapse collapse" id="navbarMainCollapse">
                    <ul class="navbar-nav align-items-lg-center gap-1">
                        <li class="nav-item"><a class="nav-link<?= $_current_path === '/' ? ' active' : '' ?>"
                                href="<?= url_for('index') ?>">Home</a></li>
                        <li class="nav-item"><a class="nav-link<?= $_current_path === '/about' ? ' active' : '' ?>"
                                href="<?= url_for('about') ?>">About</a></li>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle<?= str_starts_with($_current_path, '/services') ? ' active' : '' ?>"
                                href="<?= url_for('services') ?>" aria-expanded="false">IT Services</a>
                            <ul class="dropdown-menu">
                                <?php foreach ($nav_professional as $s): ?>
                                    <li><a class="dropdown-item"
                                            href="<?= url_for('service_detail', ['slug' => $s['slug']]) ?>"><i
                                                class="<?= e($s['icon_class']) ?> me-2 dropdown-item-icon"></i>
                                            <?= e($s['title']) ?>
                                        </a></li>
                                <?php endforeach; ?>
                                <li>
                                    <hr class="dropdown-divider">
                                </li>
                                <li><a class="dropdown-item" href="<?= url_for('services') ?>"><strong>View All
                                            Services</strong></a></li>
                            </ul>
                        </li>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="<?= url_for('services') ?>"
                                aria-expanded="false">Technical Repair Services</a>
                            <ul class="dropdown-menu">
                                <?php foreach ($nav_repair as $s): ?>
                                    <li><a class="dropdown-item"
                                            href="<?= url_for('service_detail', ['slug' => $s['slug']]) ?>"><i
                                                class="<?= e($s['icon_class']) ?> me-2 dropdown-item-icon"></i>
                                            <?= e($s['title']) ?>
                                        </a></li>
                                <?php endforeach; ?>
                                <li>
                                    <hr class="dropdown-divider">
                                </li>
                                <li><a class="dropdown-item" href="<?= url_for('services') ?>"><strong>View All
                                            Services</strong></a></li>
                            </ul>
                        </li>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle<?= str_starts_with($_current_path, '/industries') ? ' active' : '' ?>"
                                href="<?= url_for('industries') ?>" aria-expanded="false">Industries</a>
                            <ul class="dropdown-menu">
                                <?php foreach ($nav_industries as $ind): ?>
                                    <li><a class="dropdown-item"
                                            href="<?= url_for('industry_detail', ['slug' => $ind['slug']]) ?>"><i
                                                class="<?= e($ind['icon_class']) ?> me-2 dropdown-item-icon"></i>
                                            <?= e($ind['title']) ?>
                                        </a></li>
                                <?php endforeach; ?>
                                <li>
                                    <hr class="dropdown-divider">
                                </li>
                                <li><a class="dropdown-item" href="<?= url_for('industries') ?>"><strong>View All
                                            Industries</strong></a></li>
                            </ul>
                        </li>
                        <li class="nav-item d-lg-none"><a class="nav-link" href="<?= url_for('request_quote') ?>"><i
                                    class="fa-solid fa-file-invoice me-2"></i>Request Quote</a></li>
                        <!-- Mobile theme toggle -->
                        <li class="nav-item d-lg-none mt-2">
                            <button type="button" class="theme-toggle theme-toggle-mobile" id="theme-toggle-mobile"
                                aria-label="Toggle theme">
                                <i class="fa-solid fa-sun theme-icon-sun"></i>
                                <i class="fa-solid fa-moon theme-icon-moon"></i>
                                <span class="theme-toggle-label theme-label-dark">Light Mode</span>
                                <span class="theme-toggle-label theme-label-light">Dark Mode</span>
                            </button>
                        </li>
                        <!-- Mobile CTA buttons -->
                        <li class="nav-item d-lg-none mt-2">
                            <div class="mobile-nav-ctas">
                                <form method="GET" action="<?= url_for('ticket_search') ?>"
                                    class="ticket-track-form ticket-track-form-mobile" role="search"
                                    aria-label="Ticket search">
                                    <label class="visually-hidden" for="mobileTicketSearch">Search ticket number</label>
                                    <input id="mobileTicketSearch" type="search" name="ticket_number" value=""
                                        placeholder="Track Ticket #" maxlength="40" autocomplete="off">
                                    <button type="submit"><i
                                            class="fa-solid fa-magnifying-glass me-1"></i>Track</button>
                                </form>
                                <?php if (!empty($_phone)): ?>
                                    <a class="btn btn-call btn-nav-call" href="tel:<?= e($_phone_raw) ?>"><i
                                            class="fa-solid fa-phone"></i> Call Now</a>
                                <?php endif; ?>
                                <a class="btn btn-quote btn-nav-quote" href="<?= url_for('request_quote') ?>"><i
                                        class="fa-solid fa-file-lines"></i> Request a Quote</a>
                                <a class="btn btn-remote-support btn-nav-remote"
                                    href="<?= url_for('remote_support') ?>"><i class="fa-solid fa-life-ring"></i> Remote
                                    Support</a>
                                <a class="btn btn-danger btn-nav-cta"
                                    href="<?= url_for('contact') ?>?subject=Support+Message"><i
                                        class="fa-solid fa-envelope"></i> Send Message</a>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    </header>

    <!-- Flash Messages -->
    <?php $messages = get_flashed_messages(true); ?>
    <?php if (!empty($messages)): ?>
        <div class="container flash-wrap" aria-live="polite">
            <?php foreach ($messages as $msg): ?>
                <div class="alert alert-modern alert-<?= e($msg['category']) ?> alert-dismissible fade show" role="alert">
                    <i class="fa-solid <?= $msg['category'] === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation' ?>"></i>
                    <?= e($msg['message']) ?>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>

    <!-- Main Content -->
    <main id="main-content">
        <?= $__page_content ?? '' ?>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="row g-5">
                <div class="col-lg-4">
                    <div class="brand-text brand-stack-footer" aria-label="Right Tech Experts, Right On Repair">
                        <span class="brand-primary">Right Tech Experts</span>
                        <span class="brand-secondary">Right On Repair</span>
                    </div>
                    <p>
                        <?= e($site_settings['tagline'] ?? 'Managed IT, cybersecurity, cloud architecture, software development, and technical repairs for local businesses.') ?>
                    </p>
                    <?php if (!empty($_phone) || !empty($site_settings['email']) || !empty($site_settings['address'])): ?>
                        <ul class="footer-contact-list">
                            <?php if (!empty($_phone)): ?>
                                <li class="footer-contact-item"><i class="fa-solid fa-phone me-2 footer-contact-icon"></i>
                                    <?= e($_phone) ?>
                                </li>
                            <?php endif; ?>
                            <?php if (!empty($site_settings['email'])): ?>
                                <li class="footer-contact-item"><i class="fa-solid fa-envelope me-2 footer-contact-icon"></i>
                                    <?= e($site_settings['email']) ?>
                                </li>
                            <?php endif; ?>
                            <?php if (!empty($site_settings['address'])): ?>
                                <li><i class="fa-solid fa-location-dot me-2 footer-contact-icon"></i>
                                    <?= e($site_settings['address']) ?>
                                </li>
                            <?php endif; ?>
                        </ul>
                    <?php endif; ?>
                    <div class="footer-social">
                        <?php if (!empty($site_settings['facebook'])): ?><a href="<?= e($site_settings['facebook']) ?>"
                                target="_blank" rel="noopener noreferrer" aria-label="Facebook"><i
                                    class="fa-brands fa-facebook-f"></i></a>
                        <?php endif; ?>
                        <?php if (!empty($site_settings['twitter'])): ?><a href="<?= e($site_settings['twitter']) ?>"
                                target="_blank" rel="noopener noreferrer" aria-label="Twitter"><i
                                    class="fa-brands fa-x-twitter"></i></a>
                        <?php endif; ?>
                        <?php if (!empty($site_settings['linkedin'])): ?><a href="<?= e($site_settings['linkedin']) ?>"
                                target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><i
                                    class="fa-brands fa-linkedin-in"></i></a>
                        <?php endif; ?>
                    </div>
                </div>
                <div class="col-6 col-lg-2">
                    <h5>Services</h5>
                    <ul>
                        <?php foreach (array_slice($nav_professional, 0, 5) as $s): ?>
                            <li><a href="<?= url_for('service_detail', ['slug' => $s['slug']]) ?>">
                                    <?= e($s['title']) ?>
                                </a></li>
                        <?php endforeach; ?>
                    </ul>
                </div>
                <div class="col-6 col-lg-2">
                    <h5>Company</h5>
                    <ul>
                        <li><a href="<?= url_for('about') ?>">About Us</a></li>
                        <li><a href="<?= url_for('services') ?>">All Services</a></li>
                        <li><a href="<?= url_for('industries') ?>">Industries</a></li>
                        <li><a href="<?= url_for('contact') ?>">Contact</a></li>
                        <li><a href="<?= url_for('request_quote') ?>">Request Quote</a></li>
                    </ul>
                </div>
                <div class="col-lg-4">
                    <h5>Service Area</h5>
                    <p class="footer-service-note">
                        <?= e($footer_content['service_area']['description'] ?? 'On-site and remote support for businesses throughout Orange County.') ?>
                    </p>
                    <div class="footer-chips">
                        <?php
                        $cities = $footer_content['service_area']['cities'] ?? ORANGE_COUNTY_CA_CITIES;
                        foreach ($cities as $city): ?>
                            <span class="footer-chip">
                                <?= e($city) ?>
                            </span>
                        <?php endforeach; ?>
                    </div>
                </div>
            </div>
            <div class="footer-bottom d-flex flex-wrap justify-content-between align-items-center">
                <span>
                    <?= str_replace('&copy;', '©', $site_settings['footer_text'] ?? '© 2024 Right On Repair. All rights reserved.') ?>
                </span>
                <span><a href="/admin/login" class="footer-admin-link" rel="nofollow">Admin</a></span>
            </div>
        </div>
    </footer>

    <!-- Mobile Call Button -->
    <?php if (!empty($_phone)): ?>
        <a class="mobile-call" href="tel:<?= e($_phone_raw) ?>">
            <i class="fa-solid fa-phone"></i> Call Now
        </a>
    <?php endif; ?>

    <?= $site_settings['custom_footer_code'] ?? '' ?>
    <script nonce="<?= e($_nonce) ?>"
        src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script nonce="<?= e($_nonce) ?>" src="/js/main.js?v=<?= e($_asset_version) ?>"></script>
    <script nonce="<?= e($_nonce) ?>">
            (function () {
                function sysPref() { return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light' }
                function getTheme() { return document.documentElement.getAttribute('data-theme') || sysPref() }
                function setTheme(t) {
                    document.documentElement.setAttribute('data-theme', t);
                    document.documentElement.setAttribute('data-bs-theme', t);
                    try { localStorage.setItem('theme', t) } catch (e) { }
                }
                function toggle() { setTheme(getTheme() === 'dark' ? 'light' : 'dark') }
                function bind() {
                    var btns = document.querySelectorAll('.theme-toggle');
                    for (var i = 0; i < btns.length; i++) { btns[i].addEventListener('click', toggle) }
                }
                if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', bind) } else { bind() }
            })();
    </script>
    <?= $page_scripts ?? '' ?>
</body>

</html>