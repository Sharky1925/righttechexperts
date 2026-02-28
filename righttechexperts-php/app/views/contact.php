<?php
$page_title = 'Contact Us | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = 'Contact Right On Repair for IT support, technical repairs, or a free consultation. Serving Orange County businesses with fast, reliable service.';
$_phone_raw = preg_replace('/[\s()\-]/', '', $site_settings['phone'] ?? '');
?>
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <div class="section-label"><i class="fa-solid fa-envelope"></i> Contact</div>
            <h1>Get In Touch</h1>
            <p class="lead">Tell us what you need and we'll respond within one business day.</p>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="row g-5">
            <div class="col-lg-7">
                <div class="reveal">
                    <form method="POST" action="<?= url_for('contact') ?>" class="contact-form">
                        <?= csrf_input() ?>
                        <input type="hidden" name="subject" value="<?= e($_GET['subject'] ?? 'General Inquiry') ?>">
                        <div class="row g-3">
                            <div class="col-md-6"><label for="contact-name" class="form-label">Full Name *</label><input
                                    type="text" class="form-control" id="contact-name" name="name" required
                                    maxlength="200"></div>
                            <div class="col-md-6"><label for="contact-email" class="form-label">Email *</label><input
                                    type="email" class="form-control" id="contact-email" name="email" required
                                    maxlength="200"></div>
                            <div class="col-md-6"><label for="contact-phone" class="form-label">Phone</label><input
                                    type="tel" class="form-control" id="contact-phone" name="phone" maxlength="50">
                            </div>
                            <div class="col-12"><label for="contact-message" class="form-label">Message
                                    *</label><textarea class="form-control" id="contact-message" name="message" rows="5"
                                    required maxlength="5000"></textarea></div>
                            <div class="col-12"><button type="submit" class="btn btn-primary"><i
                                        class="fa-solid fa-paper-plane"></i> Send Message</button></div>
                        </div>
                    </form>
                </div>
            </div>
            <div class="col-lg-5">
                <div class="reveal">
                    <h3>Other Ways to Reach Us</h3>
                    <?php if (!empty($site_settings['phone'])): ?>
                        <p><i class="fa-solid fa-phone me-2"></i> <a href="tel:<?= e($_phone_raw) ?>">
                                <?= e($site_settings['phone']) ?>
                            </a></p>
                    <?php endif; ?>
                    <?php if (!empty($site_settings['email'])): ?>
                        <p><i class="fa-solid fa-envelope me-2"></i> <a href="mailto:<?= e($site_settings['email']) ?>">
                                <?= e($site_settings['email']) ?>
                            </a></p>
                    <?php endif; ?>
                    <?php if (!empty($site_settings['address'])): ?>
                        <p><i class="fa-solid fa-location-dot me-2"></i>
                            <?= e($site_settings['address']) ?>
                        </p>
                    <?php endif; ?>
                    <div class="mt-4">
                        <a href="<?= url_for('request_quote') ?>" class="btn btn-ghost"><i
                                class="fa-solid fa-file-lines"></i> Request a Quote</a>
                    </div>
                    <div class="mt-2">
                        <a href="<?= url_for('remote_support') ?>" class="btn btn-remote-support"><i
                                class="fa-solid fa-life-ring"></i> Remote Support</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>