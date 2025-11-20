import os
import json
from datetime import datetime, timedelta, timezone
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
from utils.utils import is_localhost

def create_cloud_task(
        endpoint: str, 
        payload: dict, 
        queue_name: str = os.environ.get('CLOUD_TASKS_CREATE_AND_BUILD_QUEUE', 'default'), 
        task_name: str = None,
        delay_seconds: int = None,
        headers: dict = None
    ):
    """
    Creates a Google Cloud Task with the specified endpoint and payload.
    Optionally sets a custom task name and delay.

    Args:
        endpoint (str): The endpoint URL where the task will be sent
        payload (dict): The payload data to be sent with the task
        queue_name (str): Queue name
        task_name (str, optional): Custom name for the task
        delay_seconds (int, optional): Delay in seconds before the task should run

    Returns:
        dict: Response containing task information or error details
    """
    if not is_localhost():
        try:
            project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
            location = os.environ.get('CLOUD_TASKS_LOCATION', 'us-central1')
            queue_name = queue_name

            if not project_id:
                return {
                    "status": "error",
                    "message": "GOOGLE_CLOUD_PROJECT environment variable not set"
                }

            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(project_id, location, queue_name)

            request_headers = {
                'Content-Type': 'application/json',
            }
            if headers:
                request_headers.update(headers)

            task = {
                'http_request': {
                    'http_method': tasks_v2.HttpMethod.POST,
                    'url': endpoint,
                    'headers': request_headers,
                    'body': json.dumps(payload).encode()
                }
            }

            # Add schedule_time if delay_seconds is provided
            if delay_seconds is not None:
                schedule_time = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(schedule_time)
                task['schedule_time'] = timestamp

            if task_name:
                task['name'] = client.task_path(project_id, location, queue_name, task_name)

            response = client.create_task(request={"parent": parent, "task": task})

            return {
                "status": "success",
                "message": "Cloud Task created successfully",
                "task_name": response.name,
                "task_id": response.name.split('/')[-1]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create Cloud Task: {str(e)}"
            }
    else:
        return {
            "status": "warning",
            "message": "Can't run Cloud Tasks locally"
        }