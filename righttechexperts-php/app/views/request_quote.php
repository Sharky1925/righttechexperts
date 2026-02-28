<?php
$page_title = 'Request a Quote | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = 'Request a free business IT quote from Right On Repair. Managed IT, cybersecurity, cloud, and development services for Orange County businesses.';
?>
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <div class="section-label"><i class="fa-solid fa-file-lines"></i> Quote</div>
            <h1>Request a Business Quote</h1>
            <p class="lead">Tell us about your technology needs and we'll prepare a detailed proposal within 24 hours.
            </p>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="reveal">
                    <form method="POST" action="<?= url_for('request_quote') ?>" class="contact-form">
                        <?= csrf_input() ?>
                        <div class="row g-3">
                            <div class="col-md-6"><label for="quote-name" class="form-label">Full Name *</label><input
                                    type="text" class="form-control" id="quote-name" name="name" required
                                    maxlength="200"></div>
                            <div class="col-md-6"><label for="quote-email" class="form-label">Business Email
                                    *</label><input type="email" class="form-control" id="quote-email" name="email"
                                    required maxlength="200"></div>
                            <div class="col-md-6"><label for="quote-phone" class="form-label">Phone</label><input
                                    type="tel" class="form-control" id="quote-phone" name="phone" maxlength="50"></div>
                            <div class="col-md-6"><label for="quote-company" class="form-label">Company</label><input
                                    type="text" class="form-control" id="quote-company" name="company" maxlength="200">
                            </div>
                            <div class="col-12"><label for="quote-service" class="form-label">Service Type</label>
                                <select class="form-select" id="quote-service" name="service_type">
                                    <option value="">Select a service area…</option>
                                    <option value="Managed IT">Managed IT Services</option>
                                    <option value="Cybersecurity">Cybersecurity</option>
                                    <option value="Cloud Solutions">Cloud Solutions</option>
                                    <option value="Software Development">Software & Web Development</option>
                                    <option value="Technical Repair">Technical Repair</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>
                            <div class="col-12"><label for="quote-message" class="form-label">Project Details
                                    *</label><textarea class="form-control" id="quote-message" name="message" rows="5"
                                    required maxlength="5000"
                                    placeholder="Describe your needs, timeline, and any specific requirements..."></textarea>
                            </div>
                            <div class="col-12"><button type="submit" class="btn btn-primary"><i
                                        class="fa-solid fa-paper-plane"></i> Submit Quote Request</button></div>
                        </div>
                    </form>
                    <p class="text-center mt-3"><a href="<?= url_for('request_quote_personal') ?>">Looking for a
                            personal/device repair quote? →</a></p>
                </div>
            </div>
        </div>
    </div>
</section>