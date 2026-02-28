<?php
$page_title = 'Blog | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = 'IT insights, cybersecurity tips, and technology guides from Right On Repair — your Orange County IT partner.';
?>
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <div class="section-label"><i class="fa-solid fa-blog"></i> Blog</div>
            <h1>IT Insights & Guides</h1>
            <p class="lead">Technology tips, cybersecurity best practices, and business IT advice.</p>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <?php if (!empty($categories)): ?>
            <div class="chip-list reveal" style="margin-bottom:2rem">
                <a href="<?= url_for('blog') ?>" class="chip <?= empty($current_category) ? 'chip--active' : '' ?>">All</a>
                <?php foreach ($categories as $cat): ?>
                    <a href="<?= url_for('blog') ?>?category=<?= urlencode($cat['slug']) ?>"
                        class="chip <?= $current_category === $cat['slug'] ? 'chip--active' : '' ?>">
                        <?= e($cat['name']) ?>
                    </a>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>

        <?php if (!empty($posts)): ?>
            <div class="row g-4">
                <?php foreach ($posts as $idx => $p): ?>
                    <div class="col-md-6 col-lg-4">
                        <div class="service-card reveal" data-delay="<?= $idx * 60 ?>">
                            <h3>
                                <?= e($p['title']) ?>
                            </h3>
                            <p class="text-muted" style="font-size:.85rem">
                                <?= e(date('M j, Y', strtotime($p['created_at'] ?? 'now'))) ?>
                            </p>
                            <p>
                                <?= e(mb_substr(strip_tags($p['content'] ?? $p['excerpt'] ?? ''), 0, 120)) ?>…
                            </p>
                            <a href="<?= url_for('post', ['slug' => $p['slug']]) ?>" class="card-link stretched-link">Read more
                                <i class="fa-solid fa-arrow-right"></i></a>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>

            <!-- Pagination -->
            <?php if ($total_pages > 1): ?>
                <nav class="mt-5 d-flex justify-content-center" aria-label="Blog pagination">
                    <ul class="pagination">
                        <?php if ($page > 1): ?>
                            <li class="page-item"><a class="page-link"
                                    href="<?= url_for('blog') ?>?page=<?= $page - 1 ?><?= $current_category ? '&category=' . urlencode($current_category) : '' ?>">←
                                    Prev</a></li>
                        <?php endif; ?>
                        <?php for ($i = max(1, $page - 2); $i <= min($total_pages, $page + 2); $i++): ?>
                            <li class="page-item <?= $i === $page ? 'active' : '' ?>"><a class="page-link"
                                    href="<?= url_for('blog') ?>?page=<?= $i ?><?= $current_category ? '&category=' . urlencode($current_category) : '' ?>">
                                    <?= $i ?>
                                </a></li>
                        <?php endfor; ?>
                        <?php if ($page < $total_pages): ?>
                            <li class="page-item"><a class="page-link"
                                    href="<?= url_for('blog') ?>?page=<?= $page + 1 ?><?= $current_category ? '&category=' . urlencode($current_category) : '' ?>">Next
                                    →</a></li>
                        <?php endif; ?>
                    </ul>
                </nav>
            <?php endif; ?>
        <?php else: ?>
            <div class="text-center reveal">
                <p>No posts found.</p>
            </div>
        <?php endif; ?>
    </div>
</section>