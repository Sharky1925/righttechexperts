<?php
/**
 * Homepage — converted from app/templates/index.html
 */

$page_title = 'Managed IT Services & Technical Repair Services in Orange County | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = 'Managed IT services and technical repair services in Orange County. One all-in-one tech and repair shop for business IT support, cybersecurity, cloud, development, and fast device repair.';
$meta_keywords = 'managed IT services Orange County, technical repair services Orange County, business IT support Orange County, cybersecurity Orange County, cloud solutions Orange County, computer repair Orange County';

$_nonce = csp_nonce();
$_phone_raw = preg_replace('/[\s()\-]/', '', $site_settings['phone'] ?? '');
$colors = ['blue', 'purple', 'green', 'amber', 'rose', 'cyan'];
$hero = $cb['hero'] ?? [];
$services_heading = $cb['services_heading'] ?? [];
$ind_heading = $cb['industries_heading'] ?? [];
$stats_section = $cb['stats'] ?? [];
$hiw = $cb['how_it_works'] ?? [];
$testi_heading = $cb['testimonials_heading'] ?? [];
$sa = $cb['service_area'] ?? [];
$cta = $cb['cta'] ?? [];

$structured_data = '<script nonce="' . e($_nonce) . '" type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": ' . json_encode($site_settings['company_name'] ?? 'Right On Repair') . ',
  "description": "Managed IT services and technical repair services in Orange County from one all-in-one tech and repair shop.",
  "provider": { "@type": "Organization", "name": ' . json_encode($site_settings['company_name'] ?? 'Right On Repair') . ' }
}
</script>';
?>

<!-- Hero — Command Center -->
<section class="hero hero--command">
    <div class="hero-glow"></div>
    <div class="hero-glow-2"></div>
    <div class="container">
        <div class="hero-slogan-landing reveal reveal-scale">
            <?php if (file_exists(VIEWS_DIR . '/_hero_slogan.php')): ?>
                <?php include VIEWS_DIR . '/_hero_slogan.php'; ?>
            <?php endif; ?>
        </div>
        <div class="hero-command-top">
            <div class="signal-strip" aria-hidden="true">
                <?php
                $pills = ($cb['signal_pills']['items'] ?? null) ?: ['OC RESPONSE < 2H', '24/7 MONITORING', 'SECURITY-FIRST'];
                foreach ($pills as $pill): ?>
                    <span class="signal-pill">
                        <?= e($pill) ?>
                    </span>
                <?php endforeach; ?>
            </div>
            <div class="hero-badge"><span class="pulse-dot"></span>
                <?= e($hero['badge'] ?? 'Managed IT + Technical Repair for Orange County') ?>
            </div>
            <h1 class="gradient-shimmer">
                <?= e($hero['title'] ?? 'Managed IT Services & Technical Repair Services in Orange County') ?>
            </h1>
            <p class="lead">
                <?= e($hero['lead'] ?? 'One local team for proactive managed IT, cybersecurity, cloud, software, and fast device repair. Your all-in-one tech and repair shop for reliable business uptime.') ?>
            </p>
            <div class="hero-buttons hero-buttons--landing">
                <a href="<?= url_for('contact') ?>?subject=Free+Consultation" class="btn btn-primary"><i
                        class="fa-solid fa-calendar-check"></i> Book Free Consultation</a>
                <a href="<?= url_for('remote_support') ?>" class="btn btn-remote-support"><i
                        class="fa-solid fa-life-ring"></i> Remote Support</a>
                <a href="<?= url_for('contact') ?>?subject=Support+Message" class="btn btn-danger"
                    aria-label="Send a support message"><i class="fa-solid fa-envelope"></i> Send Message</a>
                <?php if (!empty($site_settings['phone'])): ?>
                    <a href="tel:<?= e($_phone_raw) ?>" class="btn btn-call"
                        aria-label="Call support at <?= e($site_settings['phone']) ?>"><i class="fa-solid fa-phone"></i>
                        Call Support</a>
                <?php endif; ?>
            </div>
        </div>
        <div class="hero-cards-grid reveal">
            <?php foreach ($hero_cards as $card): ?>
                <a class="hero-icon-card" href="<?= e($card['href']) ?>" aria-label="<?= e($card['aria_label']) ?>">
                    <div class="hic-icon <?= e($card['color']) ?>"><i class="<?= e($card['icon']) ?>"></i></div>
                    <h4>
                        <?= e($card['title']) ?>
                    </h4>
                    <p>
                        <?= e($card['subtitle']) ?>
                    </p>
                </a>
            <?php endforeach; ?>
        </div>

        <!-- Trust Signal Ticker -->
        <?php $trust_signals = array_slice(($cb['trust_signals']['items'] ?? []), 0, 8); ?>
        <?php if (!empty($trust_signals)): ?>
            <div class="hero-service-crossing reveal" aria-label="Trust and compliance signals">
                <div class="hero-service-lane hero-service-lane--forward">
                    <div class="hero-service-track">
                        <?php foreach ($trust_signals as $idx => $sig): ?>
                            <span class="hero-service-pill" data-pill-delay="<?= $idx * 170 ?>">
                                <i class="<?= e($sig['icon'] ?? '') ?>"></i>
                                <?= e($sig['label'] ?? '') ?>
                            </span>
                        <?php endforeach; ?>
                        <?php foreach ($trust_signals as $idx => $sig): ?>
                            <span class="hero-service-pill" data-pill-delay="<?= $idx * 170 ?>">
                                <i class="<?= e($sig['icon'] ?? '') ?>"></i>
                                <?= e($sig['label'] ?? '') ?>
                            </span>
                        <?php endforeach; ?>
                    </div>
                </div>
            </div>
        <?php endif; ?>
    </div>
