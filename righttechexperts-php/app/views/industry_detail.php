<?php
$page_title = e($industry['title']) . ' IT Services | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = mb_substr($hero_description ?: ($industry['title'] . ' IT services in Orange County'), 0, 220);
$colors = ['blue', 'purple', 'green', 'amber', 'rose', 'cyan'];
$challenge_list = array_filter(explode('|', $challenges));
$solution_list = array_filter(explode('|', $solutions));
$stat_list = array_filter(explode('|', $stats));
?>
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <div class="section-label"><i class="<?= e($industry['icon_class']) ?>"></i> Industry</div>
            <h1>
                <?= e($industry['title']) ?>
            </h1>
            <p class="lead">
                <?= e($hero_description ?: $industry['description'] ?? '') ?>
            </p>
            <div class="hero-buttons">
                <a href="<?= url_for('contact') ?>?subject=<?= urlencode($industry['title'] . ' IT Support') ?>"
                    class="btn btn-primary"><i class="fa-solid fa-calendar-check"></i> Get Started</a>
                <a href="<?= url_for('request_quote') ?>" class="btn btn-ghost"><i class="fa-solid fa-file-lines"></i>
                    Request Quote</a>
            </div>
        </div>
    </div>
</section>

<?php if (!empty($stat_list)): ?>
    <section class="section">
        <div class="container">
            <div class="stat-grid reveal">
                <?php foreach ($stat_list as $s):
                    $parts = explode(':', $s, 2);
                    if (count($parts) < 2)
                        continue; ?>
                    <div class="stat-card"><span class="stat-value">
                            <?= e(trim($parts[1])) ?>
                        </span>
                        <h4>
                            <?= e(trim($parts[0])) ?>
                        </h4>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </section>
<?php endif; ?>

<?php if (!empty($challenge_list)): ?>
    <section class="section section--alt">
        <div class="container">
            <div class="section-heading text-center reveal">
                <h2>Industry Challenges</h2>
            </div>
            <div class="row g-4">
                <?php foreach ($challenge_list as $idx => $ch): ?>
                    <div class="col-md-6">
                        <div class="service-card reveal" data-delay="<?= $idx * 60 ?>">
                            <div class="icon-wrap <?= $colors[$idx % 6] ?>"><i class="fa-solid fa-triangle-exclamation"></i>
                            </div>
                            <h3>
                                <?= e(trim($ch)) ?>
                            </h3>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </section>
<?php endif; ?>

<?php if (!empty($solution_list)): ?>
    <section class="section">
        <div class="container">
            <div class="section-heading text-center reveal">
                <h2>Our Solutions</h2>
            </div>
            <div class="row g-4">
                <?php foreach ($solution_list as $idx => $sol): ?>
                    <div class="col-md-6">
                        <div class="service-card reveal" data-delay="<?= $idx * 60 ?>">
                            <div class="icon-wrap <?= $colors[$idx % 6] ?>"><i class="fa-solid fa-circle-check"></i></div>
                            <h3>
                                <?= e(trim($sol)) ?>
                            </h3>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </section>
<?php endif; ?>

<?php if (!empty($services)): ?>
    <section class="section section--alt">
        <div class="container">
            <div class="section-heading text-center reveal">
                <h2>Services for
                    <?= e($industry['title']) ?>
                </h2>
            </div>
            <div class="row g-4">
                <?php foreach (array_slice($services, 0, 6) as $idx => $s): ?>
                    <div class="col-md-6 col-lg-4">
                        <div class="service-card reveal" data-delay="<?= $idx * 60 ?>">
                            <div class="icon-wrap <?= $colors[$idx % 6] ?>"><i
                                    class="<?= e($s['icon_class'] ?? 'fa-solid fa-gear') ?>"></i></div>
                            <h3>
                                <?= e($s['title']) ?>
                            </h3>
                            <a href="<?= url_for('service_detail', ['slug' => $s['slug']]) ?>"
                                class="card-link stretched-link">Learn more <i class="fa-solid fa-arrow-right"></i></a>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </section>
<?php endif; ?>

<?php if (!empty($other_industries)): ?>
    <section class="section">
        <div class="container">
            <div class="section-heading text-center reveal">
                <h2>Other Industries</h2>
            </div>
            <div class="row g-4">
                <?php foreach (array_slice($other_industries, 0, 4) as $idx => $oi): ?>
                    <div class="col-md-6 col-lg-3">
                        <div class="service-card reveal" data-delay="<?= $idx * 60 ?>">
                            <div class="icon-wrap <?= $colors[$idx % 6] ?>"><i
                                    class="<?= e($oi['icon_class'] ?? 'fa-solid fa-building') ?>"></i></div>
                            <h3>
                                <?= e($oi['title']) ?>
                            </h3>
                            <a href="<?= url_for('industry_detail', ['slug' => $oi['slug']]) ?>"
                                class="card-link stretched-link">View <i class="fa-solid fa-arrow-right"></i></a>
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
                <h2>Need
                    <?= e($industry['title']) ?> IT Support?
                </h2>
                <p>Contact us for a free assessment tailored to your industry.</p>
                <div class="cta-actions">
                    <a href="<?= url_for('contact') ?>?subject=<?= urlencode($industry['title'] . ' IT Support') ?>"
                        class="btn btn-secondary"><i class="fa-solid fa-calendar-check"></i> Schedule Consultation</a>
                </div>
            </div>
        </div>
    </div>
</section>