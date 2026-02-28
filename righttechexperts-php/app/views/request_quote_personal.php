<?php
$page_title = 'Personal Repair Quote | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = 'Request a personal device repair quote. Fast laptops, phones, tablets, and desktop repairs in Orange County.';
?>
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <div class="section-label"><i class="fa-solid fa-laptop-medical"></i> Repair Quote</div>
            <h1>Personal Device Repair Quote</h1>
            <p class="lead">Tell us about your device issue and we'll get back to you with a repair estimate.</p>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="reveal">
                    <form method="POST" action="<?= url_for('request_quote_personal') ?>" class="contact-form">
                        <?= csrf_input() ?>
                        <div class="row g-3">
                            <div class="col-md-6"><label for="pq-name" class="form-label">Full Name *</label><input
                                    type="text" class="form-control" id="pq-name" name="name" required maxlength="200">
                            </div>
                            <div class="col-md-6"><label for="pq-email" class="form-label">Email *</label><input
                                    type="email" class="form-control" id="pq-email" name="email" required
                                    maxlength="200"></div>
                            <div class="col-md-6"><label for="pq-phone" class="form-label">Phone</label><input
                                    type="tel" class="form-control" id="pq-phone" name="phone" maxlength="50"></div>
                            <div class="col-md-6"><label for="pq-device" class="form-label">Device Type</label>
                                <select class="form-select" id="pq-device" name="device_type">
                                    <option value="">Select device…</option>
                                    <option value="Laptop">Laptop</option>
                                    <option value="Desktop">Desktop</option>
                                    <option value="Phone">Phone</option>
                                    <option value="Tablet">Tablet</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>
                            <div class="col-12"><label for="pq-message" class="form-label">Describe the Issue
                                    *</label><textarea class="form-control" id="pq-message" name="message" rows="5"
                                    required maxlength="5000"
                                    placeholder="What's happening with your device? When did the issue start?"></textarea>
                            </div>
                            <div class="col-12"><button type="submit" class="btn btn-primary"><i
                                        class="fa-solid fa-paper-plane"></i> Submit Repair Quote</button></div>
                        </div>
                    </form>
                    <p class="text-center mt-3"><a href="<?= url_for('request_quote') ?>">← Need a business IT quote
                            instead?</a></p>
                </div>
            </div>
        </div>
    </div>
</section>