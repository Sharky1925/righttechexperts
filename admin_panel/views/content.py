from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from admin_panel.decorators import permission_required
from core.constants import (
    WORKFLOW_DRAFT,
    WORKFLOW_PUBLISHED,
    WORKFLOW_STATUSES,
    WORKFLOW_STATUS_LABELS,
    normalize_workflow_status,
)
from core.content_schemas import CONTENT_SCHEMAS
from core.utils import clean_text, utc_now_naive
from public.models import (
    Category,
    ContentBlock,
    Industry,
    IndustryVersion,
    Post,
    PostVersion,
    Service,
    ServiceVersion,
)


def workflow_status_label(status):
    normalized = normalize_workflow_status(status, default=WORKFLOW_DRAFT)
    return WORKFLOW_STATUS_LABELS.get(normalized, WORKFLOW_STATUS_LABELS[WORKFLOW_DRAFT])


def workflow_status_badge(status):
    normalized = normalize_workflow_status(status, default=WORKFLOW_DRAFT)
    if normalized == WORKFLOW_PUBLISHED:
        return 'bg-success'
    if normalized == 'approved':
        return 'bg-primary'
    if normalized == 'review':
        return 'bg-warning text-dark'
    return 'bg-secondary'


def format_datetime_local(value):
    if not isinstance(value, datetime):
        return ''
    return value.strftime('%Y-%m-%dT%H:%M')


def _parse_datetime_local(value):
    raw = (value or '').strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw, '%Y-%m-%dT%H:%M')
    except ValueError:
        return None


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_ids(values):
    if not values:
        return []
    candidates = []
    for value in values:
        if value is None:
            continue
        for part in str(value).split(','):
            token = part.strip()
            if not token:
                continue
            if token.isdigit():
                candidates.append(int(token))
    deduped = []
    seen = set()
    for item in candidates:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


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


def _unique_slug(model, base_slug, instance_id=None):
    normalized = (base_slug or '').strip('-') or 'item'
    candidate = normalized
    counter = 2
    while model.objects.filter(slug=candidate).exclude(id=instance_id).exists():
        candidate = f'{normalized}-{counter}'
        counter += 1
    return candidate


def _workflow_context():
    return {
        'workflow_options': WORKFLOW_STATUSES,
        'workflow_status_label': workflow_status_label,
        'workflow_status_badge': workflow_status_badge,
        'format_datetime_local': format_datetime_local,
    }


@permission_required('content:manage')
def content_list(request):
    grouped = {}
    for (page, section), schema in CONTENT_SCHEMAS.items():
        grouped.setdefault(page, []).append(
            {
                'section': section,
                'label': clean_text(schema.get('label', section), 140),
            }
        )
    pages = {}
    for page, sections in sorted(grouped.items(), key=lambda item: item[0]):
        pages[page] = sorted(sections, key=lambda item: item['label'].lower())
    return render(request, 'admin/content_list.html', {'pages': pages})


@permission_required('content:manage')
def content_edit(request, page, section):
    schema = CONTENT_SCHEMAS.get((page, section))
    if not schema:
        raise Http404

    block = ContentBlock.objects.filter(page=page, section=section).first()
    current_data = {}
    if block and block.content:
        try:
            parsed = json.loads(block.content)
            if isinstance(parsed, dict):
                current_data = parsed
        except (TypeError, ValueError):
            current_data = {}

    if request.method == 'POST':
        payload = {}
        for field in schema.get('fields', []):
            key = field.get('key', '')
            field_type = field.get('type', 'text')
            raw = request.POST.get(key, '')
            if field_type in {'text', 'textarea'}:
                payload[key] = str(raw or '').strip()
                continue
            if field_type == 'lines':
                payload[key] = [line.strip() for line in str(raw or '').splitlines() if line.strip()]
                continue
            if field_type == 'json':
                raw_json = str(raw or '').strip()
                if not raw_json:
                    payload[key] = []
                    continue
                try:
                    payload[key] = json.loads(raw_json)
                except ValueError:
                    messages.error(request, f'Invalid JSON for "{field.get("label", key)}".')
                    return render(
                        request,
                        'admin/content_edit.html',
                        {
                            'schema': schema,
                            'current_data': payload | {key: raw_json},
                        },
                    )
                continue
            payload[key] = str(raw or '').strip()

        now = utc_now_naive()
        try:
            if block:
                block.content = json.dumps(payload, ensure_ascii=False)
                block.updated_at = now
                block.save()
            else:
                ContentBlock.objects.create(
                    page=page,
                    section=section,
                    content=json.dumps(payload, ensure_ascii=False),
                    updated_at=now,
                )
            messages.success(request, f'Updated content block: {page} / {section}.')
            return redirect('admin:content_edit', page=page, section=section)
        except Exception:
            messages.error(request, 'Unable to save content block. Please try again.')
            current_data = payload

    return render(
        request,
        'admin/content_edit.html',
        {
            'schema': schema,
            'current_data': current_data,
        },
    )


