from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import SuspiciousFileOperation
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils._os import safe_join
from django.utils.text import slugify

from admin_panel.decorators import permission_required
from admin_panel.models import Media
from core.utils import clean_text, utc_now_naive

MAX_UPLOAD_BYTES = 10 * 1024 * 1024

# --- Security: strict file extension allowlist ---
ALLOWED_EXTENSIONS = {
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.ico', '.svg', '.bmp', '.tiff',
    # Documents
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv',
    # Archives
    '.zip', '.gz',
    # Fonts
    '.woff', '.woff2', '.ttf', '.otf', '.eot',
    # Video/Audio
    '.mp4', '.webm', '.mp3', '.ogg', '.wav',
}

# MIME types that are safe to serve inline (displayed in browser)
_INLINE_SAFE_MIMES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp',
    'image/x-icon', 'image/tiff',
    'application/pdf',
}


def _uploaded_path(upload, folder='media'):
    suffix = Path(upload.name).suffix.lower()
    stem = slugify(Path(upload.name).stem)[:60] or 'file'
    token = uuid4().hex[:8]
    rel_path = f'{folder}/{stem}-{token}{suffix}'
    abs_path = Path(settings.MEDIA_ROOT) / rel_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    with abs_path.open('wb') as out:
        for chunk in upload.chunks():
            out.write(chunk)
    return rel_path


def _image_dimensions(abs_path):
    try:
        from PIL import Image

        with Image.open(abs_path) as img:
            return int(img.width), int(img.height)
    except Exception:
        return None, None


@permission_required('content:manage')
def media(request):
    items = list(Media.objects.order_by('-created_at', '-id'))
    return render(request, 'admin/media.html', {'items': items})


@permission_required('content:manage')
def media_upload(request):
    if request.method != 'POST':
        return redirect('admin:media')
    uploads = request.FILES.getlist('file')
    if not uploads:
        messages.error(request, 'Please choose at least one file to upload.')
        return redirect('admin:media')

    saved_count = 0
    for upload in uploads:
        if upload.size > MAX_UPLOAD_BYTES:
            messages.error(request, f'{upload.name}: file exceeds 10MB limit.')
            continue

        suffix = Path(upload.name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            messages.error(request, f'{upload.name}: file type "{suffix}" is not allowed.')
            continue

        rel_path = _uploaded_path(upload, folder='media')
        abs_path = Path(settings.MEDIA_ROOT) / rel_path
        width, height = _image_dimensions(abs_path)

        try:
            Media.objects.create(
                filename=clean_text(upload.name, 300),
                file_path=rel_path,
                file_size=upload.size,
                mime_type=clean_text(upload.content_type, 100),
                alt_text='',
                width=width,
                height=height,
                folder='media',
                created_at=utc_now_naive(),
            )
            saved_count += 1
        except Exception:
            try:
                abs_path.unlink(missing_ok=True)
            except Exception:
                pass
            messages.error(request, f'{upload.name}: failed to save to media library.')

    if saved_count:
        messages.success(request, f'Uploaded {saved_count} file(s).')
    return redirect('admin:media')


@permission_required('content:manage')
def media_delete(request, id):
    if request.method != 'POST':
        return redirect('admin:media')
    item = get_object_or_404(Media, id=id)
    file_path = item.file_path or ''
    item.delete()
    if file_path:
        try:
            safe_path = safe_join(settings.MEDIA_ROOT, file_path)
            Path(safe_path).unlink(missing_ok=True)
        except Exception:
            pass
    messages.success(request, 'Media deleted.')
    return redirect('admin:media')


@permission_required('content:manage')
def media_edit(request, id):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed.'}, status=405)
    item = get_object_or_404(Media, id=id)
    item.alt_text = clean_text(request.POST.get('alt_text', ''), 300)
    item.save(update_fields=['alt_text'])
    return JsonResponse({'ok': True, 'id': item.id, 'alt_text': item.alt_text})


def uploaded_file(request, filename):
    try:
        safe_path = safe_join(settings.MEDIA_ROOT, filename)
    except SuspiciousFileOperation as exc:
        raise Http404 from exc

    path = Path(safe_path)
    if not path.is_file():
        raise Http404

    # Block serving of file types not in the allowlist
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise Http404

    try:
        response = FileResponse(open(path, 'rb'))
    except FileNotFoundError as exc:
        raise Http404 from exc

    # Determine safe Content-Disposition
    import mimetypes
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type and mime_type in _INLINE_SAFE_MIMES:
        response['Content-Disposition'] = f'inline; filename="{path.name}"'
    else:
        # Force download for non-image/non-PDF files to prevent browser execution
        response['Content-Disposition'] = f'attachment; filename="{path.name}"'

    response['Cache-Control'] = 'private, max-age=3600'
    return response
