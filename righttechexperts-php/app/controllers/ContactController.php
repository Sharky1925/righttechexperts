<?php
/**
 * Contact Controller
 * Converts public/views/contact.py — form submissions
 */

class ContactController
{
    public static function contact_submit(): void
    {
        if (!verify_csrf()) {
            flash('Invalid form submission. Please try again.', 'danger');
            header('Location: ' . url_for('contact'));
            exit;
        }

        $name = trim(mb_substr($_POST['name'] ?? '', 0, 200));
        $email = trim(mb_substr($_POST['email'] ?? '', 0, 200));
        $phone = trim(mb_substr($_POST['phone'] ?? '', 0, 50));
        $subject = trim(mb_substr($_POST['subject'] ?? '', 0, 200));
        $message = trim(mb_substr($_POST['message'] ?? '', 0, 5000));

        if (!$name || !$email || !$message) {
            flash('Please fill in all required fields.', 'danger');
            header('Location: ' . url_for('contact'));
            exit;
        }

        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            flash('Please provide a valid email address.', 'danger');
            header('Location: ' . url_for('contact'));
            exit;
        }

        try {
            db_insert('contact_submission', [
                'name' => $name,
                'email' => $email,
                'phone' => $phone,
                'subject' => $subject,
                'message' => $message,
                'form_type' => 'contact',
                'ip_address' => $_SERVER['REMOTE_ADDR'] ?? '',
                'user_agent' => mb_substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 300),
                'created_at' => gmdate('Y-m-d H:i:s'),
            ]);
        } catch (Exception $e) {
            if (APP_DEBUG)
                error_log('Contact insert failed: ' . $e->getMessage());
        }

        flash('Your message has been sent successfully! We\'ll get back to you soon.', 'success');
        header('Location: ' . url_for('contact'));
        exit;
    }

    public static function request_quote_submit(): void
    {
        if (!verify_csrf()) {
            flash('Invalid form submission.', 'danger');
            header('Location: ' . url_for('request_quote'));
            exit;
        }

        $name = trim(mb_substr($_POST['name'] ?? '', 0, 200));
        $email = trim(mb_substr($_POST['email'] ?? '', 0, 200));
        $phone = trim(mb_substr($_POST['phone'] ?? '', 0, 50));
        $company = trim(mb_substr($_POST['company'] ?? '', 0, 200));
        $service_type = trim(mb_substr($_POST['service_type'] ?? '', 0, 200));
        $message = trim(mb_substr($_POST['message'] ?? '', 0, 5000));

        if (!$name || !$email || !$message) {
            flash('Please fill in all required fields.', 'danger');
            header('Location: ' . url_for('request_quote'));
            exit;
        }

        try {
            db_insert('contact_submission', [
                'name' => $name,
                'email' => $email,
                'phone' => $phone,
                'company' => $company,
                'subject' => "Quote Request: {$service_type}",
                'message' => $message,
                'form_type' => 'business_quote',
                'ip_address' => $_SERVER['REMOTE_ADDR'] ?? '',
                'user_agent' => mb_substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 300),
                'created_at' => gmdate('Y-m-d H:i:s'),
            ]);
        } catch (Exception $e) {
            if (APP_DEBUG)
                error_log('Quote insert failed: ' . $e->getMessage());
        }

        flash('Your quote request has been submitted! We\'ll respond within 24 hours.', 'success');
        header('Location: ' . url_for('request_quote'));
        exit;
    }

    public static function request_quote_personal_submit(): void
    {
        if (!verify_csrf()) {
            flash('Invalid form submission.', 'danger');
            header('Location: ' . url_for('request_quote_personal'));
            exit;
        }

        $name = trim(mb_substr($_POST['name'] ?? '', 0, 200));
        $email = trim(mb_substr($_POST['email'] ?? '', 0, 200));
        $phone = trim(mb_substr($_POST['phone'] ?? '', 0, 50));
        $device = trim(mb_substr($_POST['device_type'] ?? '', 0, 200));
        $message = trim(mb_substr($_POST['message'] ?? '', 0, 5000));

        if (!$name || !$email || !$message) {
            flash('Please fill in all required fields.', 'danger');
            header('Location: ' . url_for('request_quote_personal'));
            exit;
        }

        try {
            db_insert('contact_submission', [
                'name' => $name,
                'email' => $email,
                'phone' => $phone,
                'subject' => "Personal Quote: {$device}",
                'message' => $message,
                'form_type' => 'personal_quote',
                'ip_address' => $_SERVER['REMOTE_ADDR'] ?? '',
                'user_agent' => mb_substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 300),
                'created_at' => gmdate('Y-m-d H:i:s'),
            ]);
        } catch (Exception $e) {
            if (APP_DEBUG)
                error_log('Personal quote insert failed: ' . $e->getMessage());
        }

        flash('Your repair quote request has been submitted! We\'ll get back to you soon.', 'success');
        header('Location: ' . url_for('request_quote_personal'));
        exit;
    }
}