</section>

<!-- Services Grid -->
<section class="section" id="services">
    <div class="container">
        <div class="section-heading text-center reveal">
            <div class="section-label"><i class="fa-solid fa-grid-2"></i>
                <?= e($services_heading['label'] ?? 'Services') ?>
            </div>
            <h2>
                <?= e($services_heading['title'] ?? 'Everything Your Business Needs Under One Roof') ?>
            </h2>
            <p>
                <?= e($services_heading['subtitle'] ?? 'From proactive IT management to hands-on device repairs, we handle every layer of your technology.') ?>
            </p>
        </div>
        <div class="row g-4">
            <?php foreach ($pro_services as $idx => $service): ?>
                <div class="col-md-6 col-lg-4">
                    <div class="service-card reveal" data-delay="<?= $idx * 60 ?>">
                        <div class="icon-wrap <?= $colors[$idx % 6] ?>"><i
                                class="<?= e($service['icon_class'] ?? '') ?>"></i></div>
                        <h3>
                            <?= e($service['title']) ?>
                        </h3>
                        <p>
                            <?= e(mb_substr($service['description'] ?? 'Structured technology support tailored to your operations.', 0, 96)) ?>
                        </p>
                        <a href="<?= url_for('service_detail', ['slug' => $service['slug']]) ?>"
                            class="card-link stretched-link" aria-label="Learn more about <?= e($service['title']) ?>">Learn
                            more <i class="fa-solid fa-arrow-right"></i></a>
                    </div>
                </div>
            <?php endforeach; ?>
            <?php $offset = count($pro_services);
            foreach ($repair_services as $idx => $service): ?>
                <div class="col-md-6 col-lg-4">
                    <div class="service-card reveal" data-delay="<?= ($offset + $idx) * 60 ?>">
                        <div class="icon-wrap <?= $colors[($offset + $idx) % 6] ?>"><i
                                class="<?= e($service['icon_class'] ?? '') ?>"></i></div>
                        <h3>
                            <?= e($service['title']) ?>
                        </h3>
                        <p>
                            <?= e(mb_substr($service['description'] ?? 'Structured technology support tailored to your operations.', 0, 96)) ?>
                        </p>
                        <a href="<?= url_for('service_detail', ['slug' => $service['slug']]) ?>"
                            class="card-link stretched-link" aria-label="Learn more about <?= e($service['title']) ?>">Learn
                            more <i class="fa-solid fa-arrow-right"></i></a>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
        <div class="text-center section-cta-spacer">
            <a href="<?= url_for('services') ?>" class="btn btn-ghost">View All Services <i
                    class="fa-solid fa-arrow-right"></i></a>
        </div>
    </div>
