from typing import Any, Optional

from main.commons import exceptions
from main.core import (
    handle_config_api_exception,
    handle_deepsearch_api_exception,
    handle_pfd_api_exception,
)
from main.engines.async_task.schemas import ExceptionInfo, Result
from main.engines.async_task.tasks.base import BaseAsyncTask
from main.engines.exceptions import NoValidImportFileException
from main.engines.file import download_file
from main.engines.project import unzip_import_file
from main.engines.pusher import trigger_async_task_status_changed
from main.enums import (
    IMPORT_TYPE_TO_SERVICE_FILE_NAME_MAPPING,
    AsyncTaskStatus,
    AutoflowState,
    BotType,
    ProjectImportServiceFileName,
)
from main.libs.utils import get_config_api_sdk, get_deepsearch_api_sdk, get_pfd_api_sdk
from main.models.async_task import AsyncTaskModel


class ImportProject(BaseAsyncTask):
    def __init__(self, task: AsyncTaskModel):
        super().__init__(task)
        self.file_url = None

    def execute(self) -> Result:
        return_value = self.import_project(
            *self.task.meta_data.args,
            **self.task.meta_data.kwargs,
        )

        return Result(return_value=return_value)

    @handle_config_api_exception
    @handle_deepsearch_api_exception
    @handle_pfd_api_exception
    def import_project(
        self,
        project_id: int,
        organization_id: int,
        file_url: str,
        import_types: list,
        import_connections: bool,
    ):

        zipped_file = download_file(file_url)
        try:
            unzipped_files = unzip_import_file(zipped_file)
        except NoValidImportFileException as e:
            raise exceptions.BadRequest(error_message=e.message)

        unzipped_file_names = [file['name'] for file in unzipped_files]
        for import_type in import_types:
            required_file_name = IMPORT_TYPE_TO_SERVICE_FILE_NAME_MAPPING[import_type]
            if required_file_name not in unzipped_file_names:
                raise exceptions.BadRequest(
                    error_message=f'{import_type} specified for import but {required_file_name} is not in uploaded file.'
                )

        config_api = get_config_api_sdk()
        deepsearch_api = get_deepsearch_api_sdk()
        pfd_api = get_pfd_api_sdk()
        autoflows = config_api.get_autoflows(
            project_id=project_id, organization_id=organization_id
        )
        required_file_names = [
            IMPORT_TYPE_TO_SERVICE_FILE_NAME_MAPPING[import_type]
            for import_type in import_types
        ]
        # Import project settings
        if ProjectImportServiceFileName.CONFIG_API in required_file_names:
            config_api_file = [
                file
                for file in unzipped_files
                if file['name'] == ProjectImportServiceFileName.CONFIG_API
            ][0]
            config_api.import_project_data(
                project_id=project_id,
                organization_id=organization_id,
                file_tuple=(config_api_file['name'], config_api_file['content']),
                copy_connections=import_connections,
            )
        # Import FAQ Bot
        elif ProjectImportServiceFileName.DEEPSEARCH_API in required_file_names:
            deepsearch_api_file = [
                file
                for file in unzipped_files
                if file['name'] == ProjectImportServiceFileName.DEEPSEARCH_API
            ][0]
            faq_autoflow = [
                autoflow
                for autoflow in autoflows
                if autoflow['bot_type'] == BotType.FAQ
            ][0]
            if faq_autoflow['state'] != AutoflowState.BOT_CREATED:
                raise exceptions.BadRequest(error_message='FAQ Bot is not created.')

            response = deepsearch_api.import_project_graph(
                project_id=project_id,
                file_tuple=(
                    deepsearch_api_file['name'],
                    deepsearch_api_file['content'],
                ),
            )
            new_graph_id = response.get('id')
            # After importing FAQ graph, update autoflow meta_data with new graph id
            faq_autoflow = config_api.get_autoflow(
                bot_type=BotType.FAQ,
                project_id=project_id,
                organization_id=organization_id,
            )
            payload = {'meta_data': {'graph_id': new_graph_id}}
            config_api.update_autoflow(
                project_id=project_id,
                organization_id=organization_id,
                autoflow_id=faq_autoflow['id'],
                payload=payload,
            )
        # Import Conversational Bot
        elif ProjectImportServiceFileName.PFD_API in required_file_names:
            pfd_api_file = [
                file
                for file in unzipped_files
                if file['name'] == ProjectImportServiceFileName.PFD_API
            ][0]

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
            if not sessions:
                raise exceptions.BadRequest(
                    error_message='Project does not have any session.'
                )
            latest_session = max(sessions['items'], key=lambda x: x['id'])
            pfd_api.import_session(
                latest_session['id'],
                file_tuple=(pfd_api_file['name'], pfd_api_file['content']),
            )

        return {}

    def _notify_status_changed(
        self,
        status: str,
    ):

        data = {
            'id': self.task.id,
            'project_id': self.task.meta_data.kwargs.get('id'),
            'status': status,
        }

        trigger_async_task_status_changed(data)

    def on_running(self):
        super().on_running()
        self._notify_status_changed(AsyncTaskStatus.RUNNING)

    def on_success(self, return_value: Optional[Any]):
        super().on_success(return_value)
        self._notify_status_changed(
            AsyncTaskStatus.SUCCESS,
        )

    def on_timed_out(self):
        super().on_timed_out()
        self._notify_status_changed(
            AsyncTaskStatus.TIMED_OUT,
        )

    def on_exception(self, e: ExceptionInfo):
        super().on_exception(e)
        self._notify_status_changed(AsyncTaskStatus.FAILED)
