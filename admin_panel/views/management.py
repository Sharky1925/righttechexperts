from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from admin_panel.decorators import permission_required
from admin_panel.models import User
from core.constants import ROLE_DEFAULT, USER_ROLE_CHOICES, USER_ROLE_LABELS, WORKFLOW_PUBLISHED
from core.utils import clean_text, utc_now_naive
from public.models import (
    Category,
    CmsArticle,
    CmsPage,
    Industry,
    MenuItem,
    Post,
    Service,
    SiteSetting,
    TeamMember,
    Testimonial,
)

VALID_MENU_LOCATIONS = {'header', 'footer', 'mobile'}
PASSWORD_COMPLEXITY_RE = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{10,}$')
GENERAL_SETTING_KEYS = [
    'company_name',
    'tagline',
    'footer_text',
    'phone',
    'email',
    'address',
    'facebook',
    'twitter',
    'linkedin',
    'meta_title',
    'meta_description',
    'custom_head_code',
    'custom_footer_code',
]
HEADLESS_SETTING_KEYS = [
    'headless_delivery_default_limit',
    'headless_delivery_max_limit',
    'headless_delivery_require_token',
    'headless_delivery_token',
    'headless_sync_enabled',
    'headless_sync_token',
    'headless_sync_max_items',
]


def _safe_int(value, default=0, min_value=None, max_value=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if min_value is not None:
        parsed = max(min_value, parsed)
    if max_value is not None:
        parsed = min(max_value, parsed)
    return parsed


def _coerce_ids(values):
    if not values:
        return []
    result = []
    seen = set()
    for value in values:
        for part in str(value or '').split(','):
            token = part.strip()
            if not token.isdigit():
                continue
            parsed = int(token)
            if parsed in seen:
                continue
            seen.add(parsed)
            result.append(parsed)
    return result


def _uploaded_path(upload, folder):
    suffix = Path(upload.name).suffix.lower()
    stem = slugify(Path(upload.name).stem)[:60] or 'upload'
    token = uuid4().hex[:8]
    rel_path = f'{folder}/{stem}-{token}{suffix}'
    abs_path = Path(settings.MEDIA_ROOT) / rel_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    with abs_path.open('wb') as out:
        for chunk in upload.chunks():
            out.write(chunk)
    return rel_path


def _set_setting(key, value):
    value = '' if value is None else str(value)
    SiteSetting.objects.update_or_create(key=key, defaults={'value': value})


def _settings_map(keys=None):
    query = SiteSetting.objects
    if keys:
        query = query.filter(key__in=keys)
    return {key: value for key, value in query.values_list('key', 'value')}


def _clear_site_cache():
    cache.clear()


def _unique_slug(model, seed, max_length, instance_id=None):
    base = slugify(seed or '')[:max_length] or 'item'
    candidate = base
    i = 2
    while model.objects.filter(slug=candidate).exclude(id=instance_id).exists():
        suffix = f'-{i}'
        candidate = f'{base[: max_length - len(suffix)]}{suffix}'
        i += 1
    return candidate


def _assignable_roles(user):
    roles = [role for role in USER_ROLE_CHOICES if user.can_assign_role(role)]
    if not roles:
        return [ROLE_DEFAULT]
    return roles


def _password_is_strong(password):
    return bool(PASSWORD_COMPLEXITY_RE.match(password or ''))


def _normalize_menu_location(value):
    candidate = clean_text(value or '', 20).lower()
    if candidate in VALID_MENU_LOCATIONS:
        return candidate
    return 'header'


@permission_required('content:manage')
def team(request):
    show_trash = bool((request.GET.get('trash') or '').strip())
    query = TeamMember.objects.order_by('sort_order', 'id')
    if show_trash:
        query = query.filter(is_trashed=True)
    else:
        query = query.filter(Q(is_trashed=False) | Q(is_trashed__isnull=True))
    return render(
        request,
        'admin/team.html',
        {
            'items': list(query),
            'bulk_url': '/admin/team/bulk',
        },
    )


def _save_team(request, item=None):
    target = item if item is not None else TeamMember()
    target.name = clean_text(request.POST.get('name', ''), 200)
    target.position = clean_text(request.POST.get('position', ''), 200)
    target.bio = request.POST.get('bio', '')
    target.linkedin = clean_text(request.POST.get('linkedin', ''), 300)
    target.sort_order = _safe_int(request.POST.get('sort_order'), default=0)
    if not target.name or not target.position:
        return None, 'Name and position are required.'

    upload = request.FILES.get('photo')
    if upload:
        target.photo = _uploaded_path(upload, folder='team')

    now = utc_now_naive()
    if not getattr(target, 'id', None):
        target.created_at = now
        target.is_trashed = False
        target.trashed_at = None
    target.save()
    return target, ''


@permission_required('content:manage')
def team_add(request):
    item = None
    if request.method == 'POST':
        item, error = _save_team(request)
        if item:
            messages.success(request, 'Team member created.')
            return redirect('admin:team_edit', id=item.id)
        messages.error(request, error)
    return render(request, 'admin/team_form.html', {'item': item})


@permission_required('content:manage')
def team_edit(request, id):
    item = get_object_or_404(TeamMember, id=id)
    if request.method == 'POST':
        updated, error = _save_team(request, item=item)
        if updated:
            messages.success(request, 'Team member updated.')
            return redirect('admin:team_edit', id=updated.id)
        messages.error(request, error)
    return render(request, 'admin/team_form.html', {'item': item})


@permission_required('content:manage')
def team_delete(request, id):
    if request.method != 'POST':
        return redirect('admin:team')
    item = get_object_or_404(TeamMember, id=id)
    if item.is_trashed:
        item.delete()
        messages.success(request, 'Team member permanently deleted.')
        return redirect('admin:team')
    item.is_trashed = True
    item.trashed_at = utc_now_naive()
    item.save(update_fields=['is_trashed', 'trashed_at'])
    messages.success(request, 'Team member moved to trash.')
    return redirect('admin:team')


@permission_required('content:manage')
def team_trash_restore(request, id):
    if request.method != 'POST':
        return redirect('admin:team')
    item = get_object_or_404(TeamMember, id=id)
    item.is_trashed = False
    item.trashed_at = None
    item.save(update_fields=['is_trashed', 'trashed_at'])
    messages.success(request, 'Team member restored.')
    return redirect('/admin/team?trash=1')


@permission_required('content:manage')
def team_bulk(request):
    if request.method != 'POST':
        return redirect('admin:team')
    action = clean_text(request.POST.get('action', ''), 20).lower()
    ids = _coerce_ids(request.POST.getlist('ids'))
    if not ids:
        messages.error(request, 'No team members selected.')
        return redirect('admin:team')
    query = TeamMember.objects.filter(id__in=ids)
    if action == 'delete':
        deleted, _ = query.delete()
        messages.success(request, f'Deleted {deleted} records.')
    elif action == 'trash':
        query.update(is_trashed=True, trashed_at=utc_now_naive())
        messages.success(request, f'Moved {len(ids)} records to trash.')
    else:
        query.update(is_trashed=False, trashed_at=None)
        messages.success(request, f'Updated {len(ids)} records.')
    return redirect('admin:team')


@permission_required('content:manage')
def testimonials(request):
    show_trash = bool((request.GET.get('trash') or '').strip())
    query = Testimonial.objects.order_by('-created_at', '-id')
    if show_trash:
        query = query.filter(is_trashed=True)
    else:
        query = query.filter(Q(is_trashed=False) | Q(is_trashed__isnull=True))
    return render(
        request,
        'admin/testimonials.html',
        {
            'items': list(query),
            'bulk_url': '/admin/testimonials/bulk',
        },
    )


def _save_testimonial(request, item=None):
    target = item if item is not None else Testimonial()
    target.client_name = clean_text(request.POST.get('client_name', ''), 200)
    target.company = clean_text(request.POST.get('company', ''), 200)
    target.content = request.POST.get('content', '')
    target.rating = _safe_int(request.POST.get('rating'), default=5, min_value=1, max_value=5)
    target.is_featured = bool(request.POST.get('is_featured'))
    if not target.client_name or not target.content:
        return None, 'Client name and content are required.'
    if not getattr(target, 'id', None):
        target.created_at = utc_now_naive()
        target.is_trashed = False
        target.trashed_at = None
    target.save()
    return target, ''


@permission_required('content:manage')
def testimonial_add(request):
    item = None
    if request.method == 'POST':
        item, error = _save_testimonial(request)
        if item:
            messages.success(request, 'Testimonial created.')
            return redirect('admin:testimonial_edit', id=item.id)
        messages.error(request, error)
    return render(request, 'admin/testimonial_form.html', {'item': item})


@permission_required('content:manage')
def testimonial_edit(request, id):
    item = get_object_or_404(Testimonial, id=id)
    if request.method == 'POST':
        updated, error = _save_testimonial(request, item=item)
        if updated:
            messages.success(request, 'Testimonial updated.')
            return redirect('admin:testimonial_edit', id=updated.id)
        messages.error(request, error)
    return render(request, 'admin/testimonial_form.html', {'item': item})


@permission_required('content:manage')
def testimonial_delete(request, id):
    if request.method != 'POST':
        return redirect('admin:testimonials')
    item = get_object_or_404(Testimonial, id=id)
    if item.is_trashed:
        item.delete()
        messages.success(request, 'Testimonial permanently deleted.')
        return redirect('admin:testimonials')
    item.is_trashed = True
    item.trashed_at = utc_now_naive()
    item.save(update_fields=['is_trashed', 'trashed_at'])
    messages.success(request, 'Testimonial moved to trash.')
    return redirect('admin:testimonials')


@permission_required('content:manage')
def testimonial_trash_restore(request, id):
    if request.method != 'POST':
        return redirect('admin:testimonials')
    item = get_object_or_404(Testimonial, id=id)
    item.is_trashed = False
    item.trashed_at = None
    item.save(update_fields=['is_trashed', 'trashed_at'])
    messages.success(request, 'Testimonial restored.')
    return redirect('/admin/testimonials?trash=1')


@permission_required('content:manage')
def testimonials_bulk(request):
    if request.method != 'POST':
        return redirect('admin:testimonials')
    action = clean_text(request.POST.get('action', ''), 20).lower()
    ids = _coerce_ids(request.POST.getlist('ids'))
    if not ids:
        messages.error(request, 'No testimonials selected.')
        return redirect('admin:testimonials')
    query = Testimonial.objects.filter(id__in=ids)
    if action == 'delete':
        deleted, _ = query.delete()
        messages.success(request, f'Deleted {deleted} records.')
    elif action == 'trash':
        query.update(is_trashed=True, trashed_at=utc_now_naive())
        messages.success(request, f'Moved {len(ids)} records to trash.')
    else:
        query.update(is_trashed=False, trashed_at=None)
        messages.success(request, f'Updated {len(ids)} records.')
    return redirect('admin:testimonials')


@permission_required('content:manage')
def categories(request):
    post_counts = {
        row['category_id']: row['total']
        for row in Post.objects.values('category_id').annotate(total=Count('id'))
    }
    items = list(Category.objects.order_by('name', 'id'))
    for cat in items:
        cat.post_count = post_counts.get(cat.id, 0)
    return render(request, 'admin/categories.html', {'items': items})


@permission_required('content:manage')
def category_add(request):
    if request.method != 'POST':
        return redirect('admin:categories')
    name = clean_text(request.POST.get('name', ''), 100)
    if not name:
        messages.error(request, 'Category name is required.')
        return redirect('admin:categories')
    slug = _unique_slug(Category, name, max_length=100)
    Category.objects.create(name=name, slug=slug)
    messages.success(request, 'Category created.')
    return redirect('admin:categories')


@permission_required('content:manage')
def category_edit(request, id):
    item = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        name = clean_text(request.POST.get('name', ''), 100)
        if not name:
            messages.error(request, 'Category name is required.')
            return render(request, 'admin/category_form.html', {'item': item})
        item.name = name
        item.slug = _unique_slug(Category, name, max_length=100, instance_id=item.id)
        item.save(update_fields=['name', 'slug'])
        messages.success(request, 'Category updated.')
        return redirect('admin:categories')
    return render(request, 'admin/category_form.html', {'item': item})


@permission_required('content:manage')
def category_delete(request, id):
    if request.method != 'POST':
        return redirect('admin:categories')
    item = get_object_or_404(Category, id=id)
    Post.objects.filter(category_id=item.id).update(category_id=None)
    item.delete()
    messages.success(request, 'Category deleted.')
    return redirect('admin:categories')


@permission_required('users:manage')
def users(request):
    items = list(User.objects.order_by('username', 'id'))
    return render(
        request,
        'admin/users.html',
        {
            'items': items,
            'role_labels': USER_ROLE_LABELS,
        },
    )


@permission_required('users:manage')
def user_add(request):
    assignable_roles = _assignable_roles(request.user)
    default_role = assignable_roles[0]
    if request.method == 'POST':
        username = clean_text(request.POST.get('username', ''), 80)
        email = clean_text(request.POST.get('email', ''), 120)
        role = clean_text(request.POST.get('role', default_role), 30).lower()
        password = request.POST.get('password', '')

        if not username or not email:
            messages.error(request, 'Username and email are required.')
        elif role not in assignable_roles:
            messages.error(request, 'You do not have permission to assign that role.')
        elif not _password_is_strong(password):
            messages.error(request, 'Password must be at least 10 characters with upper/lower/number/symbol.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                created_at=utc_now_naive(),
            )
            messages.success(request, 'Admin user created.')
            return redirect('admin:users')

    return render(
        request,
        'admin/user_form.html',
        {
            'user': None,
            'assignable_roles': assignable_roles,
            'default_role': default_role,
            'role_labels': USER_ROLE_LABELS,
        },
    )


@permission_required('users:manage')
def user_edit(request, id):
    item = get_object_or_404(User, id=id)
    assignable_roles = _assignable_roles(request.user)
    if item.role_key not in assignable_roles and item.id != request.user.id:
        assignable_roles.append(item.role_key)

    if request.method == 'POST':
        email = clean_text(request.POST.get('email', ''), 120)
        role = clean_text(request.POST.get('role', item.role_key), 30).lower()
        password = request.POST.get('password', '')
        if not email:
            messages.error(request, 'Email is required.')
        elif role not in assignable_roles:
            messages.error(request, 'You do not have permission to assign that role.')
        elif User.objects.filter(email=email).exclude(id=item.id).exists():
            messages.error(request, 'Email already exists.')
        elif password and not _password_is_strong(password):
            messages.error(request, 'Password must be at least 10 characters with upper/lower/number/symbol.')
        else:
            item.email = email
            item.role = role
            update_fields = ['email', 'role']
            if password:
                item.set_password(password)
                update_fields.append('password')
            item.save(update_fields=update_fields)
            messages.success(request, 'Admin user updated.')
            return redirect('admin:user_edit', id=item.id)

    return render(
        request,
        'admin/user_form.html',
        {
            'user': item,
            'assignable_roles': assignable_roles,
            'default_role': item.role_key,
            'role_labels': USER_ROLE_LABELS,
        },
    )


@permission_required('users:manage')
def user_delete(request, id):
    if request.method != 'POST':
        return redirect('admin:users')
    item = get_object_or_404(User, id=id)
    if item.id == request.user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('admin:users')
    item.delete()
    messages.success(request, 'Admin user deleted.')
    return redirect('admin:users')


@permission_required('settings:manage')
def settings_view(request):
    if request.method == 'POST':
        for key in GENERAL_SETTING_KEYS:
            _set_setting(key, request.POST.get(key, ''))
        _clear_site_cache()
        messages.success(request, 'Settings updated.')
        return redirect('admin:settings')
    settings_map = _settings_map(GENERAL_SETTING_KEYS)
    return render(request, 'admin/settings.html', {'settings': settings_map})


@permission_required('settings:manage')
def appearance(request):
    return redirect('admin:settings')


def _bool_like(value):
    return str(value or '').strip().lower() in {'1', 'true', 'yes', 'on'}


@permission_required('settings:manage')
def headless_hub(request):
    config_default_limit = _safe_int(getattr(settings, 'HEADLESS_DELIVERY_DEFAULT_LIMIT', 20), 20, 1, 500)
    config_max_limit = _safe_int(getattr(settings, 'HEADLESS_DELIVERY_MAX_LIMIT', 100), 100, 1, 1000)
    env_delivery_token = (getattr(settings, 'HEADLESS_DELIVERY_TOKEN', '') or '').strip()
    env_require_token = _bool_like(getattr(settings, 'HEADLESS_DELIVERY_REQUIRE_TOKEN', False))
    env_sync_token = (getattr(settings, 'HEADLESS_SYNC_TOKEN', '') or '').strip()
    env_sync_enabled = _bool_like(getattr(settings, 'HEADLESS_SYNC_ENABLED', False))
    env_sync_max_items = _safe_int(getattr(settings, 'HEADLESS_SYNC_MAX_ITEMS', 250), 250, 1, 5000)

    if request.method == 'POST':
        _set_setting(
            'headless_delivery_default_limit',
            str(_safe_int(request.POST.get('headless_delivery_default_limit'), config_default_limit, 1, 500)),
        )
        _set_setting(
            'headless_delivery_max_limit',
            str(_safe_int(request.POST.get('headless_delivery_max_limit'), config_max_limit, 1, 1000)),
        )
        _set_setting(
            'headless_delivery_require_token',
            '1' if request.POST.get('headless_delivery_require_token') else '0',
        )
        token_value = (request.POST.get('headless_delivery_token') or '').strip()
        if request.POST.get('clear_headless_delivery_token'):
            _set_setting('headless_delivery_token', '')
        elif token_value:
            _set_setting('headless_delivery_token', token_value)
        _clear_site_cache()
        messages.success(request, 'Headless settings updated.')
        return redirect('admin:headless_hub')

    settings_map = _settings_map(HEADLESS_SETTING_KEYS)
    site_delivery_token = (settings_map.get('headless_delivery_token') or '').strip()
    effective_delivery_token = site_delivery_token or env_delivery_token
    require_token = _bool_like(settings_map.get('headless_delivery_require_token')) or env_require_token
    default_limit = _safe_int(settings_map.get('headless_delivery_default_limit'), config_default_limit, 1, 500)
    max_limit = _safe_int(settings_map.get('headless_delivery_max_limit'), config_max_limit, 1, 1000)
    sync_enabled = _bool_like(settings_map.get('headless_sync_enabled')) or env_sync_enabled
    sync_token_configured = bool((settings_map.get('headless_sync_token') or '').strip() or env_sync_token)
    sync_max_items = _safe_int(settings_map.get('headless_sync_max_items'), env_sync_max_items, 1, 5000)

    base = f'{request.scheme}://{request.get_host()}'
    endpoints = [
        {'label': 'Delivery Index', 'path': '/api/delivery', 'url': f'{base}/api/delivery'},
        {'label': 'Headless Export', 'path': '/api/headless/export', 'url': f'{base}/api/headless/export'},
        {'label': 'Headless Sync', 'path': '/api/headless/sync', 'url': f'{base}/api/headless/sync'},
    ]

    try:
        from acp.models import AcpDashboardDocument, AcpPageDocument

        acp_pages_published = AcpPageDocument.objects.filter(status=WORKFLOW_PUBLISHED).count()
        acp_dashboards_published = AcpDashboardDocument.objects.filter(status=WORKFLOW_PUBLISHED).count()
    except Exception:
        acp_pages_published = 0
        acp_dashboards_published = 0

    counts = {
        'cms_pages_published': CmsPage.objects.filter(is_published=True).count(),
        'cms_articles_published': CmsArticle.objects.filter(is_published=True).count(),
        'services_published': Service.objects.filter(workflow_status=WORKFLOW_PUBLISHED).filter(
            Q(is_trashed=False) | Q(is_trashed__isnull=True)
        ).count(),
        'industries_published': Industry.objects.filter(workflow_status=WORKFLOW_PUBLISHED).filter(
            Q(is_trashed=False) | Q(is_trashed__isnull=True)
        ).count(),
        'posts_published': Post.objects.filter(workflow_status=WORKFLOW_PUBLISHED).filter(
            Q(is_trashed=False) | Q(is_trashed__isnull=True)
        ).count(),
        'acp_pages_published': acp_pages_published,
        'acp_dashboards_published': acp_dashboards_published,
    }
    quick_links = [
        {'label': 'Settings', 'href': '/admin/settings'},
        {'label': 'CMS Pages', 'href': '/admin/cms-pages'},
        {'label': 'CMS Articles', 'href': '/admin/cms-articles'},
        {'label': 'Services', 'href': '/admin/services'},
        {'label': 'Posts', 'href': '/admin/posts'},
    ]

    return render(
        request,
        'admin/headless_hub.html',
        {
            'delivery_auth_warning': require_token and not bool(effective_delivery_token),
            'require_token': require_token,
            'effective_delivery_token': effective_delivery_token,
            'default_limit': default_limit,
            'max_limit': max_limit,
            'sync_enabled': sync_enabled,
            'sync_token_configured': sync_token_configured,
            'sync_max_items': sync_max_items,
            'config_default_limit': config_default_limit,
            'config_max_limit': config_max_limit,
            'site_delivery_token': site_delivery_token,
            'env_delivery_token': env_delivery_token,
            'endpoints': endpoints,
            'counts': counts,
            'quick_links': quick_links,
        },
    )


def _cms_page_payload(request, item=None):
    return {
        'title': clean_text(
            request.POST.get('title', item.title if item else ''),
            200,
        ),
        'slug': clean_text(
            request.POST.get('slug', item.slug if item else ''),
            200,
        ),
        'content': request.POST.get('content', item.content if item else ''),
        'is_published': bool(request.POST.get('is_published')),
    }


def _cms_article_payload(request, item=None):
    return {
        'title': clean_text(
            request.POST.get('title', item.title if item else ''),
            220,
        ),
        'slug': clean_text(
            request.POST.get('slug', item.slug if item else ''),
            220,
        ),
        'excerpt': clean_text(
            request.POST.get('excerpt', item.excerpt if item else ''),
            600,
        ),
        'content': request.POST.get('content', item.content if item else ''),
        'is_published': bool(request.POST.get('is_published')),
    }


@permission_required('content:manage')
def cms_pages(request):
    items = list(CmsPage.objects.select_related('author').order_by('-updated_at', '-id'))
    return render(request, 'admin/cms_pages.html', {'items': items})


@permission_required('content:manage')
def cms_page_add(request):
    payload = _cms_page_payload(request)
    if request.method == 'POST':
        if not payload['title'] or not payload['content']:
            messages.error(request, 'Title and content are required.')
        else:
            now = utc_now_naive()
            slug = payload['slug'] or payload['title']
            CmsPage.objects.create(
                title=payload['title'],
                slug=_unique_slug(CmsPage, slug, max_length=200),
                content=payload['content'],
                author_id=request.user.id,
                is_published=payload['is_published'],
                created_at=now,
                updated_at=now,
            )
            messages.success(request, 'CMS page created.')
            return redirect('admin:cms_pages')
    return render(request, 'admin/cms_page_form.html', {'item': None, 'payload': payload})


@permission_required('content:manage')
def cms_page_edit(request, id):
    item = get_object_or_404(CmsPage, id=id)
    payload = _cms_page_payload(request, item=item)
    if request.method == 'POST':
        if not payload['title'] or not payload['content']:
            messages.error(request, 'Title and content are required.')
        else:
            item.title = payload['title']
            item.slug = _unique_slug(CmsPage, payload['slug'] or payload['title'], max_length=200, instance_id=item.id)
            item.content = payload['content']
            item.is_published = payload['is_published']
            item.updated_at = utc_now_naive()
            item.save(update_fields=['title', 'slug', 'content', 'is_published', 'updated_at'])
            messages.success(request, 'CMS page updated.')
            return redirect('admin:cms_page_edit', id=item.id)
    return render(request, 'admin/cms_page_form.html', {'item': item, 'payload': payload})


@permission_required('content:manage')
def cms_page_delete(request, id):
    if request.method == 'POST':
        item = get_object_or_404(CmsPage, id=id)
        item.delete()
        messages.success(request, 'CMS page deleted.')
    return redirect('admin:cms_pages')


@permission_required('content:manage')
def cms_articles(request):
    items = list(CmsArticle.objects.select_related('author').order_by('-updated_at', '-id'))
    return render(request, 'admin/cms_articles.html', {'items': items})


@permission_required('content:manage')
def cms_article_add(request):
    payload = _cms_article_payload(request)
    if request.method == 'POST':
        if not payload['title'] or not payload['content']:
            messages.error(request, 'Title and content are required.')
        else:
            now = utc_now_naive()
            slug = payload['slug'] or payload['title']
            CmsArticle.objects.create(
                title=payload['title'],
                slug=_unique_slug(CmsArticle, slug, max_length=220),
                excerpt=payload['excerpt'],
                content=payload['content'],
                author_id=request.user.id,
                is_published=payload['is_published'],
                published_at=now if payload['is_published'] else None,
                created_at=now,
                updated_at=now,
            )
            messages.success(request, 'CMS article created.')
            return redirect('admin:cms_articles')
    return render(request, 'admin/cms_article_form.html', {'item': None, 'payload': payload})


@permission_required('content:manage')
def cms_article_edit(request, id):
    item = get_object_or_404(CmsArticle, id=id)
    payload = _cms_article_payload(request, item=item)
    if request.method == 'POST':
        if not payload['title'] or not payload['content']:
            messages.error(request, 'Title and content are required.')
        else:
            item.title = payload['title']
            item.slug = _unique_slug(
                CmsArticle,
                payload['slug'] or payload['title'],
                max_length=220,
                instance_id=item.id,
            )
            item.excerpt = payload['excerpt']
            item.content = payload['content']
            item.is_published = payload['is_published']
            if item.is_published and not item.published_at:
                item.published_at = utc_now_naive()
            item.updated_at = utc_now_naive()
            item.save(
                update_fields=[
                    'title',
                    'slug',
                    'excerpt',
                    'content',
                    'is_published',
                    'published_at',
                    'updated_at',
                ]
            )
            messages.success(request, 'CMS article updated.')
            return redirect('admin:cms_article_edit', id=item.id)
    return render(request, 'admin/cms_article_form.html', {'item': item, 'payload': payload})


@permission_required('content:manage')
def cms_article_delete(request, id):
    if request.method == 'POST':
        item = get_object_or_404(CmsArticle, id=id)
        item.delete()
        messages.success(request, 'CMS article deleted.')
    return redirect('admin:cms_articles')


def _menu_tree_for_location(location):
    rows = list(MenuItem.objects.filter(menu_location=location).order_by('sort_order', 'id'))
    children_map = {}
    for row in rows:
        children_map.setdefault(getattr(row, 'parent_id', None), []).append(row)
    roots = children_map.get(None, [])
    for row in roots:
        row.children = children_map.get(row.id, [])
    return roots


@permission_required('content:manage')
def menu_editor(request):
    location = _normalize_menu_location(request.GET.get('location') or request.POST.get('menu_location'))
    if request.method == 'POST':
        label = clean_text(request.POST.get('label', ''), 200)
        if not label:
            messages.error(request, 'Menu label is required.')
            return redirect(f'/admin/menu-editor?location={location}')
        parent_id = _safe_int(request.POST.get('parent_id'), default=0)
        MenuItem.objects.create(
            menu_location=location,
            parent_id=parent_id or None,
            label=label,
            link_type=clean_text(request.POST.get('link_type', 'custom_url'), 30),
            target_slug=clean_text(request.POST.get('target_slug', ''), 200) or None,
            custom_url=clean_text(request.POST.get('custom_url', ''), 500) or None,
            icon_class=clean_text(request.POST.get('icon_class', ''), 100) or None,
            sort_order=_safe_int(request.POST.get('sort_order'), default=0),
            is_visible=bool(request.POST.get('is_visible')),
            open_in_new_tab=bool(request.POST.get('open_in_new_tab')),
            created_at=utc_now_naive(),
        )
        messages.success(request, 'Menu item added.')
        return redirect(f'/admin/menu-editor?location={location}')

    items = _menu_tree_for_location(location)
    return render(
        request,
        'admin/menu_editor.html',
        {
            'location': location,
            'items': items,
        },
    )


@permission_required('content:manage')
def menu_item_edit(request, id):
    item = get_object_or_404(MenuItem, id=id)
    location = _normalize_menu_location(item.menu_location)
    if request.method == 'POST':
        label = clean_text(request.POST.get('label', ''), 200)
        if not label:
            messages.error(request, 'Menu label is required.')
            return redirect('admin:menu_item_edit', id=item.id)
        item.label = label
        item.link_type = clean_text(request.POST.get('link_type', item.link_type), 30) or item.link_type
        item.target_slug = clean_text(request.POST.get('target_slug', ''), 200) or None
        item.custom_url = clean_text(request.POST.get('custom_url', ''), 500) or None
        item.icon_class = clean_text(request.POST.get('icon_class', ''), 100) or None
        item.sort_order = _safe_int(request.POST.get('sort_order'), default=item.sort_order or 0)
        item.is_visible = bool(request.POST.get('is_visible'))
        item.open_in_new_tab = bool(request.POST.get('open_in_new_tab'))
        parent_id = _safe_int(request.POST.get('parent_id'), default=0)
        item.parent_id = parent_id or None
        item.save(
            update_fields=[
                'label',
                'link_type',
                'target_slug',
                'custom_url',
                'icon_class',
                'sort_order',
                'is_visible',
                'open_in_new_tab',
                'parent_id',
            ]
        )
        messages.success(request, 'Menu item updated.')
        return redirect(f'/admin/menu-editor?location={location}')

    parent_candidates = list(
        MenuItem.objects.filter(menu_location=location).exclude(id=item.id).order_by('sort_order', 'id')
    )
    return render(
        request,
        'admin/menu_item_form.html',
        {
            'item': item,
            'location': location,
            'parent_candidates': parent_candidates,
        },
    )


@permission_required('content:manage')
def menu_item_delete(request, id):
    if request.method != 'POST':
        return redirect('admin:menu_editor')
    item = get_object_or_404(MenuItem, id=id)
    location = _normalize_menu_location(item.menu_location)
    MenuItem.objects.filter(parent_id=item.id).delete()
    item.delete()
    messages.success(request, 'Menu item deleted.')
    return redirect(f'/admin/menu-editor?location={location}')
