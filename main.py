import json
import base64
import logging
from google.cloud import storage
from decouple import config
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

"""
env
GCS_SERVICE_ACCOUNT=base64_string
GCS_BUCKET_NAME=pdf_scraped_data
"""


class GCSUploader:

    def __init__(
        self, bucket_name, credentials_base64: str = config("GCS_SERVICE_ACCOUNT")
    ):
        self.bucket_name = bucket_name
        self.credentials_base64 = credentials_base64
        logger.info("GCSUploader initialized for bucket: %s", bucket_name)

    def __upload_to_gcs(
        self,
        bucket_name: str,
        source_file_path: str,
        destination_blob_name: str,
        credentials_json: dict,
        is_file_object: bool = False,
    ):
        try:
            client = storage.Client.from_service_account_info(credentials_json)
            bucket = client.get_bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            if is_file_object:
                blob.upload_from_file(source_file_path)
            else:
                blob.upload_from_filename(source_file_path)
            logger.info(
                "File %s uploaded to %s in bucket %s.",
                source_file_path,
                destination_blob_name,
                bucket_name,
            )
        except Exception as e:
            logger.error(
                "Failed to upload file %s to %s: %s",
                source_file_path,
                destination_blob_name,
                str(e),
            )

    def __bs64_to_dict(self, bs64_str):
        try:
            decoded_json = json.loads(base64.b64decode(bs64_str).decode("utf-8"))
            return decoded_json
        except Exception as e:
            logger.error("Failed to decode service account credentials: %s", str(e))
            raise

    def upload(self, source_file_path: str, destination_blob_name: str):
        credentials_json = self.__bs64_to_dict(self.credentials_base64)
        self.__upload_to_gcs(
            self.bucket_name, source_file_path, destination_blob_name, credentials_json
        )


if __name__ == "__main__":
    bucket_name = config("GCS_BUCKET_NAME")
    uploader = GCSUploader(bucket_name=bucket_name)
    folder = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = "sample.txt"
    uploader.upload(file_name, f"{folder}/{file_name}")
