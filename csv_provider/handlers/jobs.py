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
import json
import time
import multiprocessing
import signal
import sys


logger = getLogger(__name__.split(".", 1)[-1])


def handle_sigterm(signo, stack_frame):
    logger.debug("got signal '{}' - exiting ...".format(signo))
    sys.exit(0)


class Result:
    def __init__(self):
        self.data_item: typing.Optional[models.DataItem] = None
        self.job: typing.Optional[models.Job] = None
        self.error = False


class Worker(multiprocessing.Process):
    def __init__(self, job: models.Job, data_item: models.DataItem, data_handler: handlers.Data):
        super().__init__(name="jobs-worker-{}".format(job.id), daemon=True)
        self.__data_item = data_item
        self.__data_handler = data_handler
        self.__job = job
        self.result = multiprocessing.Queue()

    def run(self) -> None:
        signal.signal(signal.SIGTERM, handle_sigterm)
        signal.signal(signal.SIGINT, handle_sigterm)
        result_obj = Result()
        try:
            logger.debug("starting job '{}' ...".format(self.__job.id))
            self.__job.status = models.JobStatus.running
            old_file = self.__data_item.file
            result_obj.data_item = self.__data_handler.create(self.__data_item.source_id, self.__data_item.time_field, self.__data_item.delimiter)
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
            result_obj.error = True
        result_obj.job = self.__job
        self.result.put(result_obj)


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
            try:
                if len(self.__worker_pool) < self.__max_jobs:
                    try:
                        job_id = self.__job_queue.get(timeout=self.__check_delay)
                        worker = Worker(
                            job=self.__job_pool[job_id],
                            data_item=models.DataItem(json.loads(self.__db_handler.get(b"data-", self.__job_pool[job_id].source_id.encode()))),
                            data_handler=self.__data_handler
                        )
                        self.__worker_pool[job_id] = worker
                        worker.start()
                    except queue.Empty:
                        pass
                else:
                    time.sleep(self.__check_delay)
                for job_id in list(self.__worker_pool.keys()):
                    if not self.__worker_pool[job_id].is_alive():
                        res = self.__worker_pool[job_id].result.get()
                        self.__db_handler.put(b"jobs-", res.job.id.encode(), json.dumps(dict(res.job)).encode())
                        if not res.error:
                            self.__db_handler.put(b"data-", res.data_item.source_id.encode(), json.dumps(dict(res.data_item)).encode())
                        self.__worker_pool[job_id].close()
                        del self.__worker_pool[job_id]
                        del self.__job_pool[job_id]
                        # self.__db_handler.delete(b"jobs-", job_id.encode())
            except Exception as ex:
                logger.error("job handling failed - {}".format(ex))
