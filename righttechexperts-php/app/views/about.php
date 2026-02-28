<?php
/**
 * About page — converted from app/templates/about.html
 */
$page_title = 'About Us | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = 'Learn about Right On Repair — your local Orange County IT services partner. Meet our team of experts committed to keeping your business technology running smoothly.';
$about = $cb['about'] ?? [];
$hero = $cb['hero'] ?? [];
$mission = $cb['mission'] ?? [];
$values = $cb['values'] ?? [];
$cta = $cb['cta'] ?? [];
?>

<!-- Hero -->
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <div class="section-label"><i class="fa-solid fa-users"></i> About</div>
            <h1>
                <?= e($hero['title'] ?? 'About Right On Repair') ?>
            </h1>
            <p class="lead">
                <?= e($hero['lead'] ?? 'Local IT expertise for Orange County businesses — from managed services to hands-on technical repair.') ?>
            </p>
        </div>
    </div>
</section>

<!-- Mission -->
<section class="section">
    <div class="container">
        <div class="section-heading text-center reveal">
            <h2>
                <?= e($mission['title'] ?? 'Our Mission') ?>
            </h2>
            <p>
                <?= e($mission['description'] ?? 'We provide reliable, transparent, and security-first IT services to small and mid-size businesses across Orange County.') ?>
            </p>
        </div>
    </div>
</section>

<!-- Values -->
<?php if (!empty($values['items'])): ?>
    <section class="section section--alt">
        <div class="container">
            <div class="section-heading text-center reveal">
                <h2>
                    <?= e($values['title'] ?? 'Our Values') ?>
                </h2>
            </div>
            <div class="row g-4">
                <?php $colors = ['blue', 'purple', 'green', 'amber', 'rose', 'cyan'];
                foreach ($values['items'] as $idx => $v): ?>
                    <div class="col-md-6 col-lg-4">
                        <div class="service-card reveal" data-delay="<?= $idx * 60 ?>">
                            <div class="icon-wrap <?= $colors[$idx % 6] ?>"><i
                                    class="<?= e($v['icon'] ?? 'fa-solid fa-star') ?>"></i></div>
                            <h3>
                                <?= e($v['title'] ?? '') ?>
                            </h3>
                            <p>
                                <?= e($v['description'] ?? '') ?>
                            </p>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </section>
<?php endif; ?>

<!-- Team -->
<?php if (!empty($team)): ?>
    <section class="section">
        <div class="container">
            <div class="section-heading text-center reveal">
                <div class="section-label"><i class="fa-solid fa-people-group"></i> Our Team</div>
                <h2>Meet the Team</h2>
            </div>
            <div class="row g-4">
                <?php foreach ($team as $idx => $member): ?>
                    <div class="col-md-6 col-lg-3">
                        <div class="service-card text-center reveal" data-delay="<?= $idx * 60 ?>">
                            <div class="author-avatar" style="width:64px;height:64px;font-size:24px;margin:0 auto 1rem">
                                <?= e(mb_substr($member['name'] ?? '?', 0, 1)) ?>
                            </div>
                            <h3>
                                <?= e($member['name'] ?? '') ?>
                            </h3>
                            <p class="text-muted">
                                <?= e($member['position'] ?? '') ?>
                            </p>
                            <?php if (!empty($member['bio'])): ?>
                                <p>
                                    <?= e(mb_substr($member['bio'], 0, 120)) ?>
                                </p>
                            <?php endif; ?>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </section>
<?php endif; ?>

<!-- CTA -->
<section class="section">
    <div class="container">
        <div class="cta-strip reveal">
            <div class="cta-inner">
                <h2>
                    <?= e($cta['title'] ?? 'Ready to Work With Us?') ?>
                </h2>
                <p>
                    <?= e($cta['subtitle'] ?? 'Get in touch for a free consultation. We\'ll assess your needs and build a plan that works.') ?>
                </p>
                <div class="cta-actions">
                    <a href="<?= url_for('contact') ?>?subject=Free+Consultation" class="btn btn-secondary"><i
                            class="fa-solid fa-calendar-check"></i> Schedule a Meeting</a>
                    <a href="<?= url_for('request_quote') ?>" class="btn btn-ghost btn-ghost-light"><i
                            class="fa-solid fa-file-lines"></i> Request a Quote</a>
                </div>
            </div>
        </div>
    </div>
</section>