def _service_snapshot(item):
    return {
        'title': item.title,
        'slug': item.slug,
        'description': item.description,
        'icon_class': item.icon_class or '',
        'image': item.image or '',
        'service_type': item.service_type or 'professional',
        'is_featured': bool(item.is_featured),
        'sort_order': int(item.sort_order or 0),
        'profile_json': item.profile_json or '',
        'seo_title': item.seo_title or '',
        'seo_description': item.seo_description or '',
        'og_image': item.og_image or '',
        'workflow_status': item.workflow_status or WORKFLOW_DRAFT,
        'scheduled_publish_at': format_datetime_local(item.scheduled_publish_at),
    }


def _create_service_version(item, user, change_note=''):
    try:
        latest = ServiceVersion.objects.filter(service_id=item.id).order_by('-version_number').first()
        version_number = (latest.version_number if latest else 0) + 1
        ServiceVersion.objects.create(
            service_id=item.id,
            version_number=version_number,
            snapshot_json=json.dumps(_service_snapshot(item), ensure_ascii=False),
            change_note=clean_text(change_note, 260),
            created_by_id=getattr(user, 'id', None),
            created_at=utc_now_naive(),
        )
    except Exception:
        return


def _service_preview_from_post(request, item=None):
    target = item if item is not None else Service()
    target.title = clean_text(request.POST.get('title', ''), 200)
    target.description = request.POST.get('description', '')
    target.icon_class = clean_text(request.POST.get('icon_class', 'fa-solid fa-gear'), 120) or 'fa-solid fa-gear'
    target.service_type = clean_text(request.POST.get('service_type', 'professional'), 30) or 'professional'
    target.sort_order = _safe_int(request.POST.get('sort_order'), 0)
    target.is_featured = bool(request.POST.get('is_featured'))
    target.profile_json = request.POST.get('profile_json', '')
    target.seo_title = clean_text(request.POST.get('seo_title', ''), 200)
    target.seo_description = clean_text(request.POST.get('seo_description', ''), 500)
    target.og_image = clean_text(request.POST.get('og_image', ''), 500)
    target.workflow_status = normalize_workflow_status(request.POST.get('workflow_status', WORKFLOW_DRAFT))
    target.scheduled_publish_at = _parse_datetime_local(request.POST.get('scheduled_publish_at'))
    return target


@permission_required('content:manage')
def services(request):
    show_trash = bool((request.GET.get('trash') or '').strip())
    query = Service.objects.order_by('sort_order', 'id')
    if show_trash:
        query = query.filter(is_trashed=True)
    else:
        query = query.filter(Q(is_trashed=False) | Q(is_trashed__isnull=True)).order_by('sort_order', 'id')
    items = list(query)
    ctx = {
        'items': items,
        'bulk_url': '/admin/services/bulk',
    }
    ctx.update(_workflow_context())
    return render(request, 'admin/services.html', ctx)


def _save_service(request, item=None):
    target = _service_preview_from_post(request, item=item)
    if not target.title or not target.description:
        return None, target, 'Title and description are required.'

    service_type = target.service_type if target.service_type in {'professional', 'repair'} else 'professional'
    target.service_type = service_type

    profile_raw = str(request.POST.get('profile_json', '') or '').strip()
    if profile_raw:
        try:
            json.loads(profile_raw)
        except ValueError:
            return None, target, 'Service profile JSON must be valid JSON.'
        target.profile_json = profile_raw
    else:
        target.profile_json = ''

    now = utc_now_naive()
    target.updated_at = now
    if not getattr(target, 'id', None):
        base = slugify(target.title)[:180]
        target.slug = _unique_slug(Service, base_slug=base)
        target.created_at = now
        target.is_trashed = False
        target.trashed_at = None
    else:
        if not target.slug:
            base = slugify(target.title)[:180]
            target.slug = _unique_slug(Service, base_slug=base, instance_id=target.id)

    if target.workflow_status == WORKFLOW_PUBLISHED and not target.published_at:
        target.published_at = now

    upload = request.FILES.get('image')
    if upload:
        target.image = _uploaded_path(upload, folder='services')

    target.save()
    _create_service_version(target, request.user, change_note=request.POST.get('change_note', ''))
    return target, target, ''


@permission_required('content:manage')
def service_add(request):
    item = None
    versions = []
    if request.method == 'POST':
        saved, preview, error = _save_service(request, item=item)
        if saved:
            messages.success(request, 'Service created.')
            return redirect('admin:service_edit', id=saved.id)
        item = preview
        if error:
            messages.error(request, error)
    ctx = {
        'item': item,
        'versions': versions,
    }
    ctx.update(_workflow_context())
    return render(request, 'admin/service_form.html', ctx)


