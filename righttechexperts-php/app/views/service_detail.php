<?php
/**
 * Service Detail page — FULL PARITY with 677-line Django template
 * Sections: hero, service modules, SEO content blocks, issue-solution map,
 * process workflow, lead-time diagram, local coverage & trust, tools & platforms,
 * brand coverage, related services, industries, related posts, FAQs, CTA
 */

// Profile data — from controller (service_profile) or defaults
$sp = $service_profile ?? [];
$meta_desc = $sp['meta_description'] ?? mb_substr($service['description'] ?? ($service['title'] . ' service support for Orange County businesses.'), 0, 220);
$meta_title_val = $sp['meta_title'] ?? ($service['title'] . ' — ' . ($site_settings['company_name'] ?? 'Right On Repair'));
$profile_keywords = $sp['keywords'] ?? [$service['title'] . ' Orange County', $service['title'] . ' service', 'business IT support'];
$process_steps = $sp['process'] ?? [];
$tool_stack = $sp['tools'] ?? [];
$deliverables = $sp['deliverables'] ?? [];
$faqs = $sp['faqs'] ?? [];
$hero_badges = $sp['hero_badges'] ?? [];
$service_modules = $sp['service_modules'] ?? [];
$issue_solution_map = $sp['issue_solution_map'] ?? [];
$narrative_title = $sp['narrative_title'] ?? 'Service Scope and Delivery Standards';
$seo_content_blocks = $sp['seo_content_blocks'] ?? [];
$local_cities = $sp['service_area_cities'] ?? ORANGE_COUNTY_CA_CITIES;
$compliance_frameworks = $sp['compliance_frameworks'] ?? [];
$proof_points = $sp['proof_points'] ?? [];
$lead_time_steps = $sp['lead_time_diagram'] ?? [];
$related_technologies = $sp['related_technologies'] ?? [];
$supported_brands = $sp['supported_brands'] ?? [];
$brand_services_list = $sp['brand_services'] ?? [];
$hero_tools = !empty($related_technologies) ? $related_technologies : array_column($tool_stack, 'name');
$hero_brands = !empty($supported_brands) ? $supported_brands : array_column($brand_services_list, 'brand');

$page_title = $meta_title_val;
$meta_description = $meta_desc;
$meta_keywords = implode(', ', $profile_keywords);
$_nonce = csp_nonce();
$_phone_raw = preg_replace('/[\s()\-]/', '', $site_settings['phone'] ?? '');
$mc_colors = ['blue', 'purple', 'green', 'amber'];
$colors6 = ['blue', 'purple', 'green', 'amber', 'rose', 'cyan'];

// Structured Data
$structured_data = '';
// Service schema
$structured_data .= '<script nonce="' . e($_nonce) . '" type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": ' . json_encode($service['title']) . ',
  "description": ' . json_encode($meta_desc) . ',
  "serviceType": ' . json_encode($service['service_type'] ?? 'IT') . ',
  "url": ' . json_encode(public_url('/services/' . $service['slug'])) . ',
  "provider": {
    "@type": "Organization",
    "name": ' . json_encode($site_settings['company_name'] ?? 'Right On Repair') . ',
    "telephone": ' . json_encode($site_settings['phone'] ?? '') . ',
    "email": ' . json_encode($site_settings['email'] ?? '') . '
  },
  "areaServed": [' . (!empty($local_cities)
    ? implode(',', array_map(fn($c) => '{"@type":"City","name":' . json_encode($c . ', CA') . '}', array_slice($local_cities, 0, 10)))
    : '{"@type":"AdministrativeArea","name":"Orange County, CA"}'
) . ']
}
</script>';

// BreadcrumbList
$structured_data .= '<script nonce="' . e($_nonce) . '" type="application/ld+json">
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {"@type":"ListItem","position":1,"name":"Home","item":' . json_encode(public_url('/')) . '},
  {"@type":"ListItem","position":2,"name":"Services","item":' . json_encode(public_url('/services')) . '},
  {"@type":"ListItem","position":3,"name":' . json_encode($service['title']) . ',"item":' . json_encode(public_url('/services/' . $service['slug'])) . '}
]}
</script>';

