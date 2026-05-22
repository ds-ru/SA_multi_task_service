import asyncio

from pathlib import Path
import shutil
from typing import Optional, Any, List, Dict
from dataclasses import dataclass, field

from aiobotocore.session import get_session, AioSession
from aiobotocore.client import AioBaseClient
from aiobotocore.config import AioConfig

from config.service import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, OBJECT_STORAGE_ENDPOINT, OBJECT_STORAGE_BUCKET


@dataclass
class S3Config:
    access_key: str
    secret_key: str
    region_name: str
    bucket: str
    endpoint: str


@dataclass
class S3Client:
    config: S3Config
    client: Optional[AioBaseClient] = field(init=False, default=None)
    session: Optional[AioSession] = field(init=False, default=None)

    async def __aenter__ (self) -> "S3Client":
        boto_config = AioConfig(
            retries={
                'max_attempts': 5,
                'mode': 'adaptive'
            },
            connect_timeout=10,
            read_timeout=120,
            s3={
                'multipart_threshold': 10 * 1024 * 1024,
                'multipart_chunksize': 8 * 1024 * 1024,
                'max_concurrency': 10,
            }
        )

        self.session = get_session()
        self._client_context = self.session.create_client('s3',
             aws_access_key_id=self.config.access_key,
             aws_secret_access_key=self.config.secret_key,
             endpoint_url=self.config.endpoint,
             config=boto_config)
        self.client = await self._client_context.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.close()
        if self.session:
            pass

    @staticmethod
    def _make_s3_key(local_path: str, prefix: str = "") -> str:
        return f"{prefix}/{Path(local_path).name}".lstrip('/') if prefix else Path(local_path).name

    async def get_list(self, prefix: str = "") -> List[Dict[str, Any]]:
        if not self.client:
            raise RuntimeError("Сначала подключитесь через 'async with'")

        paginator = self.client.get_paginator('list_objects_v2')
        all_objects = []

        async for result in paginator.paginate(Bucket=self.config.bucket, Prefix=prefix):
            contents = result.get('Contents', [])
            all_objects.extend(contents)

        return all_objects

    async def get_object(self, key: str) -> bytes:
        if not self.client:
            raise RuntimeError("Сначала подключитесь через 'async with'")

        response = await self.client.get_object(
            Bucket=self.config.bucket,
            Key=key,
        )

        async with response["Body"] as stream:
            data = await stream.read()

        return data

async def download_s3_object(key: str) -> bytes:
    async with s3client as client:
        return await client.get_object(key)

s3conf = S3Config(access_key=AWS_ACCESS_KEY_ID,
                  secret_key=AWS_SECRET_ACCESS_KEY,
                  region_name="",
                  bucket=OBJECT_STORAGE_BUCKET,
                  endpoint=OBJECT_STORAGE_ENDPOINT,
                  )

s3client = S3Client(s3conf)