@permission_required('content:manage')
def service_edit(request, id):
    item = get_object_or_404(Service, id=id)
    if request.method == 'POST':
        saved, preview, error = _save_service(request, item=item)
        if saved:
            messages.success(request, 'Service updated.')
            return redirect('admin:service_edit', id=saved.id)
        item = preview
        if error:
            messages.error(request, error)

    try:
        versions = list(ServiceVersion.objects.filter(service_id=item.id).order_by('-version_number')[:20])
    except Exception:
        versions = []
    ctx = {
        'item': item,
        'versions': versions,
    }
    ctx.update(_workflow_context())
    return render(request, 'admin/service_form.html', ctx)


@permission_required('content:manage')
def service_clone(request, id):
    if request.method != 'POST':
        return redirect('admin:services')
    source = get_object_or_404(Service, id=id)
    now = utc_now_naive()
    base_slug = slugify(f'{source.slug}-copy')[:180] or slugify(f'{source.title}-copy')[:180]
    cloned = Service(
        title=f'{source.title} (Copy)',
        slug=_unique_slug(Service, base_slug=base_slug),
        description=source.description,
        icon_class=source.icon_class,
        image=source.image,
        service_type=source.service_type,
        is_featured=False,
        sort_order=source.sort_order,
        profile_json=source.profile_json,
        seo_title=source.seo_title,
        seo_description=source.seo_description,
        og_image=source.og_image,
        is_trashed=False,
        trashed_at=None,
        workflow_status=WORKFLOW_DRAFT,
        scheduled_publish_at=None,
        reviewed_at=None,
        approved_at=None,
        published_at=None,
        created_at=now,
        updated_at=now,
    )
    cloned.save()
    _create_service_version(cloned, request.user, change_note='Cloned from existing service')
    messages.success(request, 'Service duplicated.')
    return redirect('admin:service_edit', id=cloned.id)


@permission_required('content:manage')
def service_delete(request, id):
    if request.method != 'POST':
        return redirect('admin:services')
    item = get_object_or_404(Service, id=id)
    if item.is_trashed:
        try:
            item.delete()
            messages.success(request, 'Service permanently deleted.')
        except Exception:
            messages.error(request, 'Unable to permanently delete service due to related records.')
        return redirect('admin:services')

    item.is_trashed = True
    item.trashed_at = utc_now_naive()
    item.updated_at = utc_now_naive()
    item.save()
    messages.success(request, 'Service moved to trash.')
    return redirect('admin:services')


@permission_required('content:manage')
def service_trash_restore(request, id):
    if request.method != 'POST':
        return redirect('admin:services')
    item = get_object_or_404(Service, id=id)
    item.is_trashed = False
    item.trashed_at = None
    item.updated_at = utc_now_naive()
    item.save()
    messages.success(request, 'Service restored from trash.')
    return redirect('/admin/services?trash=1')


@permission_required('content:manage')
def services_bulk(request):
    if request.method != 'POST':
        return redirect('admin:services')
    action = clean_text(request.POST.get('action', ''), 20).lower()
    ids = _coerce_ids(request.POST.getlist('ids'))
    if not ids:
        messages.error(request, 'No items selected for bulk action.')
        return redirect('admin:services')

    qs = Service.objects.filter(id__in=ids)
    now = utc_now_naive()
    if action == 'publish':
        qs.update(workflow_status=WORKFLOW_PUBLISHED, published_at=now, updated_at=now)
        messages.success(request, f'Published {len(ids)} service(s).')
    elif action == 'draft':
        qs.update(workflow_status=WORKFLOW_DRAFT, updated_at=now)
        messages.success(request, f'Moved {len(ids)} service(s) to draft.')
    elif action == 'trash':
        qs.update(is_trashed=True, trashed_at=now, updated_at=now)
        messages.success(request, f'Moved {len(ids)} service(s) to trash.')
    elif action == 'delete':
        try:
            deleted, _ = qs.delete()
            messages.success(request, f'Deleted {deleted} record(s).')
        except Exception:
            qs.update(is_trashed=True, trashed_at=now, updated_at=now)
            messages.error(request, 'Some records could not be permanently deleted and were moved to trash instead.')
    else:
        messages.error(request, 'Unsupported bulk action.')
    return redirect('admin:services')


