<?php
/**
 * Service Detail page
 */
$page_title = e($service['title']) . ' in Orange County | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = mb_substr($service['description'] ?? ($service['title'] . ' services in Orange County'), 0, 220);
$colors = ['blue', 'purple', 'green', 'amber', 'rose', 'cyan'];
?>

<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <div class="section-label"><i class="<?= e($service['icon_class']) ?>"></i> Service</div>
            <h1>
                <?= e($service['title']) ?>
            </h1>
            <p class="lead">
                <?= e(mb_substr($service['description'] ?? '', 0, 260)) ?>
            </p>
            <div class="hero-buttons">
                <a href="<?= url_for('contact') ?>?subject=<?= urlencode($service['title']) ?>"
                    class="btn btn-primary"><i class="fa-solid fa-calendar-check"></i> Get Started</a>
                <a href="<?= url_for('request_quote') ?>" class="btn btn-ghost"><i class="fa-solid fa-file-lines"></i>
                    Request Quote</a>
            </div>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="section-heading text-center reveal">
            <h2>Service Overview</h2>
        </div>
        <div class="row g-4">
            <div class="col-lg-8 mx-auto">
                <div class="reveal">
                    <p>
                        <?= nl2br(e($service['description'] ?? 'Comprehensive ' . $service['title'] . ' service for Orange County businesses.')) ?>
                    </p>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Related Services -->
<?php if (!empty($related_services)): ?>
    <section class="section section--alt">
        <div class="container">
            <div class="section-heading text-center reveal">
                <h2>Related Services</h2>
            </div>
            <div class="row g-4">
                <?php foreach (array_slice($related_services, 0, 6) as $idx => $rs): ?>
                    <div class="col-md-6 col-lg-4">
                        <div class="service-card reveal" data-delay="<?= $idx * 60 ?>">
                            <div class="icon-wrap <?= $colors[$idx % 6] ?>"><i
                                    class="<?= e($rs['icon_class'] ?? 'fa-solid fa-gear') ?>"></i></div>
                            <h3>
                                <?= e($rs['title']) ?>
                            </h3>
                            <p>
                                <?= e(mb_substr($rs['description'] ?? '', 0, 96)) ?>
                            </p>
                            <a href="<?= url_for('service_detail', ['slug' => $rs['slug']]) ?>"
                                class="card-link stretched-link">Learn more <i class="fa-solid fa-arrow-right"></i></a>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </section>
<?php endif; ?>

<!-- Featured Industries -->
<?php if (!empty($featured_industries)): ?>
    <section class="section">
        <div class="container">
            <div class="section-heading text-center reveal">
                <h2>Industries We Serve</h2>
            </div>
            <div class="row g-4">
                <?php foreach (array_slice($featured_industries, 0, 4) as $idx => $ind): ?>
                    <div class="col-md-6 col-lg-3">
                        <div class="service-card reveal" data-delay="<?= $idx * 60 ?>">
                            <div class="icon-wrap <?= $colors[$idx % 6] ?>"><i
                                    class="<?= e($ind['icon_class'] ?? 'fa-solid fa-building') ?>"></i></div>
                            <h3>
                                <?= e($ind['title']) ?>
                            </h3>
                            <a href="<?= url_for('industry_detail', ['slug' => $ind['slug']]) ?>"
                                class="card-link stretched-link">View industry <i class="fa-solid fa-arrow-right"></i></a>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </section>
<?php endif; ?>

<section class="section">
    <div class="container">
        <div class="cta-strip reveal">
            <div class="cta-inner">
                <h2>Ready to Get Started?</h2>
                <p>Contact us for a personalized
                    <?= e(strtolower($service['title'])) ?> consultation.
                </p>
                <div class="cta-actions">
                    <a href="<?= url_for('contact') ?>?subject=<?= urlencode($service['title']) ?>"
                        class="btn btn-secondary"><i class="fa-solid fa-calendar-check"></i> Schedule Consultation</a>
                    <a href="<?= url_for('request_quote') ?>" class="btn btn-ghost btn-ghost-light"><i
                            class="fa-solid fa-file-lines"></i> Request Quote</a>
                </div>
            </div>
        </div>
    </div>
</section>