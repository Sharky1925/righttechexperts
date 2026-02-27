# MyLauncher Django Migration Workspace

This directory is an isolated scaffold for Flask -> Django migration.

- Source Flask app remains untouched at: `/Users/umutdemirkapu/mylauncher`
- Templates/static copied from Flask app to: `app/templates`, `app/static`
- Current status: **Phase 1+ implementation in progress (public + core admin flows now functional)**

## Quick start

```bash
cd /Users/umutdemirkapu/Desktop/mylauncherdjangocodex
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py check
python manage.py runserver
```

## Preview locally

```bash
cd /Users/umutdemirkapu/Desktop/mylauncherdjangocodex
source .venv/bin/activate
python manage.py runserver 127.0.0.1:4173
```

Open:
- `http://127.0.0.1:4173/`
- `http://127.0.0.1:4173/admin/login`

## Admin login

- URL: `http://127.0.0.1:4173/admin/login`
- Current known admin user: `codexadmin`
- Current known password: `pass1234`

If login still fails, reset password:

```bash
cd /Users/umutdemirkapu/Desktop/mylauncherdjangocodex
source .venv/bin/activate
python manage.py shell -c "from admin_panel.models import User; u=User.objects.get(username='codexadmin'); u.set_password('pass1234'); u.save(update_fields=['password']); print('password-reset:', u.username)"
```

If you run inside a sandbox and see `attempt to write a readonly database`, run the reset command in your normal local terminal (outside sandbox), or point `LEGACY_SQLITE_PATH` to a writable copy.

## What is implemented now

- Dynamic SEO endpoints: `sitemap.xml` and `robots.txt`
- Public contact + quote form POST handling with validation and lead capture
- Cached global site context (settings/navigation/footer)
- Admin content tools:
  - Page content block editor
  - Services CRUD + bulk actions + clone + restore + autosave
  - Blog posts CRUD + bulk actions + clone + restore + autosave
  - Industries CRUD + bulk actions + clone + restore + autosave
  - Contacts inbox + lead status + CSV export + bulk actions
  - Support ticket queue + detail review actions + timeline updates
  - Team/Testimonial/Category CRUD (with trash/bulk where applicable)
  - Admin user management (role-aware assignment + password validation)
  - Site settings + Headless hub settings UI
  - CMS Pages / CMS Articles CRUD
  - Navigation menu editor + menu item edit/delete
  - Media library upload/edit/delete
  - Security events listing/filtering
- Safer upload serving path validation
- Session backend switched to signed cookies for legacy DB compatibility

## Tests

```bash
cd /Users/umutdemirkapu/Desktop/mylauncherdjangocodex
source .venv/bin/activate
python manage.py test public.tests admin_panel.tests
```

## Notes

- Models are currently scaffolded with `managed = False` for schema parity with the legacy app.
- `config/jinja2_env.py` provides Flask-style `url_for`, `csrf_input`, and `get_flashed_messages` adapters.
- Remaining placeholder modules are mostly in `acp/` and `headless/`.
