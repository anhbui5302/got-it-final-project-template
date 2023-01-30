from .base import EnumBase

BASE_PROJECT_PATH = '/organizations/<int:organization_id>/projects/<int:project_id>'


class TokenType(EnumBase):
    REFRESH_TOKEN = 'refresh_token'


class AccountStatus(EnumBase):
    DELETED = 'deleted'
    ACTIVE = 'active'


class AudienceType:
    ACCOUNT = 'account'
    APPLICATION = 'application'


class ProjectRasaEnvironment(EnumBase):
    STAGING = 'staging'
    PRODUCTION = 'production'


class ApplicationStatus(EnumBase):
    DELETED = 'deleted'
    ACTIVE = 'active'


class PusherEvent:
    RASA_STATUS_CHANGED = 'rasa_status_changed'
    ASYNC_TASK_STATUS_CHANGED = 'async_task_status_changed'


class FileReferenceType(EnumBase):
    PROJECT = 'project'


class FileType(EnumBase):
    EXPORT = 'export'
    IMPORT = 'import'


class BotType(EnumBase):
    FAQ = 'faq'
    CONVERSATIONAL = 'conversational'


class ProjectExportServiceFileName(EnumBase):
    CONFIG_API = 'config_api.zip'
    DEEPSEARCH_API = 'deepsearch_api.zip'
    PFD_API = 'pfd_api.zip'


class ProjectImportServiceFileName(ProjectExportServiceFileName):
    pass


class ProjectExportFileName(EnumBase):
    EXPORT = 'export.zip'


class ProjectImportFileName(EnumBase):
    IMPORT = 'import.zip'


class ProjectExportType(EnumBase):
    PROJECT_SETTINGS = 'project_settings'
    FAQ = 'faq'
    CONVERSATIONAL = 'conversational'


class AutoflowState(EnumBase):
    BOT_CREATED = 'bot_created'


class ProjectImportFileExtension(EnumBase):
    ZIP = '.zip'


class AsyncTaskStatus(EnumBase):
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILED = 'failed'
    TIMED_OUT = 'timed_out'


class AsyncTaskReferenceType(EnumBase):
    SESSION = 'session'
    PROJECT = 'project'


class AsyncTaskModule(EnumBase):
    PROJECT = 'project'


class OrganizationTier(EnumBase):
    SELECT = 'select'
    PRO = 'pro'
    ENTERPRISE = 'enterprise'
    QUICKSTART = 'quickstart'


class EventName(EnumBase):
    IMPORT = 'import'
    EXPORT = 'export'
    CREATE_RASA = 'create_rasa'
    CHANGE_TIER = 'change_tier'
    CREATE_ORGANIZATION = 'create_organization'
    ADD_ADMIN = 'add_admin'
    EDIT_ADMIN = 'edit_admin'
