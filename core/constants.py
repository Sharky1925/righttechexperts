WORKFLOW_DRAFT = 'draft'
WORKFLOW_REVIEW = 'review'
WORKFLOW_APPROVED = 'approved'
WORKFLOW_PUBLISHED = 'published'
WORKFLOW_STATUSES = (
    WORKFLOW_DRAFT,
    WORKFLOW_REVIEW,
    WORKFLOW_APPROVED,
    WORKFLOW_PUBLISHED,
)
WORKFLOW_STATUS_LABELS = {
    WORKFLOW_DRAFT: 'Draft',
    WORKFLOW_REVIEW: 'In Review',
    WORKFLOW_APPROVED: 'Approved',
    WORKFLOW_PUBLISHED: 'Published',
}

ROLE_OWNER = 'owner'
ROLE_ADMIN = 'admin'
ROLE_PUBLISHER = 'publisher'
ROLE_REVIEWER = 'reviewer'
ROLE_EDITOR = 'editor'
ROLE_SUPPORT = 'support'
USER_ROLE_CHOICES = (
    ROLE_OWNER,
    ROLE_ADMIN,
    ROLE_PUBLISHER,
    ROLE_REVIEWER,
    ROLE_EDITOR,
    ROLE_SUPPORT,
)
USER_ROLE_LABELS = {
    ROLE_OWNER: 'Owner',
    ROLE_ADMIN: 'Admin',
    ROLE_PUBLISHER: 'Publisher',
    ROLE_REVIEWER: 'Reviewer',
    ROLE_EDITOR: 'Editor',
    ROLE_SUPPORT: 'Support',
}
ROLE_DEFAULT = ROLE_ADMIN
ROLE_PERMISSIONS = {
    ROLE_OWNER: {
        'dashboard:view',
        'content:manage',
        'workflow:review',
        'workflow:publish',
        'support:manage',
        'security:view',
        'settings:manage',
        'users:manage',
        'acp:studio:view',
        'acp:pages:manage',
        'acp:dashboards:manage',
        'acp:registry:manage',
        'acp:metrics:manage',
        'acp:content:manage',
        'acp:theme:manage',
        'acp:mcp:manage',
        'acp:publish',
        'acp:audit:view',
        'acp:mcp:audit:view',
        'acp:environments:manage',
    },
    ROLE_ADMIN: {
        'dashboard:view',
        'content:manage',
        'workflow:review',
        'workflow:publish',
        'support:manage',
        'security:view',
        'settings:manage',
        'users:manage',
        'acp:studio:view',
        'acp:pages:manage',
        'acp:dashboards:manage',
        'acp:registry:manage',
        'acp:metrics:manage',
        'acp:content:manage',
        'acp:theme:manage',
        'acp:mcp:manage',
        'acp:publish',
        'acp:audit:view',
        'acp:mcp:audit:view',
        'acp:environments:manage',
    },
    ROLE_PUBLISHER: {
        'dashboard:view',
        'content:manage',
        'workflow:review',
        'workflow:publish',
        'acp:studio:view',
        'acp:pages:manage',
        'acp:dashboards:manage',
        'acp:content:manage',
        'acp:theme:manage',
        'acp:publish',
    },
    ROLE_REVIEWER: {
        'dashboard:view',
        'content:manage',
        'workflow:review',
        'acp:studio:view',
        'acp:pages:manage',
        'acp:dashboards:manage',
        'acp:content:manage',
        'acp:theme:manage',
    },
    ROLE_EDITOR: {
        'dashboard:view',
        'content:manage',
        'acp:studio:view',
        'acp:pages:manage',
        'acp:content:manage',
        'acp:theme:manage',
    },
    ROLE_SUPPORT: {
        'dashboard:view',
        'support:manage',
        'acp:studio:view',
    },
}

ORANGE_COUNTY_CA_CITIES = (
    'Aliso Viejo',
    'Anaheim',
    'Brea',
    'Buena Park',
    'Costa Mesa',
    'Cypress',
    'Dana Point',
    'Fountain Valley',
    'Fullerton',
    'Garden Grove',
    'Huntington Beach',
    'Irvine',
    'La Habra',
    'La Palma',
    'Laguna Beach',
    'Laguna Hills',
    'Laguna Niguel',
    'Laguna Woods',
    'Lake Forest',
    'Los Alamitos',
    'Mission Viejo',
    'Newport Beach',
    'Orange',
    'Placentia',
    'Rancho Santa Margarita',
    'San Clemente',
    'San Juan Capistrano',
    'Santa Ana',
    'Seal Beach',
    'Stanton',
    'Tustin',
    'Villa Park',
    'Westminster',
    'Yorba Linda',
)

