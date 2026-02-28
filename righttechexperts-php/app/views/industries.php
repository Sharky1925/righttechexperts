<?php
$page_title = 'Industries We Serve | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = 'Industry-specific IT services for Orange County businesses. Healthcare, legal, construction, manufacturing, retail, and more.';
$colors = ['blue', 'purple', 'green', 'amber', 'rose', 'cyan'];
$hero = $cb['hero'] ?? [];
?>
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <div class="section-label"><i class="fa-solid fa-city"></i> Industries</div>
            <h1>
                <?= e($hero['title'] ?? 'Industries We Serve') ?>
            </h1>
            <p class="lead">
                <?= e($hero['lead'] ?? 'IT services tailored to how your industry works — security, compliance, and support aligned to your operations.') ?>
            </p>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="row g-4">
            <?php foreach ($industries as $idx => $ind): ?>
                <div class="col-md-6 col-lg-4">
                    <div class="service-card reveal" data-delay="<?= $idx * 60 ?>">
                        <div class="icon-wrap <?= $colors[$idx % 6] ?>"><i
                                class="<?= e($ind['icon_class'] ?? 'fa-solid fa-building') ?>"></i></div>
                        <h3>
                            <?= e($ind['title']) ?>
                        </h3>
                        <p>
                            <?= e(mb_substr($ind['description'] ?? '', 0, 120)) ?>
                        </p>
                        <a href="<?= url_for('industry_detail', ['slug' => $ind['slug']]) ?>"
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
                <h2>Don't See Your Industry?</h2>
                <p>We work with businesses across all sectors. Contact us to discuss how we can support your specific
                    needs.</p>
                <div class="cta-actions">
                    <a href="<?= url_for('contact') ?>" class="btn btn-secondary"><i class="fa-solid fa-envelope"></i>
                        Contact Us</a>
                    <a href="<?= url_for('services') ?>" class="btn btn-ghost btn-ghost-light"><i
                            class="fa-solid fa-grid-2"></i> View Services</a>
                </div>
            </div>
        </div>
    </div>
</section>