@permission_required('content:manage')
def service_autosave(request, id):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed.'}, status=405)
    item = get_object_or_404(Service, id=id)
    preview = _service_preview_from_post(request, item=item)
    item.title = preview.title
    item.description = preview.description
    item.icon_class = preview.icon_class
    item.service_type = preview.service_type
    item.sort_order = preview.sort_order
    item.is_featured = preview.is_featured
    item.profile_json = preview.profile_json
    item.seo_title = preview.seo_title
    item.seo_description = preview.seo_description
    item.og_image = preview.og_image
    item.workflow_status = preview.workflow_status
    item.scheduled_publish_at = preview.scheduled_publish_at
    item.updated_at = utc_now_naive()
    item.save()
    return JsonResponse({'ok': True, 'saved_at': item.updated_at.isoformat()})


@permission_required('content:manage')
def service_restore(request, id):
    if request.method != 'POST':
        return redirect('admin:services')
    version = get_object_or_404(ServiceVersion, id=id)
    service = version.service
    try:
        snapshot = json.loads(version.snapshot_json or '{}')
    except ValueError:
        messages.error(request, 'Version snapshot is invalid JSON.')
        return redirect('admin:service_edit', id=service.id)

    service.title = clean_text(snapshot.get('title', service.title), 200) or service.title
    service.description = snapshot.get('description', service.description)
    service.icon_class = clean_text(snapshot.get('icon_class', service.icon_class), 120) or service.icon_class
    service.service_type = clean_text(snapshot.get('service_type', service.service_type), 30) or service.service_type
    service.sort_order = _safe_int(snapshot.get('sort_order'), service.sort_order or 0)
    service.is_featured = bool(snapshot.get('is_featured'))
    service.profile_json = snapshot.get('profile_json', service.profile_json)
    service.seo_title = clean_text(snapshot.get('seo_title', service.seo_title), 200)
    service.seo_description = clean_text(snapshot.get('seo_description', service.seo_description), 500)
    service.og_image = clean_text(snapshot.get('og_image', service.og_image), 500)
    service.workflow_status = normalize_workflow_status(snapshot.get('workflow_status', service.workflow_status))
    service.scheduled_publish_at = _parse_datetime_local(snapshot.get('scheduled_publish_at', ''))
    service.updated_at = utc_now_naive()
    service.save()
    _create_service_version(service, request.user, change_note=f'Restored version {version.version_number}')
    messages.success(request, f'Restored service to version {version.version_number}.')
    return redirect('admin:service_edit', id=service.id)


def _post_snapshot(item):
    return {
        'title': item.title,
        'slug': item.slug,
        'excerpt': item.excerpt or '',
        'content': item.content,
        'featured_image': item.featured_image or '',
        'category_id': item.category_id,
        'seo_title': item.seo_title or '',
        'seo_description': item.seo_description or '',
        'og_image': item.og_image or '',
        'workflow_status': item.workflow_status or WORKFLOW_DRAFT,
        'scheduled_publish_at': format_datetime_local(item.scheduled_publish_at),
    }


def _create_post_version(item, user, change_note=''):
    try:
        latest = PostVersion.objects.filter(post_id=item.id).order_by('-version_number').first()
        version_number = (latest.version_number if latest else 0) + 1
        PostVersion.objects.create(
            post_id=item.id,
            version_number=version_number,
            snapshot_json=json.dumps(_post_snapshot(item), ensure_ascii=False),
            change_note=clean_text(change_note, 260),
            created_by_id=getattr(user, 'id', None),
            created_at=utc_now_naive(),
        )
    except Exception:
        return


def _post_preview_from_post(request, item=None):
    target = item if item is not None else Post()
    target.title = clean_text(request.POST.get('title', ''), 300)
    target.excerpt = request.POST.get('excerpt', '')
    target.content = request.POST.get('content', '')
    target.category_id = _safe_int(request.POST.get('category_id'), 0) or None
    target.seo_title = clean_text(request.POST.get('seo_title', ''), 200)
    target.seo_description = clean_text(request.POST.get('seo_description', ''), 500)
    target.og_image = clean_text(request.POST.get('og_image', ''), 500)
    target.workflow_status = normalize_workflow_status(request.POST.get('workflow_status', WORKFLOW_DRAFT))
    target.scheduled_publish_at = _parse_datetime_local(request.POST.get('scheduled_publish_at'))
    return target


@permission_required('content:manage')
def posts(request):
    show_trash = bool((request.GET.get('trash') or '').strip())
    query = Post.objects.select_related('category').order_by('-updated_at', '-created_at', '-id')
    if show_trash:
        query = query.filter(is_trashed=True)
    else:
        query = query.filter(Q(is_trashed=False) | Q(is_trashed__isnull=True)).order_by('-updated_at', '-created_at', '-id')
    items = list(query)
    ctx = {
        'items': items,
        'bulk_url': '/admin/posts/bulk',
    }
    ctx.update(_workflow_context())
    return render(request, 'admin/posts.html', ctx)


