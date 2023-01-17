# TODO: to be open sourced
import os
from io import BytesIO
from time import time
from typing import BinaryIO

import boto3

from main import config
from main.libs.log import ServiceLogger

logger = ServiceLogger(__name__)


def upload(file_: BinaryIO, file_path: str) -> str:
    """
    Upload a file to s3

    :param file_: file-like object (supports read() method).
    :param file_path: path to file, S3 prefix not included.
    :return: uploaded url
    """

    file_key = generate_file_key(file_path)

    logger.debug(
        message='Start uploading file to S3',
        data={
            'file_key': file_key,
        },
    )
    start_time = time()

    # IMPORTANT: move the cursor to the beginning of the file
    file_.seek(0, 0)

    s3 = _get_s3_client()
    s3.upload_fileobj(
        Fileobj=file_,
        Bucket=config.AWS_S3_BUCKET_NAME,
        Key=file_key,
    )

    end_time = time()
    logger.debug(
        message='Finish uploading file to S3',
        data={
            'file_key': file_key,
            'duration': end_time - start_time,
        },
    )

    return generate_file_url(file_path)


def download(file_url: str):
    """
    Download a file from s3

    :param file_url: a s3 file url
    :return: a tuple contains a file-like object, filename, content_type
    """

    logger.debug(
        message='Start downloading file from S3',
        data={
            'url': file_url,
        },
    )
    start_time = time()

    file_key = _get_file_key_from_url(file_url)
    s3 = _get_s3_client()
    s3_response_object = s3.get_object(
        Bucket=config.AWS_S3_BUCKET_NAME,
        Key=file_key,
    )
    file_ = s3_response_object['Body']

    end_time = time()
    logger.debug(
        message='Finish downloading file from S3',
        data={
            'file_key': file_key,
            'duration': end_time - start_time,
        },
    )

    return (
        BytesIO(file_.read()),
        file_key.split('/')[-1],
        s3_response_object['ContentType'],
    )


def copy(source_path: str, destination_path: str):
    """
    Make a copy of an existing file on the same bucket in S3
    :param source_path: source s3 file path
    :param destination_path: destination s3 file path
    :return: new file url
    """

    source_file_key = generate_file_key(source_path)
    destination_file_key = generate_file_key(destination_path)

    logger.debug(
        message='Start copying file in S3',
        data={
            'source_file_key': source_file_key,
            'destination_file_key': destination_file_key,
        },
    )
    start_time = time()

    s3 = _get_s3_client()
    s3.copy(
        CopySource={
            'Bucket': config.AWS_S3_BUCKET_NAME,
            'Key': source_file_key,
        },
        Bucket=config.AWS_S3_BUCKET_NAME,
        Key=destination_file_key,
    )

    end_time = time()
    logger.debug(
        message='Finish copying file in S3',
        data={
            'source_file_key': source_file_key,
            'destination_file_key': destination_file_key,
            'duration': end_time - start_time,
        },
    )

    return generate_file_url(destination_path)


def generate_file_key(file_path: str) -> str:
    return os.path.join(
        config.AWS_FILE_PATH_PREFIX,
        file_path,
    )


def generate_file_url(file_path: str) -> str:
    key = generate_file_key(file_path)
    return os.path.join(config.AWS_S3_URL, key)


def generate_presigned_url(file_url, expire_time=900) -> str:
    """
    Generate a presigned url for an existing s3 file

    :param file_url: an s3 file url
    :param expire_time: time to expiration in seconds
    :return: s3 presigned url
    """
    file_key = _get_file_key_from_url(file_url)
    s3 = _get_s3_client()
    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': config.AWS_S3_BUCKET_NAME,
            'Key': file_key,
        },
        ExpiresIn=expire_time,
    )
    return presigned_url


def _get_s3_client():
    session = boto3.Session(
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    )
    return session.client('s3')


def _get_file_key_from_url(s3_url):
    return s3_url.replace(f'{config.AWS_S3_URL}/', '')
