<?php
/**
 * Support Controller
 * Converts public/views/support.py — remote support ticket creation
 */

class SupportController
{
    public static function remote_support_submit(): void
    {
        if (!verify_csrf()) {
            flash('Invalid form submission.', 'danger');
            header('Location: ' . url_for('remote_support'));
            exit;
        }

        $full_name = trim(mb_substr($_POST['full_name'] ?? '', 0, 200));
        $email = trim(mb_substr($_POST['email'] ?? '', 0, 200));
        $company = trim(mb_substr($_POST['company'] ?? '', 0, 200));
        $phone = trim(mb_substr($_POST['phone'] ?? '', 0, 50));
        $issue = trim(mb_substr($_POST['issue_description'] ?? '', 0, 5000));

        if (!$full_name || !$email || !$issue) {
            flash('Please fill in all required fields.', 'danger');
            header('Location: ' . url_for('remote_support'));
            exit;
        }

        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            flash('Please provide a valid email address.', 'danger');
            header('Location: ' . url_for('remote_support'));
            exit;
        }

        // Find or create support client
        $client = db_query_one("SELECT * FROM support_client WHERE email = ?", [$email]);
        if (!$client) {
            $client_id = db_insert('support_client', [
                'full_name' => $full_name,
                'email' => $email,
                'company' => $company,
                'phone' => $phone,
                'password_hash' => password_hash(bin2hex(random_bytes(16)), PASSWORD_DEFAULT),
                'created_at' => gmdate('Y-m-d H:i:s'),
            ]);
        } else {
            $client_id = $client['id'];
        }

        // Generate ticket number
        $ticket_number = 'RT-' . strtoupper(bin2hex(random_bytes(4)));

        db_insert('support_ticket', [
            'ticket_number' => $ticket_number,
            'client_id' => $client_id,
            'subject' => mb_substr($issue, 0, 200),
            'details' => $issue,
            'status' => 'open',
            'priority' => 'normal',
            'created_at' => gmdate('Y-m-d H:i:s'),
        ]);

        flash("Your support ticket has been created! Ticket number: {$ticket_number}", 'success');
        header('Location: ' . url_for('remote_support'));
        exit;
    }
}
