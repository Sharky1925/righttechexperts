<?php
$page_title = 'Remote Support | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = 'Get remote IT support from Right On Repair. Submit a support ticket and our technicians will connect to resolve your issue fast.';
?>
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <div class="section-label"><i class="fa-solid fa-life-ring"></i> Support</div>
            <h1>Remote Support</h1>
            <p class="lead">Submit a support request and our team will get back to you quickly. For urgent issues, call
                us directly.</p>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="row g-5">
            <div class="col-lg-7">
                <div class="reveal">
                    <h2>Create Support Ticket</h2>
                    <form method="POST" action="<?= url_for('remote_support') ?>" class="contact-form">
                        <?= csrf_input() ?>
                        <div class="row g-3">
                            <div class="col-md-6"><label for="rs-name" class="form-label">Full Name *</label><input
                                    type="text" class="form-control" id="rs-name" name="full_name" required
                                    maxlength="200"></div>
                            <div class="col-md-6"><label for="rs-email" class="form-label">Email *</label><input
                                    type="email" class="form-control" id="rs-email" name="email" required
                                    maxlength="200"></div>
                            <div class="col-md-6"><label for="rs-company" class="form-label">Company</label><input
                                    type="text" class="form-control" id="rs-company" name="company" maxlength="200">
                            </div>
                            <div class="col-md-6"><label for="rs-phone" class="form-label">Phone</label><input
                                    type="tel" class="form-control" id="rs-phone" name="phone" maxlength="50"></div>
                            <div class="col-12"><label for="rs-issue" class="form-label">Issue Description
                                    *</label><textarea class="form-control" id="rs-issue" name="issue_description"
                                    rows="5" required maxlength="5000"
                                    placeholder="Describe your issue in detail..."></textarea></div>
                            <div class="col-12"><button type="submit" class="btn btn-primary"><i
                                        class="fa-solid fa-ticket"></i> Submit Ticket</button></div>
                        </div>
                    </form>
                </div>
            </div>
            <div class="col-lg-5">
                <div class="reveal">
                    <h3>Already Have a Ticket?</h3>
                    <p>Track your existing ticket by number:</p>
                    <form method="GET" action="<?= url_for('ticket_search') ?>" class="d-flex gap-2 mb-4">
                        <input type="text" class="form-control" name="ticket_number" placeholder="e.g. RT-A1B2C3D4"
                            maxlength="40">
                        <button type="submit" class="btn btn-ghost"><i class="fa-solid fa-magnifying-glass"></i>
                            Track</button>
                    </form>
                    <h3>Need Immediate Help?</h3>
                    <?php if (!empty($site_settings['phone'])): ?>
                        <p><i class="fa-solid fa-phone me-2"></i> <a
                                href="tel:<?= e(preg_replace('/[\s()\-]/', '', $site_settings['phone'])) ?>">
                                <?= e($site_settings['phone']) ?>
                            </a></p>
                    <?php endif; ?>
                    <?php if (!empty($site_settings['email'])): ?>
                        <p><i class="fa-solid fa-envelope me-2"></i> <a href="mailto:<?= e($site_settings['email']) ?>">
                                <?= e($site_settings['email']) ?>
                            </a></p>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>
</section>