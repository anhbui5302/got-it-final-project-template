import zipfile
from typing import Any, Dict, Optional

from six import BytesIO

from main import config
from main.commons import exceptions
from main.core import (
    handle_config_api_exception,
    handle_deepsearch_api_exception,
    handle_pfd_api_exception,
)
from main.engines.async_task.schemas import ExceptionInfo, Result
from main.engines.async_task.tasks.base import BaseAsyncTask
from main.engines.file import upload_file
from main.engines.project import generate_export_file_path
from main.engines.pusher import trigger_async_task_status_changed
from main.enums import (
    AsyncTaskStatus,
    AutoflowState,
    BotType,
    FileReferenceType,
    FileType,
    ProjectExportFileName,
    ProjectExportServiceFileName,
    ProjectExportType,
)
from main.libs.s3 import generate_presigned_url
from main.libs.utils import get_config_api_sdk, get_deepsearch_api_sdk, get_pfd_api_sdk
from main.models.async_task import AsyncTaskModel


class ExportProject(BaseAsyncTask):
    def __init__(self, task: AsyncTaskModel):
        super().__init__(task)
        self.file_url = None

    def execute(self) -> Result:
        return_value = self.export_project(
            *self.task.meta_data.args,
            **self.task.meta_data.kwargs,
        )
        self.file_url = return_value
        return Result(return_value=return_value)

    @handle_config_api_exception
    @handle_deepsearch_api_exception
    @handle_pfd_api_exception
    def export_project(
        self,
        account_id: int,
        project_id: int,
        organization_id: int,
        export_types: list,
        export_connections: bool,
    ):
        config_api = get_config_api_sdk()
        deepsearch_api = get_deepsearch_api_sdk()
        pfd_api = get_pfd_api_sdk()

        autoflows = config_api.get_autoflows(
            project_id=project_id, organization_id=organization_id
        )
        config_api_response = deepsearch_api_response = pfd_api_response = None
        for export_type in export_types:
            if export_type == ProjectExportType.PROJECT_SETTINGS:
                # Export project
                config_api_response = config_api.export_project_data(
                    organization_id, project_id, export_connections
                )
            elif export_type == ProjectExportType.FAQ:
                # Export FAQ Bot
                faq_autoflow = [
                    autoflow
                    for autoflow in autoflows
                    if autoflow['bot_type'] == BotType.FAQ
                ][0]
                graph_id = faq_autoflow.get('meta_data', {}).get('graph_id')
                if faq_autoflow['state'] != AutoflowState.BOT_CREATED:
                    raise exceptions.BadRequest(error_message='FAQ Bot is not created.')

                deepsearch_api_response = deepsearch_api.export_project_graph(
                    project_id, graph_id
                )
            elif export_type == ProjectExportType.CONVERSATIONAL:
                # Export Conv Bot
                conv_autoflow = [
                    autoflow
                    for autoflow in autoflows
                    if autoflow['bot_type'] == BotType.CONVERSATIONAL
                ][0]
                if conv_autoflow['state'] != AutoflowState.BOT_CREATED:
                    raise exceptions.BadRequest(
                        error_message='Conversational Bot is not created.'
                    )
                sessions = pfd_api.get_sessions(project_id)
                latest_session = max(sessions['items'], key=lambda x: x['id'])
                pfd_api_response = pfd_api.export_session(latest_session['id'])

        response_list = [config_api_response, deepsearch_api_response, pfd_api_response]
        # Don't include zips for services that are not exported.
        project_data = {
            k: v
            for (k, v) in tuple(
                zip(ProjectExportServiceFileName.get_list(), response_list)
            )
            if v is not None
        }
        # Zip responses and upload to s3
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            for file_name, data in project_data.items():
                zip_file.writestr(file_name, data)

        file = upload_file(
            reference_type=FileReferenceType.PROJECT,
            reference_id=project_id,
            file_type=FileType.EXPORT,
            file_name=ProjectExportFileName.EXPORT,
            data=zip_buffer,
            file_path=generate_export_file_path(
                project_id, ProjectExportFileName.EXPORT
            ),
        )

        file_url = generate_presigned_url(
            file.url, config.UPLOADED_FILE_EXPIRATION_IN_SECONDS
        )
        return file_url

    def _notify_status_changed(
        self,
        status: str,
        file_url: Optional[Dict] = None,
    ):

        data = {
            'id': self.task.id,
            'project_id': self.task.meta_data.kwargs.get('id'),
            'status': status,
        }

        if file_url is not None:
            data['file_url'] = file_url

        trigger_async_task_status_changed(data)

    def on_running(self):
        super().on_running()
        self._notify_status_changed(AsyncTaskStatus.RUNNING)

    def on_success(self, return_value: Optional[Any]):
        super().on_success(return_value)
        self._notify_status_changed(
            AsyncTaskStatus.SUCCESS,
            file_url=self.file_url,
        )

    def on_timed_out(self):
        super().on_timed_out()
        self._notify_status_changed(
            AsyncTaskStatus.TIMED_OUT,
        )

    def on_exception(self, e: ExceptionInfo):
        super().on_exception(e)
        self._notify_status_changed(AsyncTaskStatus.FAILED)
