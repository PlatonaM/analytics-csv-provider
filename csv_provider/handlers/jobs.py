"""
   Copyright 2021 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

__all__ = ("Jobs",)


from ..logger import getLogger
from .. import models
from .. import handlers
import threading
import queue
import typing
import uuid
import datetime
import base64
import gzip
import json
import time


logger = getLogger(__name__.split(".", 1)[-1])


class Worker(threading.Thread):
    def __init__(self, job: models.Job, db_handler: handlers.DB, data_handler: handlers.Data):
        super().__init__(name="jobs-worker-{}".format(job.id), daemon=True)
        self.__db_handler = db_handler
        self.__data_handler = data_handler
        self.__job = job
        self.done = False

    def run(self) -> None:
        try:
            logger.debug("starting job '{}' ...".format(self.__job.id))
            self.__job.status = models.JobStatus.running
            data_item = models.DataItem(json.loads(self.__db_handler.get(b"data-", self.__job.source_id.encode())))
            old_file = data_item.file
            data_item = self.__data_handler.create(data_item.source_id, data_item.time_field, data_item.delimiter)
            self.__db_handler.put(b"data-", data_item.source_id.encode(), json.dumps(dict(data_item)).encode())
            if old_file:
                try:
                    self.__data_handler.remove(old_file)
                except Exception as ex:
                    logger.warning("{}: could not remove old file - {}".format(self.__job.id, ex))
            self.__job.status = models.JobStatus.finished
            logger.debug("{}: completed successfully".format(self.__job.id))
        except Exception as ex:
            self.__job.status = models.JobStatus.failed
            self.__job.reason = str(ex)
            logger.error("{}: failed - {}".format(self.__job.id, ex))
        self.__db_handler.put(b"jobs-", self.__job.id.encode(), json.dumps(dict(self.__job)).encode())
        self.done = True


class Jobs(threading.Thread):
    def __init__(self, db_handler: handlers.DB, data_handler: handlers.Data, check_delay: typing.Union[int, float], max_jobs: int):
        super().__init__(name="jobs-handler", daemon=True)
        self.__db_handler = db_handler
        self.__data_handler = data_handler
        self.__check_delay = check_delay
        self.__max_jobs = max_jobs
        self.__job_queue = queue.Queue()
        self.__job_pool: typing.Dict[str, models.Job] = dict()
        self.__worker_pool: typing.Dict[str, Worker] = dict()

    def create(self, source_id: str) -> str:
        for job in self.__job_pool.values():
            if job.source_id == source_id:
                logger.debug("job for source '{}' already exists".format(source_id))
                return job.id
        job = models.Job()
        job.id = uuid.uuid4().hex
        job.source_id = source_id
        job.created = "{}Z".format(datetime.datetime.utcnow().isoformat())
        self.__job_pool[job.id] = job
        logger.debug("created job for source '{}'".format(source_id))
        self.__job_queue.put_nowait(job.id)
        return job.id

    def get_job(self, job_id: str) -> models.Job:
        return self.__job_pool[job_id]

    def list_jobs(self) -> list:
        return list(self.__job_pool.keys())

    def run(self):
        while True:
            if len(self.__worker_pool) < self.__max_jobs:
                try:
                    job_id = self.__job_queue.get(timeout=self.__check_delay)
                    worker = Worker(
                        job=self.__job_pool[job_id],
                        db_handler=self.__db_handler,
                        data_handler=self.__data_handler
                    )
                    self.__worker_pool[job_id] = worker
                    worker.start()
                except queue.Empty:
                    pass
            else:
                time.sleep(self.__check_delay)
            for job_id in list(self.__worker_pool.keys()):
                if self.__worker_pool[job_id].done:
                    del self.__worker_pool[job_id]
                    del self.__job_pool[job_id]
                    # self.__db_handler.delete(b"jobs-", job_id.encode())