</section>

<!-- Industries -->
<section class="section section--alt" id="industries">
    <div class="container">
        <div class="section-heading text-center reveal">
            <div class="section-label"><i class="fa-solid fa-city"></i>
                <?= e($ind_heading['label'] ?? 'Industries') ?>
            </div>
            <h2>
                <?= e($ind_heading['title'] ?? 'Industry-Specific IT Support') ?>
            </h2>
            <p>
                <?= e($ind_heading['subtitle'] ?? 'We tailor security, support, and technology strategy to how your industry works.') ?>
            </p>
        </div>
        <div class="row g-4">
            <?php foreach (array_slice($nav_industries, 0, 8) as $idx => $ind): ?>
                <div class="col-md-6 col-lg-3">
                    <div class="service-card reveal" data-delay="<?= $idx * 60 ?>">
                        <div class="icon-wrap <?= $colors[$idx % 6] ?>"><i class="<?= e($ind['icon_class'] ?? '') ?>"></i>
                        </div>
                        <h3>
                            <?= e($ind['title']) ?>
                        </h3>
                        <p>
                            <?= e(mb_substr($ind['description'] ?? 'Industry-specific support aligned to your workflows.', 0, 84)) ?>
                        </p>
                        <a href="<?= url_for('industry_detail', ['slug' => $ind['slug']]) ?>"
                            class="card-link stretched-link" aria-label="Learn more about <?= e($ind['title']) ?>">Industry
                            Page <i class="fa-solid fa-arrow-right"></i></a>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
        <div class="text-center section-cta-spacer">
            <a href="<?= url_for('industries') ?>" class="btn btn-ghost">View All Industries <i
                    class="fa-solid fa-arrow-right"></i></a>
        </div>
    </div>
</section>

<!-- Stats -->
<section class="section">
    <div class="container">
        <div class="section-heading text-center reveal">
            <div class="section-label"><i class="fa-solid fa-chart-column"></i>
                <?= e($stats_section['label'] ?? 'Results') ?>
            </div>
            <h2>
                <?= e($stats_section['title'] ?? 'Measurable Impact for Local Businesses') ?>
            </h2>
        </div>
        <div class="stat-grid reveal">
            <?php
            $default_stats = [
                ['value' => '500+', 'title' => 'Devices Managed', 'note' => 'Across Orange County businesses'],
                ['value' => '99.9%', 'title' => 'Uptime Target', 'note' => 'Proactive monitoring & patching'],
                ['value' => '<2hr', 'title' => 'Response Time', 'note' => 'For critical support requests'],
                ['value' => '100%', 'title' => 'Local Focus', 'note' => 'Orange County businesses only'],
            ];
            foreach (($stats_section['items'] ?? $default_stats) as $s): ?>
                <div class="stat-card">
                    <span class="stat-value">
                        <?= e($s['value'] ?? '') ?>
                    </span>
                    <h4>
                        <?= e($s['title'] ?? '') ?>
                    </h4>
                    <p class="stat-note">
                        <?= e($s['note'] ?? '') ?>
                    </p>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
</section>

<!-- How It Works -->
<section class="section section--alt">
    <div class="container">
        <div class="section-heading text-center reveal">
            <div class="section-label"><i class="fa-solid fa-diagram-project"></i>
                <?= e($hiw['label'] ?? 'How It Works') ?>
            </div>
            <h2>
                <?= e($hiw['title'] ?? 'Get Started in Three Steps') ?>
            </h2>
            <p>
                <?= e($hiw['subtitle'] ?? 'From first call to full coverage, we make the process simple and transparent.') ?>
            </p>
        </div>
        <div class="timeline-grid reveal">
            <?php
            $default_steps = [
                ['title' => 'Free Assessment', 'description' => 'We review your current systems, devices, and pain points in a 30-minute call.'],
                ['title' => 'Custom Plan', 'description' => 'You get a clear proposal with scope, pricing, and timeline — no guessing.'],
                ['title' => 'Ongoing Support', 'description' => 'We onboard your team, start monitoring, and provide proactive support.'],
            ];
            foreach (($hiw['items'] ?? $default_steps) as $idx => $step): ?>
                <div class="timeline-card" data-delay="<?= $idx * 80 ?>">
                    <span class="process-icon">
                        <?= sprintf('%02d', $idx + 1) ?>
                    </span>
                    <div>
                        <h4>
                            <?= e($step['title'] ?? '') ?>
                        </h4>
                        <p>
                            <?= e($step['description'] ?? '') ?>
                        </p>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
