<?php
$page_title = e($page['title'] ?? 'Page') . ' | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = mb_substr(strip_tags($page['content'] ?? ''), 0, 220);
?>
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <h1>
                <?= e($page['title'] ?? '') ?>
            </h1>
        </div>
    </div>
</section>
<section class="section">
    <div class="container">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <article class="reveal">
                    <?= $page['content'] ?? '' ?>
                </article>
            </div>
        </div>
    </div>
</section>