<?php
$page_title = e($article['title'] ?? 'Article') . ' | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = mb_substr(strip_tags($article['content'] ?? ''), 0, 220);
?>
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <h1>
                <?= e($article['title'] ?? '') ?>
            </h1>
            <?php if (!empty($article['created_at'])): ?>
                <p class="text-muted">
                    <?= e(date('F j, Y', strtotime($article['created_at']))) ?>
                </p>
            <?php endif; ?>
        </div>
    </div>
</section>
<section class="section">
    <div class="container">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <article class="reveal">
                    <?= $article['content'] ?? '' ?>
                </article>
            </div>
        </div>
    </div>
</section>