</section>

<!-- Testimonials -->
<?php if (!empty($testimonials)): ?>
    <section class="section">
        <div class="container">
            <div class="section-heading text-center reveal">
                <div class="section-label"><i class="fa-solid fa-star"></i>
                    <?= e($testi_heading['label'] ?? 'Testimonials') ?>
                </div>
                <h2>
                    <?= e($testi_heading['title'] ?? 'Client Success Stories') ?>
                </h2>
            </div>
            <div class="row g-4">
                <?php foreach ($testimonials as $idx => $t): ?>
                    <div class="col-md-6 col-lg-3">
                        <div class="testimonial-card reveal" data-delay="<?= $idx * 80 ?>">
                            <i class="fa-solid fa-quote-right quote-icon"></i>
                            <div class="stars">
                                <?php for ($i = 0; $i < ($t['rating'] ?? 5); $i++): ?><i class="fa-solid fa-star"></i>
                                <?php endfor; ?>
                            </div>
                            <div class="content">"
                                <?= e($t['content'] ?? '') ?>"
                            </div>
                            <div class="author">
                                <div class="author-avatar">
                                    <?= e(mb_substr($t['client_name'] ?? '?', 0, 1)) ?>
                                </div>
                                <div>
                                    <div class="author-name">
                                        <?= e($t['client_name'] ?? '') ?>
                                    </div>
                                    <div class="author-role">
                                        <?= e($t['company'] ?? '') ?>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </section>
<?php endif; ?>

<!-- Service Area / Local SEO -->
<section class="section">
    <div class="container">
        <div class="section-heading text-center reveal">
            <div class="section-label"><i class="fa-solid fa-location-dot"></i>
                <?= e($sa['label'] ?? 'Service Area') ?>
            </div>
            <h2>
                <?= e($sa['title'] ?? 'IT Services Across Orange County') ?>
            </h2>
            <p>
                <?= e($sa['subtitle'] ?? 'On-site and remote support for businesses throughout the region.') ?>
            </p>
        </div>
        <div class="chip-list chip-list-centered reveal">
            <?php foreach (($sa['cities'] ?? ORANGE_COUNTY_CA_CITIES) as $city): ?>
                <span class="chip"><i class="fa-solid fa-location-dot"></i>
                    <?= e($city) ?>
                </span>
            <?php endforeach; ?>
        </div>
    </div>
</section>

<!-- Final CTA -->
<section class="section">
    <div class="container">
        <div class="cta-strip reveal">
            <div class="cta-inner">
                <h2>
                    <?= e($cta['title'] ?? 'Ready To Fix Your IT?') ?>
                </h2>
                <p>
                    <?= e($cta['subtitle'] ?? 'Schedule a free consultation or call us directly. No obligations, no pressure — just a clear plan for better IT.') ?>
                </p>
                <div class="cta-actions">
                    <a href="<?= url_for('contact') ?>?subject=Free+Consultation" class="btn btn-secondary"><i
                            class="fa-solid fa-calendar-check"></i>
                        <?= e($cta['button_text'] ?? 'Schedule a Meeting') ?>
                    </a>
                    <a href="<?= url_for('remote_support') ?>" class="btn btn-remote-support"><i
                            class="fa-solid fa-life-ring"></i> Remote Support</a>
                    <?php if (!empty($site_settings['phone'])): ?>
                        <a href="tel:<?= e($_phone_raw) ?>" class="btn btn-ghost btn-ghost-light"><i
                                class="fa-solid fa-phone"></i>
                            <?= e($site_settings['phone']) ?>
                        </a>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>
</section>