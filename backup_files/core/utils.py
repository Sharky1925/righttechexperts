import ipaddress
import json
import re
from datetime import datetime, timezone

from django.http import HttpRequest

from public.models import ContentBlock

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def utc_now_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def clean_text(value, max_length=255):
    return (value or '').strip()[:max_length]


def escape_like(value):
    return str(value or '').replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def is_valid_email(value):
    return bool(EMAIL_RE.match(value or ''))


def normalized_ip(value):
    candidate = (value or '').split(',', 1)[0].strip()
    if not candidate:
        return ''
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return ''


def get_request_ip(request: HttpRequest):
    remote_ip = normalized_ip(getattr(request, 'META', {}).get('REMOTE_ADDR') if request else '')
    return remote_ip or 'unknown'


def get_page_content(page):
    blocks = ContentBlock.objects.filter(page=page)
    result = {}
    for block in blocks:
        try:
            result[block.section] = json.loads(block.content)
        except (json.JSONDecodeError, TypeError):
            result[block.section] = {}
    return result
