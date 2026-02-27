from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from django.contrib import messages

from acp.models import AcpAuditEvent
from admin_panel.views.content import format_datetime_local, workflow_status_badge, workflow_status_label
from core.constants import USER_ROLE_CHOICES, USER_ROLE_LABELS, WORKFLOW_DRAFT, WORKFLOW_STATUSES, normalize_workflow_status
from core.utils import clean_text, get_request_ip, utc_now_naive


DEFAULT_ENVIRONMENT = 'development'


def workflow_context():
    return {
        'workflow_options': WORKFLOW_STATUSES,
        'workflow_status_label': workflow_status_label,
        'workflow_status_badge': workflow_status_badge,
        'format_datetime_local': format_datetime_local,
    }


def role_context():
    return {
        'role_options': USER_ROLE_CHOICES,
        'role_labels': USER_ROLE_LABELS,
    }


def parse_datetime_local(value: Any):
    raw = str(value or '').strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw, '%Y-%m-%dT%H:%M')
    except ValueError:
        return None


def normalize_status(value: Any):
    return normalize_workflow_status(value, default=WORKFLOW_DRAFT)


def parse_json_text(raw: Any, *, expect: str = 'any'):
    source = str(raw or '').strip()
    if not source:
        source = '{}' if expect == 'dict' else '[]' if expect == 'list' else '{}'
    try:
        loaded = json.loads(source)
    except (TypeError, ValueError):
        return None, f'Invalid JSON ({expect}).'

    if expect == 'dict' and not isinstance(loaded, dict):
        return None, 'JSON must be an object.'
    if expect == 'list' and not isinstance(loaded, list):
        return None, 'JSON must be an array.'
    return source, ''


def load_json(raw: Any, fallback):
    try:
        data = json.loads(raw or '')
    except (TypeError, ValueError):
        return fallback
    if isinstance(fallback, dict) and isinstance(data, dict):
        return data
    if isinstance(fallback, list) and isinstance(data, list):
        return data
    return fallback


def safe_int(value: Any, default=0, *, min_value=None, max_value=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if min_value is not None:
        parsed = max(min_value, parsed)
    if max_value is not None:
        parsed = min(max_value, parsed)
    return parsed


def maybe_mark_published(target, status, scheduled_publish_at):
    now = utc_now_naive()
    if status == 'published':
        if not scheduled_publish_at or scheduled_publish_at <= now:
            target.published_at = now
    return target


def write_audit(
    request,
    *,
    domain: str,
    action: str,
    entity_type: str,
    entity_id: Any,
    before_json: str = '',
    after_json: str = '',
    environment: str = DEFAULT_ENVIRONMENT,
):
    try:
        AcpAuditEvent.objects.create(
            domain=clean_text(domain, 50),
            action=clean_text(action, 50),
            entity_type=clean_text(entity_type, 60),
            entity_id=clean_text(str(entity_id or ''), 120),
            before_json=before_json or '',
            after_json=after_json or '',
            actor_user_id=getattr(request.user, 'id', None),
            actor_username=clean_text(getattr(request.user, 'username', 'system'), 120) or 'system',
            actor_ip=get_request_ip(request),
            actor_user_agent=clean_text(request.META.get('HTTP_USER_AGENT', ''), 320),
            environment=clean_text(environment, 40) or DEFAULT_ENVIRONMENT,
            created_at=utc_now_naive(),
        )
    except Exception:
        return


def flash_json_error(request, field_label='JSON'):
    messages.error(request, f'{field_label} is invalid.')

