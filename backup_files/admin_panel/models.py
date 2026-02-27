import re

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import check_password as django_check_password
from django.contrib.auth.hashers import make_password
from django.db import models

from core.constants import ROLE_ADMIN, ROLE_DEFAULT, ROLE_OWNER, USER_ROLE_CHOICES, USER_ROLE_LABELS, normalize_user_role
from core.hashers import WerkzeugPBKDF2SHA256PasswordHasher

SUPPORT_TICKET_NUMBER_SANITIZER_RE = re.compile(r'[^A-Z0-9-]+')
LEGACY_WERKZEUG_PBKDF2_PREFIX = 'pbkdf2:sha256:'


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        user = self.model(username=username, email=self.normalize_email(email or ''), **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', ROLE_OWNER)
        return self.create_user(username, email=email, password=password, **extra_fields)


class User(AbstractBaseUser):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=80, unique=True)
    email = models.CharField(max_length=120, unique=True)
    password = models.CharField(max_length=256, db_column='password_hash')
    role = models.CharField(max_length=30, default=ROLE_DEFAULT)
    created_at = models.DateTimeField(blank=True, null=True)

    # Remove AbstractBaseUser DB field that does not exist in legacy table.
    last_login = None

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        db_table = 'user'
        managed = False

    @property
    def role_key(self):
        return normalize_user_role(self.role, default=ROLE_DEFAULT)

    @property
    def role_label(self):
        return USER_ROLE_LABELS.get(self.role_key, USER_ROLE_LABELS[ROLE_DEFAULT])

    @property
    def is_staff(self):
        return self.role_key in {ROLE_OWNER, ROLE_ADMIN}

    @property
    def is_active(self):
        return True

    def has_permission(self, permission):
        from core.constants import ROLE_PERMISSIONS

        return permission in ROLE_PERMISSIONS.get(self.role_key, ROLE_PERMISSIONS[ROLE_DEFAULT])

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    def can_assign_role(self, role):
        target = normalize_user_role(role, default=ROLE_DEFAULT)
        if self.role_key == ROLE_OWNER:
            return target in USER_ROLE_CHOICES
        if self.role_key != ROLE_ADMIN:
            return False
        return target in USER_ROLE_CHOICES and target != ROLE_OWNER

    def set_password(self, raw_password):
        self.password = make_password(raw_password, hasher='pbkdf2_sha256')

    def check_password(self, raw_password):
        encoded = self.password or ''
        if encoded.startswith(LEGACY_WERKZEUG_PBKDF2_PREFIX):
            return WerkzeugPBKDF2SHA256PasswordHasher().verify(raw_password, encoded)
        return django_check_password(raw_password, encoded)


class Media(models.Model):
    id = models.BigAutoField(primary_key=True)
    filename = models.CharField(max_length=300)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField(blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    alt_text = models.CharField(max_length=300, blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    folder = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'media'
        managed = False


class ContactSubmission(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=300, blank=True, null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False, null=True)
    lead_status = models.CharField(max_length=30, blank=True, null=True)
    lead_notes = models.TextField(blank=True, null=True)
    source_page = models.CharField(max_length=300, blank=True, null=True)
    utm_source = models.CharField(max_length=200, blank=True, null=True)
    utm_medium = models.CharField(max_length=200, blank=True, null=True)
    utm_campaign = models.CharField(max_length=200, blank=True, null=True)
    referrer_url = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'contact_submission'
        managed = False


class SupportClient(models.Model):
    id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, unique=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    password_hash = models.CharField(max_length=256)
    created_at = models.DateTimeField(blank=True, null=True)
    last_login_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'support_client'
        managed = False

    def set_password(self, password):
        self.password_hash = make_password(password, hasher='pbkdf2_sha256')

    def check_password(self, password):
        encoded = self.password_hash or ''
        if encoded.startswith(LEGACY_WERKZEUG_PBKDF2_PREFIX):
            return WerkzeugPBKDF2SHA256PasswordHasher().verify(password, encoded)
        return django_check_password(password, encoded)


class SupportTicket(models.Model):
    id = models.BigAutoField(primary_key=True)
    ticket_number = models.CharField(max_length=24, unique=True)
    client = models.ForeignKey(SupportClient, db_column='client_id', on_delete=models.DO_NOTHING)
    subject = models.CharField(max_length=300)
    service_slug = models.CharField(max_length=200, blank=True, null=True)
    priority = models.CharField(max_length=20)
    status = models.CharField(max_length=30)
    details = models.TextField()
    internal_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'support_ticket'
        managed = False


class SupportTicketEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    ticket = models.ForeignKey(SupportTicket, db_column='ticket_id', on_delete=models.DO_NOTHING)
    event_type = models.CharField(max_length=40)
    message = models.TextField(blank=True, null=True)
    actor_type = models.CharField(max_length=30)
    actor_name = models.CharField(max_length=200)
    actor_user = models.ForeignKey(User, db_column='actor_user_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    actor_client = models.ForeignKey(SupportClient, db_column='actor_client_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    status_from = models.CharField(max_length=30, blank=True, null=True)
    status_to = models.CharField(max_length=30, blank=True, null=True)
    stage_from = models.CharField(max_length=20, blank=True, null=True)
    stage_to = models.CharField(max_length=20, blank=True, null=True)
    metadata_json = models.TextField(default='{}')
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'support_ticket_event'
        managed = False


class SupportTicketEmailVerification(models.Model):
    id = models.BigAutoField(primary_key=True)
    ticket = models.ForeignKey(SupportTicket, db_column='ticket_id', on_delete=models.DO_NOTHING)
    requester_email = models.CharField(max_length=200)
    token_hash = models.CharField(max_length=64, unique=True)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(blank=True, null=True)
    last_sent_at = models.DateTimeField()
    send_count = models.IntegerField(default=1)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'support_ticket_email_verification'
        managed = False


class AuthRateLimitBucket(models.Model):
    id = models.BigAutoField(primary_key=True)
    scope = models.CharField(max_length=80)
    ip = models.CharField(max_length=64)
    count = models.IntegerField(default=0)
    reset_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'auth_rate_limit_bucket'
        managed = False


class SecurityEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    event_type = models.CharField(max_length=40)
    scope = models.CharField(max_length=80)
    ip = models.CharField(max_length=64)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    user_agent = models.CharField(max_length=300, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'security_event'
        managed = False


class NotificationPreference(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.DO_NOTHING)
    event_type = models.CharField(max_length=60)
    channel = models.CharField(max_length=20)
    is_enabled = models.BooleanField(default=True, null=True)

    class Meta:
        db_table = 'notification_preference'
        managed = False


def normalize_ticket_number(value):
    candidate = (value or '').strip().upper()[:40]
    return SUPPORT_TICKET_NUMBER_SANITIZER_RE.sub('', candidate)
