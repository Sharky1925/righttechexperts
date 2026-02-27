from django.conf import settings
from django.db import models


class Service(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    icon_class = models.CharField(max_length=100, blank=True, null=True)
    image = models.CharField(max_length=300, blank=True, null=True)
    service_type = models.CharField(max_length=20, blank=True, null=True)
    is_featured = models.BooleanField(default=False, null=True)
    sort_order = models.IntegerField(default=0, null=True)
    profile_json = models.TextField(blank=True, null=True)
    seo_title = models.CharField(max_length=200, blank=True, null=True)
    seo_description = models.CharField(max_length=500, blank=True, null=True)
    og_image = models.CharField(max_length=500, blank=True, null=True)
    is_trashed = models.BooleanField(default=False, null=True)
    trashed_at = models.DateTimeField(blank=True, null=True)
    workflow_status = models.CharField(max_length=20)
    scheduled_publish_at = models.DateTimeField(blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'service'
        managed = False


class TeamMember(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    bio = models.TextField(blank=True, null=True)
    photo = models.CharField(max_length=300, blank=True, null=True)
    linkedin = models.CharField(max_length=300, blank=True, null=True)
    sort_order = models.IntegerField(default=0, null=True)
    is_trashed = models.BooleanField(default=False, null=True)
    trashed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'team_member'
        managed = False


class Testimonial(models.Model):
    id = models.BigAutoField(primary_key=True)
    client_name = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    rating = models.IntegerField(default=5, null=True)
    is_featured = models.BooleanField(default=False, null=True)
    is_trashed = models.BooleanField(default=False, null=True)
    trashed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'testimonial'
        managed = False


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'category'
        managed = False


class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=300)
    slug = models.CharField(max_length=300, unique=True)
    excerpt = models.TextField(blank=True, null=True)
    content = models.TextField()
    featured_image = models.CharField(max_length=300, blank=True, null=True)
    category = models.ForeignKey(Category, db_column='category_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    is_published = models.BooleanField(default=False, null=True)
    seo_title = models.CharField(max_length=200, blank=True, null=True)
    seo_description = models.CharField(max_length=500, blank=True, null=True)
    og_image = models.CharField(max_length=500, blank=True, null=True)
    is_trashed = models.BooleanField(default=False, null=True)
    trashed_at = models.DateTimeField(blank=True, null=True)
    workflow_status = models.CharField(max_length=20)
    scheduled_publish_at = models.DateTimeField(blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'post'
        managed = False


class CmsPage(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='author_id', on_delete=models.DO_NOTHING)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'cms_page'
        managed = False


class CmsArticle(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=220)
    slug = models.CharField(max_length=220, unique=True)
    excerpt = models.CharField(max_length=600, blank=True, null=True)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='author_id', on_delete=models.DO_NOTHING)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'cms_article'
        managed = False


class Industry(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    icon_class = models.CharField(max_length=100, blank=True, null=True)
    hero_description = models.TextField(blank=True, null=True)
    challenges = models.TextField(blank=True, null=True)
    solutions = models.TextField(blank=True, null=True)
    stats = models.TextField(blank=True, null=True)
    sort_order = models.IntegerField(default=0, null=True)
    seo_title = models.CharField(max_length=200, blank=True, null=True)
    seo_description = models.CharField(max_length=500, blank=True, null=True)
    og_image = models.CharField(max_length=500, blank=True, null=True)
    is_trashed = models.BooleanField(default=False, null=True)
    trashed_at = models.DateTimeField(blank=True, null=True)
    workflow_status = models.CharField(max_length=20)
    scheduled_publish_at = models.DateTimeField(blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'industry'
        managed = False


class ContentBlock(models.Model):
    id = models.BigAutoField(primary_key=True)
    page = models.CharField(max_length=50)
    section = models.CharField(max_length=80)
    content = models.TextField(default='{}')
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'content_block'
        managed = False


class SiteSetting(models.Model):
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'site_setting'
        managed = False


class PostVersion(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, db_column='post_id', on_delete=models.DO_NOTHING)
    version_number = models.IntegerField()
    snapshot_json = models.TextField(default='{}')
    change_note = models.CharField(max_length=260, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'post_version'
        managed = False


class ServiceVersion(models.Model):
    id = models.BigAutoField(primary_key=True)
    service = models.ForeignKey(Service, db_column='service_id', on_delete=models.DO_NOTHING)
    version_number = models.IntegerField()
    snapshot_json = models.TextField(default='{}')
    change_note = models.CharField(max_length=260, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'service_version'
        managed = False


class IndustryVersion(models.Model):
    id = models.BigAutoField(primary_key=True)
    industry = models.ForeignKey(Industry, db_column='industry_id', on_delete=models.DO_NOTHING)
    version_number = models.IntegerField()
    snapshot_json = models.TextField(default='{}')
    change_note = models.CharField(max_length=260, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'industry_version'
        managed = False


class MenuItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    menu_location = models.CharField(max_length=30)
    parent = models.ForeignKey('self', db_column='parent_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    label = models.CharField(max_length=200)
    link_type = models.CharField(max_length=30)
    target_slug = models.CharField(max_length=200, blank=True, null=True)
    custom_url = models.CharField(max_length=500, blank=True, null=True)
    icon_class = models.CharField(max_length=100, blank=True, null=True)
    sort_order = models.IntegerField(default=0, null=True)
    is_visible = models.BooleanField(default=True, null=True)
    open_in_new_tab = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'menu_item'
        managed = False


class PageView(models.Model):
    id = models.BigAutoField(primary_key=True)
    path = models.CharField(max_length=500)
    page_type = models.CharField(max_length=40, blank=True, null=True)
    entity_id = models.IntegerField(blank=True, null=True)
    ip_hash = models.CharField(max_length=64, blank=True, null=True)
    user_agent = models.CharField(max_length=300, blank=True, null=True)
    referrer = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'page_view'
        managed = False