def _save_post(request, item=None):
    target = _post_preview_from_post(request, item=item)
    if not target.title or not target.content:
        return None, target, 'Title and content are required.'

    now = utc_now_naive()
    target.updated_at = now
    if not getattr(target, 'id', None):
        base = slugify(target.title)[:260]
        target.slug = _unique_slug(Post, base_slug=base)
        target.created_at = now
        target.is_trashed = False
        target.trashed_at = None

    upload = request.FILES.get('featured_image')
    if upload:
        target.featured_image = _uploaded_path(upload, folder='posts')

    target.is_published = target.workflow_status == WORKFLOW_PUBLISHED
    if target.workflow_status == WORKFLOW_PUBLISHED and not target.published_at:
        target.published_at = now

    target.save()
    _create_post_version(target, request.user, change_note=request.POST.get('change_note', ''))
    return target, target, ''


@permission_required('content:manage')
def post_add(request):
    item = None
    versions = []
    if request.method == 'POST':
        saved, preview, error = _save_post(request, item=item)
        if saved:
            messages.success(request, 'Post created.')
            return redirect('admin:post_edit', id=saved.id)
        item = preview
        if error:
            messages.error(request, error)
    categories = list(Category.objects.order_by('name', 'id'))
    ctx = {
        'item': item,
        'categories': categories,
        'versions': versions,
    }
    ctx.update(_workflow_context())
    return render(request, 'admin/post_form.html', ctx)


@permission_required('content:manage')
def post_edit(request, id):
    item = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        saved, preview, error = _save_post(request, item=item)
        if saved:
            messages.success(request, 'Post updated.')
            return redirect('admin:post_edit', id=saved.id)
        item = preview
        if error:
            messages.error(request, error)
    categories = list(Category.objects.order_by('name', 'id'))
    try:
        versions = list(PostVersion.objects.filter(post_id=item.id).order_by('-version_number')[:20])
    except Exception:
        versions = []
    ctx = {
        'item': item,
        'categories': categories,
        'versions': versions,
    }
    ctx.update(_workflow_context())
    return render(request, 'admin/post_form.html', ctx)


@permission_required('content:manage')
def post_clone(request, id):
    if request.method != 'POST':
        return redirect('admin:posts')
    source = get_object_or_404(Post, id=id)
    now = utc_now_naive()
    base_slug = slugify(f'{source.slug}-copy')[:260] or slugify(f'{source.title}-copy')[:260]
    cloned = Post(
        title=f'{source.title} (Copy)',
        slug=_unique_slug(Post, base_slug=base_slug),
        excerpt=source.excerpt,
        content=source.content,
        featured_image=source.featured_image,
        category_id=source.category_id,
        is_published=False,
        seo_title=source.seo_title,
        seo_description=source.seo_description,
        og_image=source.og_image,
        is_trashed=False,
        trashed_at=None,
        workflow_status=WORKFLOW_DRAFT,
        scheduled_publish_at=None,
        reviewed_at=None,
        approved_at=None,
        published_at=None,
        created_at=now,
        updated_at=now,
    )
    cloned.save()
    _create_post_version(cloned, request.user, change_note='Cloned from existing post')
    messages.success(request, 'Post duplicated.')
    return redirect('admin:post_edit', id=cloned.id)


@permission_required('content:manage')
def post_delete(request, id):
    if request.method != 'POST':
        return redirect('admin:posts')
    item = get_object_or_404(Post, id=id)
    if item.is_trashed:
        try:
            item.delete()
            messages.success(request, 'Post permanently deleted.')
        except Exception:
            messages.error(request, 'Unable to permanently delete post due to related records.')
        return redirect('admin:posts')

    item.is_trashed = True
    item.trashed_at = utc_now_naive()
    item.updated_at = utc_now_naive()
    item.save()
    messages.success(request, 'Post moved to trash.')
    return redirect('admin:posts')


@permission_required('content:manage')
def post_trash_restore(request, id):
    if request.method != 'POST':
        return redirect('admin:posts')
    item = get_object_or_404(Post, id=id)
    item.is_trashed = False
    item.trashed_at = None
    item.updated_at = utc_now_naive()
    item.save()
    messages.success(request, 'Post restored from trash.')
    return redirect('/admin/posts?trash=1')