// FAQPage schema
if (!empty($faqs)) {
    $faq_items = [];
    foreach ($faqs as $f) {
        $faq_items[] = '{"@type":"Question","name":' . json_encode($f['q']) . ',"acceptedAnswer":{"@type":"Answer","text":' . json_encode($f['a']) . '}}';
    }
    $structured_data .= '<script nonce="' . e($_nonce) . '" type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[' . implode(',', $faq_items) . ']}
</script>';
}
?>

<div class="service-detail-clean">
    <!-- Hero -->
    <section
        class="page-header section-bottom-spacious page-header--landing-tight service-theme service-theme--<?= e($service['slug']) ?> <?= ($service['service_type'] ?? '') === 'repair' ? 'page-header--repair-tight' : '' ?>"
        id="service-overview">
        <div class="container">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="<?= url_for('index') ?>">Home</a></li>
                    <li class="breadcrumb-item"><a href="<?= url_for('services') ?>">Services</a></li>
                    <li class="breadcrumb-item active"><?= e($service['title']) ?></li>
                </ol>
            </nav>
            <div
                class="row g-5 page-layout-grid align-items-start service-hero-row <?= ($service['service_type'] ?? '') === 'repair' ? 'service-repair-hero-row' : '' ?>">
                <div class="col-lg-7 reveal-left">
                    <div class="ind-hero-icon"><i class="<?= e($service['icon_class']) ?>"></i></div>
                    <?php if (!empty($sp['positioning_badge'])): ?>
                        <div class="service-kicker-badge"><?= e($sp['positioning_badge']) ?></div>
                    <?php endif; ?>
                    <h1><?= e($service['title']) ?> <span
                            class="gradient-text"><?= e($sp['intro_kicker'] ?? 'Solutions') ?></span></h1>
                    <?php if (file_exists(VIEWS_DIR . '/_hero_slogan.php'))
                        include VIEWS_DIR . '/_hero_slogan.php'; ?>
                    <p class="industry-hero-description"><?= e($meta_desc) ?></p>
                    <div class="hero-buttons industry-hero-actions">
                        <?php if (!empty($site_settings['phone'])): ?>
                            <a href="tel:<?= e($_phone_raw) ?>" class="btn btn-call"><i class="fa-solid fa-phone"></i> Call
                                Now</a>
                        <?php endif; ?>
                        <a href="<?= url_for('request_quote') ?>" class="btn btn-primary">Request A Quote <i
                                class="fa-solid fa-magnifying-glass-chart"></i></a>
                        <a href="<?= url_for('remote_support') ?>" class="btn btn-remote-support">Remote Support <i
                                class="fa-solid fa-life-ring"></i></a>
                        <a href="<?= url_for('contact') ?>?subject=Support+Message" class="btn btn-danger"><i
                                class="fa-solid fa-envelope"></i> Send Message</a>
                    </div>
                    <?php if (!empty($hero_badges)): ?>
                        <div class="service-hero-badges">
                            <?php foreach (array_slice($hero_badges, 0, 3) as $badge): ?>
                                <span><i class="<?= e($badge['icon']) ?>"></i><?= e($badge['label']) ?></span>
                            <?php endforeach; ?>
                        </div>
                    <?php endif; ?>
                </div>
                <div class="col-lg-5 reveal-right service-hero-side-col">
                    <div class="row g-3 service-hero-metric-grid">
                        <?php foreach (array_slice($deliverables, 0, 4) as $idx => $outcome): ?>
                            <div class="col-6">
                                <article class="metric-card service-hero-metric-card">
                                    <div class="mc-icon <?= $mc_colors[$idx % 4] ?>"><i
                                            class="<?= e($outcome['icon']) ?>"></i></div>
                                    <div class="mc-label"><?= e($outcome['label']) ?></div>
                                    <div class="mc-value"><?= e($outcome['value']) ?></div>
                                </article>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            </div>

            <?php if (!empty($hero_tools) || !empty($hero_brands)): ?>
                <div class="row g-4 service-hero-support-row reveal">
                    <?php if (!empty($hero_tools)): ?>
                        <div class="<?= !empty($hero_brands) ? 'col-lg-6' : 'col-12' ?>">
                            <aside class="service-visual-panel service-hero-support-card service-hero-tools-card h-100">
                                <div class="service-panel-head">
                                    <h2><i class="fa-solid fa-layer-group"></i> Tools &amp; Technologies</h2>
                                    <p>Core platforms used to deliver <?= e(strtolower($service['title'])) ?> outcomes.</p>
                                </div>
                                <div class="service-tool-cloud service-tool-cloud--compact">
                                    <?php foreach (array_slice($hero_tools, 0, 8) as $tech): ?>
                                        <span class="service-tool-pill"><i class="fa-solid fa-microchip"></i><?= e($tech) ?></span>
                                    <?php endforeach; ?>
                                </div>
                            </aside>
                        </div>
                    <?php endif; ?>
                    <?php if (!empty($hero_brands)): ?>
                        <div class="<?= !empty($hero_tools) ? 'col-lg-6' : 'col-12' ?>">
                            <aside class="service-visual-panel service-hero-support-card service-hero-brands-card h-100">
                                <div class="service-panel-head">
                                    <h2><i class="fa-solid fa-certificate"></i> Supported Brands</h2>
                                    <p>Validated service coverage for major hardware and platform vendors.</p>
                                </div>
                                <div class="brand-pill-grid brand-pill-grid--compact">
                                    <?php foreach (array_slice($hero_brands, 0, 8) as $brand): ?>
                                        <span class="brand-pill"><?= e($brand) ?></span>
                                    <?php endforeach; ?>
                                </div>
                            </aside>
                        </div>
                    <?php endif; ?>
                </div>
            <?php endif; ?>

            <div class="service-snapshot-grid reveal mt-4">
                <article class="service-snapshot-card">
                    <div class="snap-icon"><i class="fa-solid fa-magnifying-glass-chart"></i></div>
                    <h3>Primary Search Intent</h3>
                    <p><?= e($profile_keywords[0] ?? ($service['title'] . ' Orange County')) ?></p>
                </article>
                <article class="service-snapshot-card">
                    <div class="snap-icon"><i class="fa-solid fa-cubes"></i></div>
                    <h3>Specialized Modules</h3>
                    <p><?= !empty($service_modules) ? count($service_modules) . ' service tracks aligned to ' . e(strtolower($service['title'])) . ' outcomes.' : 'Structured delivery playbooks aligned to ' . e(strtolower($service['title'])) . ' business outcomes.' ?>
                    </p>
                </article>
                <article class="service-snapshot-card">
                    <div class="snap-icon"><i class="fa-solid fa-location-dot"></i></div>
                    <h3>Local Coverage</h3>
                    <p><?= !empty($local_cities) ? count($local_cities) . ' Orange County cities with onsite and remote delivery support.' : 'Orange County-wide onsite and remote delivery coverage for every service engagement.' ?>
                    </p>
                </article>
                <article class="service-snapshot-card">
                    <div class="snap-icon"><i class="fa-solid fa-hourglass-half"></i></div>
                    <h3>Lead-Time Transparency</h3>
                    <p><?= e(!empty($lead_time_steps) ? $lead_time_steps[0]['phase'] : 'Structured intake') ?> with
                        clear delivery checkpoints.</p>
                </article>
            </div>
        </div>
    </section>

    <?php if (!empty($service_modules)): ?>
        <section class="section" id="service-scope">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-cubes"></i> Service Scope</div>
                    <h2><?= e($sp['modules_title'] ?? 'Specialized Service Programs') ?></h2>
                </div>
                <div class="row g-4 justify-content-center">
                    <?php foreach ($service_modules as $idx => $item): ?>
                        <div class="col-md-6 col-lg-3">
                            <article class="challenge-card reveal stagger-<?= $idx + 1 ?> h-100">
                                <div class="ch-icon <?= $colors6[$idx % 6] ?>"><i class="<?= e($item['icon']) ?>"></i></div>
                                <div class="ch-body">
                                    <h4><?= e($item['title']) ?></h4>
                                    <p><?= e($item['detail']) ?></p>
                                </div>
                            </article>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <?php if (!empty($seo_content_blocks)): ?>
        <section class="section section--alt" id="service-positioning">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-file-lines"></i> Service Positioning</div>
                    <h2><?= e($narrative_title) ?></h2>
                </div>
                <div class="row g-4">
                    <?php foreach ($seo_content_blocks as $idx => $block): ?>
                        <div class="col-lg-6">
                            <div
                                class="service-visual-panel h-100 reveal <?= ($idx % 2 === 1) ? 'reveal-right' : 'reveal-left' ?>">
                                <p class="mb-0"><?= e($block) ?></p>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <div class="glow-line"></div>

    <?php if (!empty($issue_solution_map)): ?>
        <section class="section" id="service-issues">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-triangle-exclamation"></i> What We Solve</div>
                    <h2>Common Challenges and Execution Response</h2>
                </div>
                <div class="issue-map-grid">
                    <?php foreach ($issue_solution_map as $idx => $item): ?>
                        <article class="issue-map-card reveal stagger-<?= $idx + 1 ?>">
                            <div class="issue-icon"><i class="<?= e($item['icon']) ?>"></i></div>
                            <h3><?= e($item['issue']) ?></h3>
                            <p><?= e($item['solution']) ?></p>
                        </article>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <div class="glow-line"></div>

    <?php if (!empty($process_steps)): ?>
        <section class="section" id="service-workflow">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-diagram-project"></i> How It Works</div>
                    <h2><?= e($sp['board_title'] ?? 'Service Workflow') ?></h2>
                </div>
                <div class="row g-4 justify-content-center">
                    <?php foreach ($process_steps as $idx => $step): ?>
                        <div class="col-md-6 col-lg-4">
                            <div class="challenge-card reveal stagger-<?= $idx + 1 ?>">
                                <div class="ch-icon <?= $colors6[$idx % 6] ?>"><i class="<?= e($step['icon']) ?>"></i></div>
                                <div class="ch-body">
                                    <h4><?= e($step['title']) ?></h4>
                                    <p><?= e($step['detail']) ?></p>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <div class="glow-line"></div>

    <?php if (!empty($lead_time_steps)): ?>
        <section class="section section--alt" id="service-lead-time">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-hourglass-half"></i> Lead Time Diagram</div>
                    <h2>From Intake to Delivery</h2>
                </div>
                <div class="lead-time-grid">
                    <?php foreach ($lead_time_steps as $idx => $item): ?>
                        <article class="lead-time-card reveal stagger-<?= $idx + 1 ?>">
                            <div class="lead-time-step">Step <?= $idx + 1 ?></div>
                            <div class="lead-time-icon"><i class="<?= e($item['icon']) ?>"></i></div>
                            <h3><?= e($item['phase']) ?></h3>
                            <div class="lead-time-eta"><?= e($item['eta']) ?></div>
                            <p><?= e($item['detail']) ?></p>
                        </article>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <div class="glow-line"></div>

    <?php if (!empty($local_cities) || !empty($compliance_frameworks) || !empty($proof_points)): ?>
        <section class="section section--alt" id="service-trust">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-location-dot"></i> Local Coverage &amp; Trust</div>
                    <h2>Operational Readiness Across Orange County</h2>
                </div>
                <div class="row g-4">
                    <div class="col-lg-6">
                        <div class="service-visual-panel h-100 reveal-left">
                            <div class="service-panel-head">
                                <h2><i class="fa-solid fa-map-location-dot"></i> Cities We Serve</h2>
                                <p>Field and remote support coverage for organizations across Orange County.</p>
                            </div>
                            <?php if (!empty($local_cities)): ?>
                                <div class="service-tool-cloud">
                                    <?php foreach ($local_cities as $city): ?>
                                        <span class="service-tool-pill"><i
                                                class="fa-solid fa-location-crosshairs"></i><?= e($city) ?></span>
                                    <?php endforeach; ?>
                                </div>
                            <?php endif; ?>
                        </div>
                    </div>
                    <div class="col-lg-6">
                        <div class="service-visual-panel h-100 reveal-right">
                            <div class="service-panel-head">
                                <h2><i class="fa-solid fa-shield-halved"></i> Governance Alignment</h2>
                                <p>Delivery model built around security, accountability, and measurable outcomes.</p>
                            </div>
                            <ul class="service-value-list mb-0">
                                <?php foreach ($compliance_frameworks as $item): ?>
                                    <li><i class="fa-solid fa-circle-check"></i><?= e($item) ?></li>
                                <?php endforeach; ?>
                                <?php foreach ($proof_points as $point): ?>
                                    <li><i class="fa-solid fa-bullseye"></i><strong><?= e($point['label']) ?>:</strong>
                                        <?= e($point['value']) ?></li>
                                <?php endforeach; ?>
                                <?php if (empty($compliance_frameworks) && empty($proof_points)): ?>
                                    <li><i class="fa-solid fa-circle-check"></i>Security-first execution, documented escalation
                                        paths, and milestone-based reporting for every engagement.</li>
                                <?php endif; ?>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <div class="glow-line"></div>

    <?php if (!empty($tool_stack)): ?>
        <section class="section" id="service-tools">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-layer-group"></i> Tools &amp; Platforms</div>
                    <h2>Related Technologies &amp; Tools</h2>
                </div>
                <?php if (!empty($related_technologies)): ?>
                    <div class="service-technology-wrap reveal">
                        <div class="service-tool-cloud">
                            <?php foreach ($related_technologies as $tech): ?>
                                <span class="service-tool-pill"><i class="fa-solid fa-microchip"></i><?= e($tech) ?></span>
                            <?php endforeach; ?>
                        </div>
                    </div>
                <?php endif; ?>
                <div class="row g-4">
                    <?php foreach ($tool_stack as $idx => $tool): ?>
                        <div class="col-md-6">
                            <div class="feature-item reveal stagger-<?= $idx + 1 ?>">
                                <div class="fi-icon <?= $colors6[$idx % 6] ?>"><i class="<?= e($tool['icon']) ?>"></i></div>
                                <div>
                                    <h4><?= e($tool['name']) ?></h4>
                                    <?php if (!empty($tool['desc'])): ?>
                                        <p><?= e($tool['desc']) ?></p><?php endif; ?>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <?php if (!empty($supported_brands) || !empty($brand_services_list)): ?>
        <section class="section section--alt" id="service-brands">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-certificate"></i> Brand Coverage</div>
                    <h2>Supported Brands and Service Scope</h2>
                </div>
                <div class="row g-4">
                    <div class="col-lg-5">
                        <div class="service-visual-panel h-100 reveal-left">
                            <div class="service-panel-head">
                                <h2><i class="fa-solid fa-tags"></i> Brands We Support</h2>
                                <p>Technical coverage across major commercial and consumer hardware ecosystems.</p>
                            </div>
                            <?php if (!empty($supported_brands)): ?>
                                <div class="brand-pill-grid">
                                    <?php foreach ($supported_brands as $brand): ?>
                                        <span class="brand-pill"><?= e($brand) ?></span>
                                    <?php endforeach; ?>
                                </div>
                            <?php endif; ?>
                        </div>
                    </div>
                    <div class="col-lg-7">
                        <div class="service-visual-panel h-100 reveal-right">
                            <div class="service-panel-head">
                                <h2><i class="fa-solid fa-list-check"></i> Service Coverage by Brand</h2>
                                <p>Repair, diagnostics, and validation workflows tailored to each platform family.</p>
                            </div>
                            <div class="brand-service-grid">
                                <?php foreach ($brand_services_list as $item): ?>
                                    <article class="brand-service-card">
                                        <h3><?= e($item['brand']) ?></h3>
                                        <p><?= e($item['services']) ?></p>
                                    </article>
                                <?php endforeach; ?>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <?php if (!empty($related_services)): ?>
        <section class="section section--alt">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-arrows-split-up-and-left"></i> Related Services</div>
                    <h2>Build a Full Coverage IT Stack</h2>
                </div>
                <div class="row g-4">
                    <?php foreach ($related_services as $idx => $rel): ?>
                        <div class="col-md-6 col-lg-4">
                            <a href="<?= url_for('service_detail', ['slug' => $rel['slug']]) ?>"
                                class="feature-item reveal stagger-<?= $idx + 1 ?> h-100 text-decoration-none">
                                <div class="fi-icon <?= $colors6[$idx % 6] ?>"><i
                                        class="<?= e($rel['icon_class'] ?? 'fa-solid fa-gear') ?>"></i></div>
                                <div>
                                    <h4><?= e($rel['title']) ?></h4>
                                    <p><?= e(mb_substr($rel['description'] ?? '', 0, 140)) ?></p>
                                </div>
                            </a>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <?php if (!empty($featured_industries)): ?>
        <section class="section">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-building"></i> Industry Coverage</div>
                    <h2>Playbooks for Sector-Specific Environments</h2>
                </div>
                <div class="row g-4 service-industries-grid">
                    <?php foreach ($featured_industries as $idx => $ind): ?>
                        <div class="col-md-6 col-lg-4">
                            <a href="<?= url_for('industry_detail', ['slug' => $ind['slug']]) ?>"
                                class="industry-card industry-card--service-link reveal stagger-<?= $idx + 1 ?> h-100 text-decoration-none"
                                aria-label="View <?= e($ind['title']) ?> industry playbook">
                                <div class="ind-icon <?= $colors6[$idx % 6] ?>"><i
                                        class="<?= e($ind['icon_class'] ?? 'fa-solid fa-building') ?>"></i></div>
                                <h3><?= e($ind['title']) ?></h3>
                                <p><?= e(mb_substr($ind['description'] ?? '', 0, 140)) ?></p>
                                <span class="ind-link">See industry playbook <i class="fa-solid fa-arrow-right"></i></span>
                            </a>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <?php if (!empty($faqs)): ?>
        <section class="section" id="service-faq">
            <div class="container">
                <div class="section-heading text-center reveal">
                    <div class="section-label"><i class="fa-solid fa-circle-question"></i> FAQ</div>
                    <h2>Frequently Asked Questions</h2>
                </div>
                <div class="service-faq-list reveal">
                    <?php foreach ($faqs as $idx => $faq): ?>
                        <details class="service-faq-item" <?= $idx === 0 ? 'open' : '' ?>>
                            <summary><?= e($faq['q']) ?></summary>
                            <p><?= e($faq['a']) ?></p>
                        </details>
                    <?php endforeach; ?>
                </div>
            </div>
        </section>
    <?php endif; ?>

    <section class="section-sm section-bottom-spacious" id="service-contact">
        <div class="cta-section reveal-scale">
            <div class="cta-inner">
                <h2>Request A Quote</h2>
                <p>Get a scoped plan for <?= e(strtolower($service['title'])) ?>, with clear priorities, timeline
                    options, and next steps.</p>
                <div class="cta-actions cta-actions-dual">
                    <?php if (!empty($site_settings['phone'])): ?>
                        <a href="tel:<?= e($_phone_raw) ?>" class="btn btn-call"><i class="fa-solid fa-phone"></i> Call
                            Now</a>
                    <?php endif; ?>
                    <a href="<?= url_for('request_quote') ?>" class="btn btn-quote"><i
                            class="fa-solid fa-file-invoice-dollar"></i> Request A Quote</a>
                    <a href="<?= url_for('contact') ?>?subject=<?= urlencode('Service Consultation: ' . $service['title']) ?>"
                        class="btn btn-danger"><i class="fa-solid fa-envelope"></i> Send Message</a>
                </div>
            </div>
        </div>
    </section>
</div>