SUPPORT_TICKET_STATUS_OPEN = 'open'
SUPPORT_TICKET_STATUS_IN_PROGRESS = 'in_progress'
SUPPORT_TICKET_STATUS_WAITING_CUSTOMER = 'waiting_customer'
SUPPORT_TICKET_STATUS_RESOLVED = 'resolved'
SUPPORT_TICKET_STATUS_CLOSED = 'closed'
SUPPORT_TICKET_STATUSES = (
    SUPPORT_TICKET_STATUS_OPEN,
    SUPPORT_TICKET_STATUS_IN_PROGRESS,
    SUPPORT_TICKET_STATUS_WAITING_CUSTOMER,
    SUPPORT_TICKET_STATUS_RESOLVED,
    SUPPORT_TICKET_STATUS_CLOSED,
)
SUPPORT_TICKET_STATUS_LABELS = {
    SUPPORT_TICKET_STATUS_OPEN: 'Open',
    SUPPORT_TICKET_STATUS_IN_PROGRESS: 'In Progress',
    SUPPORT_TICKET_STATUS_WAITING_CUSTOMER: 'Waiting on Client',
    SUPPORT_TICKET_STATUS_RESOLVED: 'Done',
    SUPPORT_TICKET_STATUS_CLOSED: 'Closed',
}
SUPPORT_TICKET_STAGE_PENDING = 'pending'
SUPPORT_TICKET_STAGE_DONE = 'done'
SUPPORT_TICKET_STAGE_CLOSED = 'closed'
SUPPORT_TICKET_STAGE_LABELS = {
    SUPPORT_TICKET_STAGE_PENDING: 'Pending',
    SUPPORT_TICKET_STAGE_DONE: 'Done',
    SUPPORT_TICKET_STAGE_CLOSED: 'Closed',
}
SUPPORT_TICKET_PENDING_STATUSES = {
    SUPPORT_TICKET_STATUS_OPEN,
    SUPPORT_TICKET_STATUS_IN_PROGRESS,
    SUPPORT_TICKET_STATUS_WAITING_CUSTOMER,
}
SUPPORT_TICKET_STAGE_TO_STATUS = {
    SUPPORT_TICKET_STAGE_PENDING: SUPPORT_TICKET_STATUS_IN_PROGRESS,
    SUPPORT_TICKET_STAGE_DONE: SUPPORT_TICKET_STATUS_RESOLVED,
    SUPPORT_TICKET_STAGE_CLOSED: SUPPORT_TICKET_STATUS_CLOSED,
}
SUPPORT_TICKET_EVENT_CREATED = 'created'
SUPPORT_TICKET_EVENT_REVIEW_ACTION = 'review_action'
SUPPORT_TICKET_EVENT_ADMIN_UPDATE = 'admin_update'

MCP_OPERATION_STATUS_PENDING_APPROVAL = 'pending_approval'
MCP_OPERATION_STATUS_QUEUED = 'queued'
MCP_OPERATION_STATUS_RUNNING = 'running'
MCP_OPERATION_STATUS_SUCCEEDED = 'succeeded'
MCP_OPERATION_STATUS_FAILED = 'failed'
MCP_OPERATION_STATUS_BLOCKED = 'blocked'
MCP_OPERATION_STATUS_REJECTED = 'rejected'
MCP_OPERATION_STATUSES = (
    MCP_OPERATION_STATUS_PENDING_APPROVAL,
    MCP_OPERATION_STATUS_QUEUED,
    MCP_OPERATION_STATUS_RUNNING,
    MCP_OPERATION_STATUS_SUCCEEDED,
    MCP_OPERATION_STATUS_FAILED,
    MCP_OPERATION_STATUS_BLOCKED,
    MCP_OPERATION_STATUS_REJECTED,
)
MCP_APPROVAL_STATUS_PENDING = 'pending'
MCP_APPROVAL_STATUS_APPROVED = 'approved'
MCP_APPROVAL_STATUS_REJECTED = 'rejected'
MCP_APPROVAL_STATUS_NOT_REQUIRED = 'not_required'


def normalize_workflow_status(value, default=WORKFLOW_DRAFT):
    candidate = (value or '').strip().lower()
    if candidate in WORKFLOW_STATUSES:
        return candidate
    return default


def normalize_user_role(value, default=ROLE_DEFAULT):
    candidate = (value or '').strip().lower()
    if candidate in USER_ROLE_CHOICES:
        return candidate
    return default


def normalize_support_ticket_status(value, default=SUPPORT_TICKET_STATUS_OPEN):
    candidate = (value or '').strip().lower()
    alias_map = {
        'pending': SUPPORT_TICKET_STAGE_TO_STATUS[SUPPORT_TICKET_STAGE_PENDING],
        'in-progress': SUPPORT_TICKET_STATUS_IN_PROGRESS,
        'waiting': SUPPORT_TICKET_STATUS_WAITING_CUSTOMER,
        'waiting-on-client': SUPPORT_TICKET_STATUS_WAITING_CUSTOMER,
        'done': SUPPORT_TICKET_STAGE_TO_STATUS[SUPPORT_TICKET_STAGE_DONE],
        'complete': SUPPORT_TICKET_STAGE_TO_STATUS[SUPPORT_TICKET_STAGE_DONE],
        'completed': SUPPORT_TICKET_STAGE_TO_STATUS[SUPPORT_TICKET_STAGE_DONE],
        'close': SUPPORT_TICKET_STAGE_TO_STATUS[SUPPORT_TICKET_STAGE_CLOSED],
    }
    normalized = alias_map.get(candidate, candidate)
    if normalized in SUPPORT_TICKET_STATUSES:
        return normalized
    return default


def support_ticket_stage_for_status(status):
    normalized = normalize_support_ticket_status(status, default=SUPPORT_TICKET_STATUS_OPEN)
    if normalized in SUPPORT_TICKET_PENDING_STATUSES:
        return SUPPORT_TICKET_STAGE_PENDING
    if normalized == SUPPORT_TICKET_STATUS_RESOLVED:
        return SUPPORT_TICKET_STAGE_DONE
    return SUPPORT_TICKET_STAGE_CLOSED


def normalize_support_ticket_stage(value, default=SUPPORT_TICKET_STAGE_PENDING):
    candidate = (value or '').strip().lower()
    if candidate in SUPPORT_TICKET_STAGE_TO_STATUS:
        return candidate
    return default