@permission_required('content:manage')
def posts_bulk(request):
    if request.method != 'POST':
        return redirect('admin:posts')
    action = clean_text(request.POST.get('action', ''), 20).lower()
    ids = _coerce_ids(request.POST.getlist('ids'))
    if not ids:
        messages.error(request, 'No items selected for bulk action.')
        return redirect('admin:posts')

    qs = Post.objects.filter(id__in=ids)
    now = utc_now_naive()
    if action == 'publish':
        qs.update(workflow_status=WORKFLOW_PUBLISHED, is_published=True, published_at=now, updated_at=now)
        messages.success(request, f'Published {len(ids)} post(s).')
    elif action == 'draft':
        qs.update(workflow_status=WORKFLOW_DRAFT, is_published=False, updated_at=now)
        messages.success(request, f'Moved {len(ids)} post(s) to draft.')
    elif action == 'trash':
        qs.update(is_trashed=True, trashed_at=now, updated_at=now)
        messages.success(request, f'Moved {len(ids)} post(s) to trash.')
    elif action == 'delete':
        try:
            deleted, _ = qs.delete()
            messages.success(request, f'Deleted {deleted} record(s).')
        except Exception:
            qs.update(is_trashed=True, trashed_at=now, updated_at=now)
            messages.error(request, 'Some records could not be permanently deleted and were moved to trash instead.')
    else:
        messages.error(request, 'Unsupported bulk action.')
    return redirect('admin:posts')


@permission_required('content:manage')
def post_autosave(request, id):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed.'}, status=405)
    item = get_object_or_404(Post, id=id)
    preview = _post_preview_from_post(request, item=item)
    item.title = preview.title
    item.excerpt = preview.excerpt
    item.content = preview.content
    item.category_id = preview.category_id
    item.seo_title = preview.seo_title
    item.seo_description = preview.seo_description
    item.og_image = preview.og_image
    item.workflow_status = preview.workflow_status
    item.scheduled_publish_at = preview.scheduled_publish_at
    item.updated_at = utc_now_naive()
    item.save()
    return JsonResponse({'ok': True, 'saved_at': item.updated_at.isoformat()})


@permission_required('content:manage')
def post_restore(request, id):
    if request.method != 'POST':
        return redirect('admin:posts')
    version = get_object_or_404(PostVersion, id=id)
    post = version.post
    try:
        snapshot = json.loads(version.snapshot_json or '{}')
    except ValueError:
        messages.error(request, 'Version snapshot is invalid JSON.')
        return redirect('admin:post_edit', id=post.id)

    post.title = clean_text(snapshot.get('title', post.title), 300) or post.title
    post.excerpt = snapshot.get('excerpt', post.excerpt)
    post.content = snapshot.get('content', post.content)
    post.featured_image = snapshot.get('featured_image', post.featured_image)
    post.category_id = _safe_int(snapshot.get('category_id'), 0) or None
    post.seo_title = clean_text(snapshot.get('seo_title', post.seo_title), 200)
    post.seo_description = clean_text(snapshot.get('seo_description', post.seo_description), 500)
    post.og_image = clean_text(snapshot.get('og_image', post.og_image), 500)
    post.workflow_status = normalize_workflow_status(snapshot.get('workflow_status', post.workflow_status))
    post.scheduled_publish_at = _parse_datetime_local(snapshot.get('scheduled_publish_at', ''))
    post.is_published = post.workflow_status == WORKFLOW_PUBLISHED
    if post.is_published and not post.published_at:
        post.published_at = utc_now_naive()
    post.updated_at = utc_now_naive()
    post.save()
    _create_post_version(post, request.user, change_note=f'Restored version {version.version_number}')
    messages.success(request, f'Restored post to version {version.version_number}.')
    return redirect('admin:post_edit', id=post.id)


def _industry_snapshot(item):
    return {
        'title': item.title,
        'slug': item.slug,
        'description': item.description,
        'icon_class': item.icon_class or '',
        'hero_description': item.hero_description or '',
        'challenges': item.challenges or '',
        'solutions': item.solutions or '',
        'stats': item.stats or '',
        'sort_order': int(item.sort_order or 0),
        'seo_title': item.seo_title or '',
        'seo_description': item.seo_description or '',
        'og_image': item.og_image or '',
        'workflow_status': item.workflow_status or WORKFLOW_DRAFT,
        'scheduled_publish_at': format_datetime_local(item.scheduled_publish_at),
    }


def _create_industry_version(item, user, change_note=''):
    try:
        latest = IndustryVersion.objects.filter(industry_id=item.id).order_by('-version_number').first()
        version_number = (latest.version_number if latest else 0) + 1
        IndustryVersion.objects.create(
            industry_id=item.id,
            version_number=version_number,
            snapshot_json=json.dumps(_industry_snapshot(item), ensure_ascii=False),
            change_note=clean_text(change_note, 260),
            created_by_id=getattr(user, 'id', None),
            created_at=utc_now_naive(),
        )
    except Exception:
        return


