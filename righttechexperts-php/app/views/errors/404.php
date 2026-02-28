<?php
$page_title = 'Page Not Found | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_robots = 'noindex, nofollow';
?>
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal text-center">
            <h1 style="font-size:5rem;opacity:.3">404</h1>
            <h2>Page Not Found</h2>
            <p class="lead">The page you're looking for doesn't exist or has been moved.</p>
            <div class="hero-buttons" style="justify-content:center">
                <a href="<?= url_for('index') ?>" class="btn btn-primary"><i class="fa-solid fa-home"></i> Go Home</a>
                <a href="<?= url_for('services') ?>" class="btn btn-ghost"><i class="fa-solid fa-grid-2"></i> View
                    Services</a>
                <a href="<?= url_for('contact') ?>" class="btn btn-ghost"><i class="fa-solid fa-envelope"></i> Contact
                    Us</a>
            </div>
        </div>
    </div>
</section>