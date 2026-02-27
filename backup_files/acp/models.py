from django.conf import settings
from django.db import models


class AcpPageDocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    slug = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=220)
    template_id = models.CharField(max_length=120)
    locale = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    seo_json = models.TextField(default='{}')
    blocks_tree = models.TextField(default='{}')
    theme_override_json = models.TextField(default='{}')
    scheduled_publish_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_pages_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='updated_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_pages_updated')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_page_document'
        managed = False


class AcpPageVersion(models.Model):
    id = models.BigAutoField(primary_key=True)
    page = models.ForeignKey(AcpPageDocument, db_column='page_id', on_delete=models.DO_NOTHING)
    version_number = models.IntegerField()
    snapshot_json = models.TextField(default='{}')
    change_note = models.CharField(max_length=260, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_page_version'
        managed = False


class AcpPageRouteBinding(models.Model):
    id = models.BigAutoField(primary_key=True)
    route_rule = models.CharField(max_length=240, unique=True)
    endpoint = models.CharField(max_length=180)
    methods_json = models.TextField(default='[]')
    page_slug = models.CharField(max_length=200, blank=True, null=True)
    page = models.ForeignKey(AcpPageDocument, db_column='page_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    sync_status = models.CharField(max_length=40)
    issue_detail = models.CharField(max_length=320, blank=True, null=True)
    is_dynamic = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_seen_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_page_route_binding'
        managed = False


class AcpDashboardDocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    dashboard_id = models.CharField(max_length=120, unique=True)
    title = models.CharField(max_length=220)
    route = models.CharField(max_length=220, unique=True)
    layout_type = models.CharField(max_length=24)
    status = models.CharField(max_length=20)
    layout_config_json = models.TextField(default='{}')
    widgets_json = models.TextField(default='[]')
    global_filters_json = models.TextField(default='[]')
    role_visibility_json = models.TextField(default='{}')
    scheduled_publish_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_dashboards_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='updated_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_dashboards_updated')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_dashboard_document'
        managed = False


class AcpDashboardVersion(models.Model):
    id = models.BigAutoField(primary_key=True)
    dashboard_document = models.ForeignKey(AcpDashboardDocument, db_column='dashboard_document_id', on_delete=models.DO_NOTHING)
    version_number = models.IntegerField()
    snapshot_json = models.TextField(default='{}')
    change_note = models.CharField(max_length=260, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_dashboard_version'
        managed = False


class AcpComponentDefinition(models.Model):
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=120, unique=True)
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=80)
    prop_schema_json = models.TextField(default='{}')
    default_props_json = models.TextField(default='{}')
    allowed_children_json = models.TextField(default='[]')
    restrictions_json = models.TextField(default='{}')
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_component_definition'
        managed = False


class AcpWidgetDefinition(models.Model):
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=120, unique=True)
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=80)
    config_schema_json = models.TextField(default='{}')
    data_contract_json = models.TextField(default='{}')
    allowed_filters_json = models.TextField(default='[]')
    permissions_required_json = models.TextField(default='[]')
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_widget_definition'
        managed = False


class AcpMetricDefinition(models.Model):
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=120, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True, null=True)
    dataset_key = models.CharField(max_length=120)
    query_template = models.TextField(default='')
    formula = models.TextField(default='')
    dimensions_json = models.TextField(default='[]')
    allowed_roles_json = models.TextField(default='[]')
    default_aggregation = models.CharField(max_length=40)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_metric_definition'
        managed = False


class AcpContentType(models.Model):
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=120, unique=True)
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True, null=True)
    schema_json = models.TextField(default='{}')
    is_enabled = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_content_types_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='updated_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_content_types_updated')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_content_type'
        managed = False


class AcpContentTypeVersion(models.Model):
    id = models.BigAutoField(primary_key=True)
    content_type = models.ForeignKey(AcpContentType, db_column='content_type_id', on_delete=models.DO_NOTHING)
    version_number = models.IntegerField()
    snapshot_json = models.TextField(default='{}')
    change_note = models.CharField(max_length=260, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_content_type_version'
        managed = False


class AcpContentEntry(models.Model):
    id = models.BigAutoField(primary_key=True)
    content_type = models.ForeignKey(AcpContentType, db_column='content_type_id', on_delete=models.DO_NOTHING)
    entry_key = models.CharField(max_length=140)
    title = models.CharField(max_length=220)
    locale = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    data_json = models.TextField(default='{}')
    scheduled_publish_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_content_entries_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='updated_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_content_entries_updated')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_content_entry'
        managed = False