def _industry_preview_from_post(request, item=None):
    target = item if item is not None else Industry()
    target.title = clean_text(request.POST.get('title', ''), 200)
    target.description = request.POST.get('description', '')
    target.icon_class = clean_text(request.POST.get('icon_class', 'fa-solid fa-building'), 120) or 'fa-solid fa-building'
    target.hero_description = request.POST.get('hero_description', '')
    target.challenges = request.POST.get('challenges', '')
    target.solutions = request.POST.get('solutions', '')
    target.stats = request.POST.get('stats', '')
    target.sort_order = _safe_int(request.POST.get('sort_order'), 0)
    target.seo_title = clean_text(request.POST.get('seo_title', ''), 200)
    target.seo_description = clean_text(request.POST.get('seo_description', ''), 500)
    target.og_image = clean_text(request.POST.get('og_image', ''), 500)
    target.workflow_status = normalize_workflow_status(request.POST.get('workflow_status', WORKFLOW_DRAFT))
    target.scheduled_publish_at = _parse_datetime_local(request.POST.get('scheduled_publish_at'))
    return target


@permission_required('content:manage')
def industries(request):
    show_trash = bool((request.GET.get('trash') or '').strip())
    query = Industry.objects.order_by('sort_order', 'id')
    if show_trash:
        query = query.filter(is_trashed=True)
    else:
        query = query.filter(Q(is_trashed=False) | Q(is_trashed__isnull=True)).order_by('sort_order', 'id')
    items = list(query)
    ctx = {
        'items': items,
        'bulk_url': '/admin/industries/bulk',
    }
    ctx.update(_workflow_context())
    return render(request, 'admin/industries.html', ctx)


def _save_industry(request, item=None):
    target = _industry_preview_from_post(request, item=item)
    if not target.title or not target.description:
        return None, target, 'Title and description are required.'

    now = utc_now_naive()
    target.updated_at = now
    if not getattr(target, 'id', None):
        base = slugify(target.title)[:180]
        target.slug = _unique_slug(Industry, base_slug=base)
        target.created_at = now
        target.is_trashed = False
        target.trashed_at = None
    else:
        if not target.slug:
            base = slugify(target.title)[:180]
            target.slug = _unique_slug(Industry, base_slug=base, instance_id=target.id)

    if target.workflow_status == WORKFLOW_PUBLISHED and not target.published_at:
        target.published_at = now

    target.save()
    _create_industry_version(target, request.user, change_note=request.POST.get('change_note', ''))
    return target, target, ''


@permission_required('content:manage')
def industry_add(request):
    item = None
    versions = []
    if request.method == 'POST':
        saved, preview, error = _save_industry(request, item=item)
        if saved:
            messages.success(request, 'Industry created.')
            return redirect('admin:industry_edit', id=saved.id)
        item = preview
        if error:
            messages.error(request, error)
    ctx = {
        'item': item,
        'versions': versions,
    }
    ctx.update(_workflow_context())
    return render(request, 'admin/industry_form.html', ctx)


@permission_required('content:manage')
def industry_edit(request, id):
    item = get_object_or_404(Industry, id=id)
    if request.method == 'POST':
        saved, preview, error = _save_industry(request, item=item)
        if saved:
            messages.success(request, 'Industry updated.')
            return redirect('admin:industry_edit', id=saved.id)
        item = preview
        if error:
            messages.error(request, error)

    try:
        versions = list(IndustryVersion.objects.filter(industry_id=item.id).order_by('-version_number')[:20])
    except Exception:
        versions = []
    ctx = {
        'item': item,
        'versions': versions,
    }
    ctx.update(_workflow_context())
    return render(request, 'admin/industry_form.html', ctx)


@permission_required('content:manage')
def industry_clone(request, id):
    if request.method != 'POST':
        return redirect('admin:industries')
    source = get_object_or_404(Industry, id=id)
    now = utc_now_naive()
    base_slug = slugify(f'{source.slug}-copy')[:180] or slugify(f'{source.title}-copy')[:180]
    cloned = Industry(
        title=f'{source.title} (Copy)',
        slug=_unique_slug(Industry, base_slug=base_slug),
        description=source.description,
        icon_class=source.icon_class,
        hero_description=source.hero_description,
        challenges=source.challenges,
        solutions=source.solutions,
        stats=source.stats,
        sort_order=source.sort_order,
        seo_title=source.seo_title,
        seo_description=source.seo_description,
        og_image=source.og_image,
        is_trashed=False,
        trashed_at=None,
        workflow_status=WORKFLOW_DRAFT,
        scheduled_publish_at=None,
        reviewed_at=None,
        approved_at=None,
        published_at=None,
        created_at=now,
        updated_at=now,
    )
    cloned.save()
    _create_industry_version(cloned, request.user, change_note='Cloned from existing industry')
    messages.success(request, 'Industry duplicated.')
    return redirect('admin:industry_edit', id=cloned.id)


@permission_required('content:manage')
def industry_delete(request, id):
    if request.method != 'POST':
        return redirect('admin:industries')
    item = get_object_or_404(Industry, id=id)
    if item.is_trashed:
        try:
            item.delete()
            messages.success(request, 'Industry permanently deleted.')
        except Exception:
            messages.error(request, 'Unable to permanently delete industry due to related records.')
        return redirect('admin:industries')

    item.is_trashed = True
    item.trashed_at = utc_now_naive()
    item.updated_at = utc_now_naive()
    item.save()
    messages.success(request, 'Industry moved to trash.')
    return redirect('admin:industries')


