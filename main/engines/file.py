from hashlib import sha3_256
from typing import Union

from six import BytesIO

from main import db, diskcache_client
from main.libs import s3
from main.models.file import FileModel

CACHE_TIMEOUT = 24 * 60 * 60  # 1 day


def upload_file(
    reference_type: str,
    reference_id: int,
    file_type: str,
    file_name: str,
    data: Union[BytesIO, bytes],
    file_path: str,
) -> FileModel:
    if isinstance(data, bytes):
        data = BytesIO(data)

    # Upload and upsert file
    file_url = s3.upload(
        # Need to create a new BytesIO object, since it will be closed after
        # uploading, while we still need to store the data in diskcache later
        BytesIO(data.getvalue()),
        file_path=file_path,
    )

    # Create a file model
    file_model_object = FileModel(
        name=file_name,
        url=file_url,
        type=file_type,
        reference_type=reference_type,
        reference_id=reference_id,
    )
    db.session.add(file_model_object)
    db.session.commit()

    # Update cached data
    cache_key = _get_cache_key(file_url)
    diskcache_client.set(
        key=cache_key,
        value=data.getvalue(),
        expire=CACHE_TIMEOUT,
    )

    return file_model_object


def download_file(file_url: str) -> BytesIO:
    cache_key = _get_cache_key(file_url)
    cached_data = diskcache_client.get(cache_key)
    if cached_data is not None:
        return BytesIO(cached_data)

    file_content, _, _ = s3.download(file_url)

    # Cache file content
    diskcache_client.set(
        key=cache_key,
        value=file_content.getvalue(),
        expire=CACHE_TIMEOUT,
    )

    return file_content


def _get_cache_key(file_url: str):
    return f'file:{sha3_256(file_url.encode()).hexdigest()}'
