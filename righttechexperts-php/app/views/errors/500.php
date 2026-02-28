<?php
$page_title = 'Server Error | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_robots = 'noindex, nofollow';
?>
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal text-center">
            <h1 style="font-size:5rem;opacity:.3">500</h1>
            <h2>Something Went Wrong</h2>
            <p class="lead">We encountered an unexpected error. Please try again or contact us directly.</p>
            <div class="hero-buttons" style="justify-content:center">
                <a href="<?= url_for('index') ?>" class="btn btn-primary"><i class="fa-solid fa-home"></i> Go Home</a>
                <a href="<?= url_for('contact') ?>" class="btn btn-ghost"><i class="fa-solid fa-envelope"></i> Contact
                    Us</a>
            </div>
        </div>
    </div>
</section>