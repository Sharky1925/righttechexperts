<?php
/**
 * Services listing page
 */
$page_title = 'IT Services & Technical Repair | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = 'Full-spectrum IT services and technical repair in Orange County. Managed IT, cybersecurity, cloud, development, and device repair under one roof.';
$colors = ['blue', 'purple', 'green', 'amber', 'rose', 'cyan'];
$hero = $cb['hero'] ?? [];
?>

<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <div class="section-label"><i class="fa-solid fa-grid-2"></i> Services</div>
            <h1>
                <?= e($hero['title'] ?? 'IT Services & Technical Repair') ?>
            </h1>
            <p class="lead">
                <?= e($hero['lead'] ?? 'Managed IT, cybersecurity, cloud solutions, software development, and technical device repair — all from one trusted Orange County partner.') ?>
            </p>
        </div>
    </div>
</section>

<!-- Professional IT Services -->
<section class="section" id="professional">
    <div class="container">
        <div class="section-heading text-center reveal">
            <h2>Professional IT Services</h2>
            <p>Managed IT, cybersecurity, cloud, and development services for business growth.</p>
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
                            <?= e(mb_substr($service['description'] ?? '', 0, 120)) ?>
                        </p>
                        <a href="<?= url_for('service_detail', ['slug' => $service['slug']]) ?>"
                            class="card-link stretched-link">Learn more <i class="fa-solid fa-arrow-right"></i></a>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
</section>

<!-- Technical Repair Services -->
<section class="section section--alt" id="repair">
    <div class="container">
        <div class="section-heading text-center reveal">
            <h2>Technical Repair Services</h2>
            <p>Fast, reliable device repair by certified technicians.</p>
        </div>
        <div class="row g-4">
            <?php foreach ($repair_services as $idx => $service): ?>
                <div class="col-md-6 col-lg-4">
                    <div class="service-card reveal" data-delay="<?= $idx * 60 ?>">
                        <div class="icon-wrap <?= $colors[$idx % 6] ?>"><i
                                class="<?= e($service['icon_class'] ?? '') ?>"></i></div>
                        <h3>
                            <?= e($service['title']) ?>
                        </h3>
                        <p>
                            <?= e(mb_substr($service['description'] ?? '', 0, 120)) ?>
                        </p>
                        <a href="<?= url_for('service_detail', ['slug' => $service['slug']]) ?>"
                            class="card-link stretched-link">Learn more <i class="fa-solid fa-arrow-right"></i></a>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="cta-strip reveal">
            <div class="cta-inner">
                <h2>Need Help Choosing?</h2>
                <p>Schedule a free consultation and we'll recommend the right services for your business.</p>
                <div class="cta-actions">
                    <a href="<?= url_for('contact') ?>?subject=Free+Consultation" class="btn btn-secondary"><i
                            class="fa-solid fa-calendar-check"></i> Book Consultation</a>
                    <a href="<?= url_for('request_quote') ?>" class="btn btn-ghost btn-ghost-light"><i
                            class="fa-solid fa-file-lines"></i> Request Quote</a>
                </div>
            </div>
        </div>
    </div>
</section>