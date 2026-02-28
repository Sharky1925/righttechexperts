<?php
/**
 * Industry Detail page — FULL PARITY with 294-line Django template
 * Sections: hero with stats, breadcrumbs, challenges with descriptions,
 * solutions with descriptions, related services, other industries, CTA
 */
$_nonce = csp_nonce();
$_phone_raw = preg_replace('/[\s()\-]/', '', $site_settings['phone'] ?? '');
$seo_desc = $seo_description ?? ($hero_description ?: ($industry['description'] ?? ''));
$seo_kw = $seo_keywords ?? ($industry['title'] . ' IT support, ' . $industry['title'] . ' cybersecurity, industry IT services Orange County, Right On Repair');
$page_title = $industry['title'] . ' IT Solutions — ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = $seo_desc;
$meta_keywords = $seo_kw;

$stat_items = !empty($industry['stats']) ? array_filter(explode('|', $industry['stats'])) : [];
$challenge_items = !empty($industry['challenges']) ? array_filter(explode('|', $industry['challenges'])) : [];
$solution_items = !empty($industry['solutions']) ? array_filter(explode('|', $industry['solutions'])) : [];
$challenge_descs = $challenge_descriptions ?? [];
$solution_descs = $solution_descriptions ?? [];

$challenge_icons = ['fa-solid fa-lock', 'fa-solid fa-plug', 'fa-solid fa-clock', 'fa-solid fa-expand', 'fa-solid fa-bug'];
$challenge_colors = ['blue', 'purple', 'amber', 'green', 'rose'];
$sol_icons = ['fa-solid fa-shield-halved', 'fa-solid fa-link', 'fa-solid fa-server', 'fa-solid fa-cloud', 'fa-solid fa-chart-line'];
$stat_icons = ['fa-solid fa-chart-line', 'fa-solid fa-shield-halved', 'fa-solid fa-bolt', 'fa-solid fa-check-double'];
$colors6 = ['blue', 'purple', 'green', 'amber', 'rose', 'cyan'];

// Structured Data
$structured_data = '<script nonce="' . e($_nonce) . '" type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": ' . json_encode($industry['title'] . ' IT Solutions') . ',
  "description": ' . json_encode($seo_desc) . ',
  "provider": {
    "@type": "Organization",
    "name": ' . json_encode($site_settings['company_name'] ?? 'Right On Repair') . ',
    "telephone": ' . json_encode($site_settings['phone'] ?? '') . ',
    "address": {"@type":"PostalAddress","addressLocality":"Fountain Valley","addressRegion":"CA","postalCode":"92708","addressCountry":"US"}
  },
  "areaServed": {"@type":"City","name":"Orange County","containedInPlace":{"@type":"State","name":"California"}},
  "serviceType": ' . json_encode('IT Solutions for ' . $industry['title']) . '
}
</script>';

// BreadcrumbList
$structured_data .= '<script nonce="' . e($_nonce) . '" type="application/ld+json">
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {"@type":"ListItem","position":1,"name":"Home","item":' . json_encode(public_url('/')) . '},
  {"@type":"ListItem","position":2,"name":"Industries","item":' . json_encode(public_url('/industries')) . '},
  {"@type":"ListItem","position":3,"name":' . json_encode($industry['title']) . '}
]}
</script>';

// FAQPage for challenges
if (!empty($challenge_items) && !empty($challenge_descs)) {
    $faq_items = [];
    foreach ($challenge_items as $ch) {
        $ch = trim($ch);
        if (isset($challenge_descs[$ch])) {
            $faq_items[] = '{"@type":"Question","name":' . json_encode('What is the challenge of ' . $ch . ' in ' . $industry['title'] . '?') . ',"acceptedAnswer":{"@type":"Answer","text":' . json_encode($challenge_descs[$ch]) . '}}';
        }
    }
    if (!empty($faq_items)) {
        $structured_data .= '<script nonce="' . e($_nonce) . '" type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[' . implode(',', $faq_items) . ']}
</script>';
    }
}
?>

