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

__all__ = ("DataCollection", "DataResource", "Jobs", "Job", "CSV")


from .logger import getLogger
from . import handlers
from . import models
import falcon
import json


logger = getLogger(__name__.split(".", 1)[-1])


def reqDebugLog(req):
    logger.debug("method='{}' path='{}' content_type='{}'".format(req.method, req.path, req.content_type))


def reqErrorLog(req, ex):
    logger.error("method='{}' path='{}' - {}".format(req.method, req.path, ex))


class DataCollection:
    def __init__(self, db_handler: handlers.DB):
        self.__db_handler = db_handler

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(self.__db_handler.list_keys(b"data-"))
            resp.status = falcon.HTTP_200
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)

    def on_post(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            data_item = models.DataItem(json.load(req.bounded_stream))
            try:
                self.__db_handler.get(b"data-", data_item.source_id.encode())
                resp.status = falcon.HTTP_200
            except KeyError:
                if not all((data_item.source_id, data_item.time_field, data_item.delimiter)):
                    raise ValueError("incomplete request")
                self.__db_handler.put(b"data-", data_item.source_id.encode(), json.dumps(dict(data_item)).encode())
                resp.status = falcon.HTTP_201
        except ValueError as ex:
            resp.status = falcon.HTTP_400
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)


class DataResource:
    def __init__(self, db_handler: handlers.DB, data_handler: handlers.Data):
        self.__db_handler = db_handler
        self.__data_handler = data_handler

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, source_id: str):
        reqDebugLog(req)
        try:
            resp.content_type = falcon.MEDIA_JSON
            resp.body = self.__db_handler.get(b"data-", source_id.encode())
            resp.status = falcon.HTTP_200
        except KeyError as ex:
            resp.status = falcon.HTTP_404
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)

    def on_delete(self, req: falcon.request.Request, resp: falcon.response.Response, source_id: str):
        reqDebugLog(req)
        try:
            data_item = models.DataItem(json.loads(self.__db_handler.get(b"data-", source_id.encode())))
            self.__db_handler.delete(b"data-", source_id.encode())
            if data_item.files:
                for file in data_item.files:
                    try:
                        self.__data_handler.remove(file)
                    except Exception:
                        pass
            resp.status = falcon.HTTP_200
        except KeyError as ex:
            resp.status = falcon.HTTP_404
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)


class CSV:
    def __init__(self, db_handler: handlers.DB, data_handler: handlers.Data):
        self.__db_handler = db_handler
        self.__data_handler = data_handler

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, source_id: str, file: str):
        reqDebugLog(req)
        try:
            data_item = models.DataItem(json.loads(self.__db_handler.get(b"data-", source_id.encode())))
            if file in data_item.files:
                resp.stream, resp.content_length = self.__data_handler.open(file)
                resp.content_type = "application/octet-stream"
                resp.status = falcon.HTTP_200
            else:
                resp.status = falcon.HTTP_404
        except (KeyError, FileNotFoundError) as ex:
            resp.status = falcon.HTTP_404
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)


class Jobs:
    def __init__(self, db_handler: handlers.DB, jobs_handler: handlers.Jobs):
        self.__db_handler = db_handler
        self.__jobs_handler = jobs_handler

    def on_post(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            req_body = json.load(req.bounded_stream)
            resp.body = self.__jobs_handler.create(req_body["source_id"])
            resp.content_type = falcon.MEDIA_TEXT
            resp.status = falcon.HTTP_200
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(
                dict(
                    current=self.__jobs_handler.list_jobs(),
                    history=self.__db_handler.list_keys(b"jobs-")
                )
            )
            resp.status = falcon.HTTP_200
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)


class Job:
    def __init__(self,  db_handler: handlers.DB, jobs_handler: handlers.Jobs):
        self.__db_handler = db_handler
        self.__jobs_handler = jobs_handler

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, job_id):
        reqDebugLog(req)
        try:
            resp.content_type = falcon.MEDIA_JSON
            try:
                resp.body = json.dumps(dict(self.__jobs_handler.get_job(job_id)))
            except KeyError:
                resp.body = self.__db_handler.get(b"jobs-", job_id.encode())
            resp.status = falcon.HTTP_200
        except KeyError as ex:
            resp.status = falcon.HTTP_404
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)