@permission_required('content:manage')
def industry_trash_restore(request, id):
    if request.method != 'POST':
        return redirect('admin:industries')
    item = get_object_or_404(Industry, id=id)
    item.is_trashed = False
    item.trashed_at = None
    item.updated_at = utc_now_naive()
    item.save()
    messages.success(request, 'Industry restored from trash.')
    return redirect('/admin/industries?trash=1')


@permission_required('content:manage')
def industries_bulk(request):
    if request.method != 'POST':
        return redirect('admin:industries')
    action = clean_text(request.POST.get('action', ''), 20).lower()
    ids = _coerce_ids(request.POST.getlist('ids'))
    if not ids:
        messages.error(request, 'No items selected for bulk action.')
        return redirect('admin:industries')

    qs = Industry.objects.filter(id__in=ids)
    now = utc_now_naive()
    if action == 'publish':
        qs.update(workflow_status=WORKFLOW_PUBLISHED, published_at=now, updated_at=now)
        messages.success(request, f'Published {len(ids)} industry item(s).')
    elif action == 'draft':
        qs.update(workflow_status=WORKFLOW_DRAFT, updated_at=now)
        messages.success(request, f'Moved {len(ids)} industry item(s) to draft.')
    elif action == 'trash':
        qs.update(is_trashed=True, trashed_at=now, updated_at=now)
        messages.success(request, f'Moved {len(ids)} industry item(s) to trash.')
    elif action == 'delete':
        try:
            deleted, _ = qs.delete()
            messages.success(request, f'Deleted {deleted} record(s).')
        except Exception:
            qs.update(is_trashed=True, trashed_at=now, updated_at=now)
            messages.error(request, 'Some records could not be permanently deleted and were moved to trash instead.')
    else:
        messages.error(request, 'Unsupported bulk action.')
    return redirect('admin:industries')


@permission_required('content:manage')
def industry_autosave(request, id):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed.'}, status=405)
    item = get_object_or_404(Industry, id=id)
    preview = _industry_preview_from_post(request, item=item)
    item.title = preview.title
    item.description = preview.description
    item.icon_class = preview.icon_class
    item.hero_description = preview.hero_description
    item.challenges = preview.challenges
    item.solutions = preview.solutions
    item.stats = preview.stats
    item.sort_order = preview.sort_order
    item.seo_title = preview.seo_title
    item.seo_description = preview.seo_description
    item.og_image = preview.og_image
    item.workflow_status = preview.workflow_status
    item.scheduled_publish_at = preview.scheduled_publish_at
    item.updated_at = utc_now_naive()
    item.save()
    return JsonResponse({'ok': True, 'saved_at': item.updated_at.isoformat()})


@permission_required('content:manage')
def industry_restore(request, id):
    if request.method != 'POST':
        return redirect('admin:industries')
    version = get_object_or_404(IndustryVersion, id=id)
    industry = version.industry
    try:
        snapshot = json.loads(version.snapshot_json or '{}')
    except ValueError:
        messages.error(request, 'Version snapshot is invalid JSON.')
        return redirect('admin:industry_edit', id=industry.id)

    industry.title = clean_text(snapshot.get('title', industry.title), 200) or industry.title
    industry.description = snapshot.get('description', industry.description)
    industry.icon_class = clean_text(snapshot.get('icon_class', industry.icon_class), 120) or industry.icon_class
    industry.hero_description = snapshot.get('hero_description', industry.hero_description)
    industry.challenges = snapshot.get('challenges', industry.challenges)
    industry.solutions = snapshot.get('solutions', industry.solutions)
    industry.stats = snapshot.get('stats', industry.stats)
    industry.sort_order = _safe_int(snapshot.get('sort_order'), industry.sort_order or 0)
    industry.seo_title = clean_text(snapshot.get('seo_title', industry.seo_title), 200)
    industry.seo_description = clean_text(snapshot.get('seo_description', industry.seo_description), 500)
    industry.og_image = clean_text(snapshot.get('og_image', industry.og_image), 500)
    industry.workflow_status = normalize_workflow_status(snapshot.get('workflow_status', industry.workflow_status))
    industry.scheduled_publish_at = _parse_datetime_local(snapshot.get('scheduled_publish_at', ''))
    industry.updated_at = utc_now_naive()
    industry.save()
    _create_industry_version(industry, request.user, change_note=f'Restored version {version.version_number}')
    messages.success(request, f'Restored industry to version {version.version_number}.')
    return redirect('admin:industry_edit', id=industry.id)