<div class="industry-detail-clean">
    <!-- Hero -->
    <section class="page-header page-header--landing-tight">
        <div class="page-header-glow" aria-hidden="true"></div>
        <div class="page-header-glow-2" aria-hidden="true"></div>
        <div class="container">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="<?= url_for('index') ?>">Home</a></li>
                    <li class="breadcrumb-item"><a href="<?= url_for('industries') ?>">Industries</a></li>
                    <li class="breadcrumb-item active"><?= e($industry['title']) ?></li>
                </ol>
            </nav>
            <div class="row align-items-center g-5 page-layout-grid">
                <div class="col-lg-7">
                    <div class="ind-hero-icon"><i class="<?= e($industry['icon_class']) ?>"></i></div>
                    <h1><?= e($industry['title']) ?> <span class="gradient-text">IT Solutions</span></h1>
                    <?php if (file_exists(VIEWS_DIR . '/_hero_slogan.php'))
                        include VIEWS_DIR . '/_hero_slogan.php'; ?>
                    <p class="industry-hero-description">
                        <?= e($industry['hero_description'] ?? $industry['description'] ?? '') ?></p>
                    <div class="hero-buttons industry-hero-actions">
                        <?php if (!empty($site_settings['phone'])): ?>
                            <a href="tel:<?= e($_phone_raw) ?>" class="btn btn-call"><i class="fa-solid fa-phone"></i> Call
                                Now</a>
                        <?php endif; ?>
                        <a href="<?= url_for('request_quote') ?>" class="btn btn-primary">Request a Quote <i
                                class="fa-solid fa-arrow-right"></i></a>
                        <a href="<?= url_for('remote_support') ?>" class="btn btn-remote-support"><i
                                class="fa-solid fa-life-ring"></i> Remote Support</a>
                        <a href="<?= url_for('contact') ?>?subject=Support+Message" class="btn btn-danger"><i
                                class="fa-solid fa-envelope"></i> Send Message</a>
                    </div>
                </div>
                <div class="col-lg-5">
                    <?php if (!empty($stat_items)): ?>
                        <div class="row g-3 industry-stat-grid">
                            <?php foreach ($stat_items as $idx => $stat):
                                $parts = explode(':', $stat, 2);
                                if (count($parts) < 2)
                                    continue;
                                ?>
                                <div class="col-6 industry-stat-col">
                                    <div class="metric-card metric-card--stat">
                                        <div class="mc-icon"><i class="<?= $stat_icons[$idx % 4] ?>"></i></div>
                                        <div class="mc-value"><?= e(trim($parts[1])) ?></div>
                                        <div class="mc-label"><?= e(trim($parts[0])) ?></div>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </section>

    <div class="glow-line"></div>

    <!-- Challenges -->
    <?php if (!empty($challenge_items)): ?>
        <section class="section" id="challenges">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label section-label--industry-challenges"><i
                            class="fa-solid fa-triangle-exclamation"></i> Industry Challenges</div>
                    <h2>Challenges in <?= e($industry['title']) ?></h2>
                    <p class="section-subtitle">Common technology pain points we solve for
                        <?= e(strtolower($industry['title'])) ?> teams.</p>
                </div>
                <div class="row g-4 justify-content-center">
                    <?php foreach ($challenge_items as $idx => $ch):
                        $ch = trim($ch); ?>
                        <div class="col-md-6 col-lg-4">
                            <div class="challenge-card reveal stagger-<?= $idx + 1 ?>">
                                <div class="ch-icon <?= $challenge_colors[$idx % 5] ?>"><i
                                        class="<?= $challenge_icons[$idx % 5] ?>"></i></div>
                                <div>
                                    <h4><?= e($ch) ?></h4>
                                    <?php if (isset($challenge_descs[$ch])): ?>
                                        <p class="card-desc"><?= e($challenge_descs[$ch]) ?></p>
                                    <?php endif; ?>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <div class="glow-line"></div>

    <!-- Solutions -->
    <?php if (!empty($solution_items)): ?>
        <section class="section section--alt" id="solutions">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-check-double"></i> Our Solutions</div>
                    <h2>How We Solve It</h2>
                    <p class="section-subtitle">Targeted solutions designed for <?= e(strtolower($industry['title'])) ?>
                        operations.</p>
                </div>
                <div class="row g-4">
                    <?php foreach ($solution_items as $idx => $sol):
                        $sol = trim($sol); ?>
                        <div class="col-md-6">
                            <div class="solution-card reveal stagger-<?= $idx + 1 ?>">
                                <div class="sol-number"><?= sprintf('%02d', $idx + 1) ?></div>
                                <div class="sol-icon"><i class="<?= $sol_icons[$idx % 5] ?>"></i></div>
                                <div>
                                    <h4><?= e($sol) ?></h4>
                                    <?php if (isset($solution_descs[$sol])): ?>
                                        <p class="card-desc"><?= e($solution_descs[$sol]) ?></p>
                                    <?php endif; ?>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <!-- Related Services -->
    <?php if (!empty($services)): ?>
        <section class="section" id="services">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-cube"></i> Related Services</div>
                    <h2>Services for <?= e($industry['title']) ?></h2>
                    <p class="section-subtitle">Explore the services we deliver to support
                        <?= e(strtolower($industry['title'])) ?> teams.</p>
                </div>
                <div class="row g-4">
                    <?php foreach (array_slice($services, 0, 6) as $idx => $svc): ?>
                        <div class="col-md-6 col-lg-4">
                            <div class="service-card reveal stagger-<?= $idx + 1 ?>">
                                <div class="icon-wrap <?= $colors6[$idx % 6] ?>"><i
                                        class="<?= e($svc['icon_class'] ?? 'fa-solid fa-gear') ?>"></i></div>
                                <h3><?= e($svc['title']) ?></h3>
                                <p><?= e(mb_substr($svc['description'] ?? 'Business-ready service delivery with predictable outcomes.', 0, 88)) ?>
                                </p>
                                <a href="<?= url_for('service_detail', ['slug' => $svc['slug']]) ?>"
                                    class="card-link stretched-link" aria-label="Learn more about <?= e($svc['title']) ?>">Learn
                                    more <i class="fa-solid fa-arrow-right"></i></a>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <!-- Other Industries -->
    <?php if (!empty($other_industries)): ?>
        <section class="section section--alt">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-building"></i> More Industries</div>
                    <h2>Explore Other Industries</h2>
                </div>
                <div class="row g-3 justify-content-center">
                    <?php foreach ($other_industries as $idx => $ind): ?>
                        <div class="col-md-6 col-lg-4 col-xl-3">
                            <a href="<?= url_for('industry_detail', ['slug' => $ind['slug']]) ?>"
                                class="industry-card industry-card--compact reveal stagger-<?= $idx + 1 ?>">
                                <div class="ind-icon <?= $colors6[$idx % 6] ?>"><i
                                        class="<?= e($ind['icon_class'] ?? 'fa-solid fa-building') ?>"></i></div>
                                <h3><?= e($ind['title']) ?></h3>
                                <span class="ind-link">Explore <i class="fa-solid fa-arrow-right"></i></span>
                            </a>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <!-- CTA -->
    <section class="section-sm section-bottom-spacious">
        <div class="cta-section reveal-scale">
            <div class="cta-inner">
                <h2>Ready to Transform Your <?= e($industry['title']) ?> IT?</h2>
                <p>Let's build a technology strategy tailored to your industry.</p>
                <div class="cta-actions cta-actions-dual">
                    <?php if (!empty($site_settings['phone'])): ?>
                        <a href="tel:<?= e($_phone_raw) ?>" class="btn btn-call"><i class="fa-solid fa-phone"></i> Call
                            Now</a>
                    <?php endif; ?>
                    <a href="<?= url_for('request_quote') ?>" class="btn btn-primary">Request a Quote <i
                            class="fa-solid fa-arrow-right"></i></a>
                    <a href="<?= url_for('remote_support') ?>" class="btn btn-remote-support"><i
                            class="fa-solid fa-life-ring"></i> Remote Support</a>
                    <a href="<?= url_for('contact') ?>?subject=Support+Message" class="btn btn-danger"><i
                            class="fa-solid fa-envelope"></i> Send Message</a>
                </div>
            </div>
        </div>
    </section>
</div>