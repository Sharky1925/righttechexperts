<?php
$page_title = e($post['title']) . ' | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = mb_substr(strip_tags($post['content'] ?? $post['excerpt'] ?? ''), 0, 220);
?>
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <div class="section-label"><i class="fa-solid fa-blog"></i> <a href="<?= url_for('blog') ?>"
                    style="color:inherit;text-decoration:none">Blog</a></div>
            <h1>
                <?= e($post['title']) ?>
            </h1>
            <p class="text-muted">
                <?= e(date('F j, Y', strtotime($post['created_at'] ?? 'now'))) ?>
            </p>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <article class="reveal">
                    <?= $post['content'] ?? '' ?>
                </article>
            </div>
        </div>
    </div>
</section>

<?php if (!empty($recent_posts)): ?>
    <section class="section section--alt">
        <div class="container">
            <div class="section-heading text-center reveal">
                <h2>Recent Posts</h2>
            </div>
            <div class="row g-4">
                <?php foreach ($recent_posts as $idx => $rp): ?>
                    <div class="col-md-4">
                        <div class="service-card reveal" data-delay="<?= $idx * 60 ?>">
                            <h3>
                                <?= e($rp['title']) ?>
                            </h3>
                            <p class="text-muted" style="font-size:.85rem">
                                <?= e(date('M j, Y', strtotime($rp['created_at'] ?? 'now'))) ?>
                            </p>
                            <a href="<?= url_for('post', ['slug' => $rp['slug']]) ?>" class="card-link stretched-link">Read <i
                                    class="fa-solid fa-arrow-right"></i></a>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
    </section>
<?php endif; ?>