class AcpContentEntryVersion(models.Model):
    id = models.BigAutoField(primary_key=True)
    content_entry = models.ForeignKey(AcpContentEntry, db_column='content_entry_id', on_delete=models.DO_NOTHING)
    version_number = models.IntegerField()
    snapshot_json = models.TextField(default='{}')
    change_note = models.CharField(max_length=260, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_content_entry_version'
        managed = False


class AcpThemeTokenSet(models.Model):
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=180)
    status = models.CharField(max_length=20)
    tokens_json = models.TextField(default='{}')
    scheduled_publish_at = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_theme_sets_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='updated_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_theme_sets_updated')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_theme_token_set'
        managed = False


class AcpThemeTokenVersion(models.Model):
    id = models.BigAutoField(primary_key=True)
    token_set = models.ForeignKey(AcpThemeTokenSet, db_column='token_set_id', on_delete=models.DO_NOTHING)
    version_number = models.IntegerField()
    snapshot_json = models.TextField(default='{}')
    change_note = models.CharField(max_length=260, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_theme_token_version'
        managed = False


class AcpMcpServer(models.Model):
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=120, unique=True)
    name = models.CharField(max_length=180)
    server_url = models.CharField(max_length=500)
    transport = models.CharField(max_length=40)
    auth_mode = models.CharField(max_length=40)
    environment = models.CharField(max_length=40)
    allowed_tools_json = models.TextField(default='[]')
    require_approval = models.CharField(max_length=24)
    is_enabled = models.BooleanField(default=True)
    notes = models.CharField(max_length=400, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='created_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_mcp_servers_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='updated_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_mcp_servers_updated')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_mcp_server'
        managed = False


class AcpMcpAuditEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    server = models.ForeignKey(AcpMcpServer, db_column='server_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    action = models.CharField(max_length=40)
    tool_name = models.CharField(max_length=160, blank=True, null=True)
    status = models.CharField(max_length=30)
    request_json = models.TextField(blank=True, null=True)
    response_json = models.TextField(blank=True, null=True)
    actor_user = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='actor_user_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_mcp_audit_event'
        managed = False


class AcpMcpOperation(models.Model):
    id = models.BigAutoField(primary_key=True)
    server = models.ForeignKey(AcpMcpServer, db_column='server_id', on_delete=models.DO_NOTHING)
    request_id = models.CharField(max_length=36, unique=True)
    tool_name = models.CharField(max_length=160)
    arguments_json = models.TextField(default='{}')
    response_json = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=32)
    approval_status = models.CharField(max_length=24)
    requires_approval = models.BooleanField(default=False)
    attempt_count = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    error_message = models.CharField(max_length=800, blank=True, null=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='requested_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_mcp_ops_requested')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='approved_by_id', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='acp_mcp_ops_approved')
    approved_at = models.DateTimeField(blank=True, null=True)
    last_attempt_at = models.DateTimeField(blank=True, null=True)
    next_attempt_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_mcp_operation'
        managed = False


class AcpEnvironment(models.Model):
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=40, unique=True)
    label = models.CharField(max_length=80)
    is_default = models.BooleanField(default=False)
    is_protected = models.BooleanField(default=False)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_environment'
        managed = False


class AcpPromotionEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    source_environment = models.CharField(max_length=40)
    target_environment = models.CharField(max_length=40)
    resource_type = models.CharField(max_length=40)
    resource_id = models.IntegerField()
    version_number = models.IntegerField()
    status = models.CharField(max_length=20)
    notes = models.CharField(max_length=300, blank=True, null=True)
    promoted_by = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='promoted_by_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_promotion_event'
        managed = False


class AcpAuditEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    domain = models.CharField(max_length=50)
    action = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=60)
    entity_id = models.CharField(max_length=120)
    before_json = models.TextField(blank=True, null=True)
    after_json = models.TextField(blank=True, null=True)
    actor_user = models.ForeignKey(settings.AUTH_USER_MODEL, db_column='actor_user_id', on_delete=models.DO_NOTHING, blank=True, null=True)
    actor_username = models.CharField(max_length=120)
    actor_ip = models.CharField(max_length=64, blank=True, null=True)
    actor_user_agent = models.CharField(max_length=320, blank=True, null=True)
    environment = models.CharField(max_length=40)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'acp_audit_event'
        managed = False
