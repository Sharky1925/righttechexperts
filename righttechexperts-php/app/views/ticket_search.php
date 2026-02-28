<?php
$page_title = 'Track Support Ticket | ' . ($site_settings['company_name'] ?? 'Right On Repair');
$meta_description = 'Track your support ticket status with Right On Repair.';
?>
<section class="hero hero--inner">
    <div class="container">
        <div class="hero-inner-content reveal">
            <div class="section-label"><i class="fa-solid fa-ticket"></i> Ticket Tracker</div>
            <h1>Track Your Ticket</h1>
            <p class="lead">Enter your ticket number to check the status of your support request.</p>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="reveal">
                    <form method="GET" action="<?= url_for('ticket_search') ?>" class="d-flex gap-2 mb-4">
                        <input type="text" class="form-control form-control-lg" name="ticket_number"
                            value="<?= e($ticket_number ?? '') ?>" placeholder="e.g. RT-A1B2C3D4" maxlength="40">
                        <button type="submit" class="btn btn-primary btn-lg"><i
                                class="fa-solid fa-magnifying-glass"></i> Search</button>
                    </form>

                    <?php if (!empty($ticket_number) && $ticket): ?>
                        <div class="service-card">
                            <h3>Ticket #
                                <?= e($ticket['ticket_number']) ?>
                            </h3>
                            <div class="d-flex gap-3 flex-wrap mb-3">
                                <span class="chip chip--active"><i class="fa-solid fa-circle-info"></i> Status:
                                    <?= e(ucfirst(str_replace('_', ' ', $ticket['status'] ?? 'Unknown'))) ?>
                                </span>
                                <?php if (!empty($ticket['priority'])): ?>
                                    <span class="chip"><i class="fa-solid fa-flag"></i> Priority:
                                        <?= e(ucfirst($ticket['priority'])) ?>
                                    </span>
                                <?php endif; ?>
                                <?php if (!empty($ticket['created_at'])): ?>
                                    <span class="chip"><i class="fa-solid fa-calendar"></i>
                                        <?= e(date('M j, Y', strtotime($ticket['created_at']))) ?>
                                    </span>
                                <?php endif; ?>
                            </div>
                            <p><strong>Subject:</strong>
                                <?= e($ticket['subject'] ?? '') ?>
                            </p>
                            <p>
                                <?= e($ticket['details'] ?? '') ?>
                            </p>

                            <?php if (!empty($events)): ?>
                                <hr>
                                <h4>Timeline</h4>
                                <?php foreach ($events as $ev): ?>
                                    <div class="mb-3 p-3"
                                        style="border-left:3px solid var(--accent-blue);background:var(--surface-primary);border-radius:var(--radius-sm)">
                                        <small class="text-muted">
                                            <?= e(date('M j, Y g:i A', strtotime($ev['created_at'] ?? 'now'))) ?>
                                        </small>
                                        <p class="mb-0">
                                            <?= e($ev['description'] ?? $ev['event_type'] ?? '') ?>
                                        </p>
                                    </div>
                                <?php endforeach; ?>
                            <?php endif; ?>
                        </div>

                    <?php elseif (!empty($ticket_number)): ?>
                        <div class="alert alert-modern alert-warning">
                            <i class="fa-solid fa-circle-exclamation"></i> No ticket found with number "<strong>
                                <?= e($ticket_number) ?>
                            </strong>". Please check the number and try again.
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>
</section>