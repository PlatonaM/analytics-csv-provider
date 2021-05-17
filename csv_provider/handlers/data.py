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

__all__ = ("Data",)


from ..logger import getLogger
from .. import models
import requests
import json
import datetime
import uuid
import os
import auth_client
import gzip
import contextlib
import hashlib


logger = getLogger(__name__.split(".", 1)[-1])


def shift_year(timestamp: str, year_map: dict):
    year = timestamp.split("-", 1)[0]
    return timestamp.replace(year, year_map[year])


def gen_year_map(start: int, end: int, base: int):
    map = dict()
    for x in range(end - start + 1):
        map[str(start + x)] = str(base + x)
    return map


class Data:
    def __init__(self, auth_handler: auth_client.Client, data_path: str, tmp_path: str, db_api_url: str, export_api_url: str, time_format: str, db_api_time_format: str, start_year: int, chunk_size: int, usr_id: str, compression: bool):
        self.__auth_handler = auth_handler
        self.__data_path = data_path
        self.__tmp_path = tmp_path
        self.__db_api_url = db_api_url
        self.__export_api_url = export_api_url
        self.__time_format = time_format
        self.__db_api_time_format = db_api_time_format
        self.__start_year = start_year
        self.__chunk_size = chunk_size
        self.__usr_id = usr_id
        self.__compression = compression

    def __execute_query(self, measurement: str, sort: str, **kwargs):
        kwargs["measurement"] = measurement
        kwargs["columns"] = [{"name": "data"}, {"name": "default_values"}]
        resp = requests.post(
            url="{}?format=table&order_direction={}&order_column_index=0&time_format={}".format(
                self.__db_api_url,
                sort,
                self.__db_api_time_format
            ),
            headers={"X-UserId": self.__usr_id, "Authorization": "Bearer " + self.__auth_handler.get_access_token()},
            json=[kwargs]
        )
        if not resp.ok:
            raise RuntimeError(resp.status_code)
        return resp.json()

    def __get_start_timestamp(self, measurement: str) -> str:
        return self.__execute_query(measurement=measurement, sort="asc", limit=1)[0][0]

    def __get_end_timestamp(self, measurement: str) -> str:
        return self.__execute_query(measurement=measurement, sort="desc", limit=1)[0][0]

    def __get_chunks(self, measurement: str, start: str, end: str):
        start = datetime.datetime.strptime(start, self.__time_format) - datetime.timedelta(microseconds=1)
        start = start.isoformat() + "Z"
        end = datetime.datetime.strptime(end, self.__time_format) + datetime.timedelta(microseconds=1)
        end = end.isoformat() + "Z"
        while True:
            chunk = self.__execute_query(measurement=measurement, sort="asc", limit=self.__chunk_size, time={"start": start, "end": end})
            if not chunk:
                break
            else:
                logger.debug(
                    "retrieved chunk with size of '{}' from '{}' to '{}' for '{}'".format(len(chunk), start, end, measurement)
                )
                start = chunk[-1][0]
                yield chunk

    def __get_export_ids(self, source_id: str):
        resp = requests.get(
            url=self.__export_api_url,
            headers={"X-UserId": self.__usr_id, "Authorization": "Bearer " + self.__auth_handler.get_access_token()}
        )
        if not resp.ok:
            raise RuntimeError(resp.status_code)
        resp = resp.json()
        src_ids = set()
        for item in resp["instances"]:
            if item["Description"] == source_id:
                logger.debug("found '{}' for '{}'".format(item["Measurement"], source_id))
                src_ids.add(item["Measurement"])
        return src_ids

    @contextlib.contextmanager
    def __open(self, path: str, mode: str):
        file = open(path, mode) if not self.__compression else gzip.open(path, mode, compresslevel=4)
        try:
            yield file
        finally:
            file.close()

    def create(self, source_id: str, time_field: str, delimiter: str) -> models.DataItem:
        data_item = models.DataItem()
        data_item.source_id = source_id
        data_item.time_field = time_field
        data_item.delimiter = delimiter
        data_item.sources = dict()
        data_item.default_values = dict()
        data_item.file = uuid.uuid4().hex
        start_year = self.__start_year
        chunks = list()
        columns = set()
        try:
            for src_id in sorted(self.__get_export_ids(data_item.source_id)):
                data_item.sources[src_id] = dict()
                data_item.sources[src_id]["start"] = self.__get_start_timestamp(measurement=src_id)
                data_item.sources[src_id]["end"] = self.__get_end_timestamp(measurement=src_id)
                data_item.sources[src_id]["year_map"] = gen_year_map(
                    start=int(data_item.sources[src_id]["start"].split("-", 1)[0]),
                    end=int(data_item.sources[src_id]["end"].split("-", 1)[0]),
                    base=start_year
                )
                start_year = start_year + len(data_item.sources[src_id]["year_map"])
            for src_id, source in data_item.sources.items():
                for chunk in self.__get_chunks(measurement=src_id, start=source["start"], end=source["end"]):
                    chunk_name = uuid.uuid4().hex
                    chunks.append(chunk_name)
                    data_item.size = data_item.size + len(chunk)
                    with open(os.path.join(self.__tmp_path, chunk_name), "wb") as file:
                        for item in chunk:
                            data: dict = json.loads(item[1])
                            data[data_item.time_field] = shift_year(item[0], source["year_map"])
                            columns.update(data.keys())
                            data_item.default_values.update(json.loads(item[2]))
                            file.write("{}\n".format(json.dumps(data, separators=(',', ':'))).encode())
            columns.discard(data_item.time_field)
            data_item.columns = [data_item.time_field, *sorted(columns)]
            line_map = dict()
            for x in range(len(data_item.columns)):
                line_map[x] = data_item.columns[x]
            with self.__open(os.path.join(self.__data_path, data_item.file), "wb") as file:
                file.write("{}\n".format(data_item.delimiter.join(data_item.columns)).encode())
                _range = range(len(data_item.columns))
                for chunk in chunks:
                    with open(os.path.join(self.__tmp_path, chunk), "rb") as chunk_file:
                        for line in chunk_file:
                            line = json.loads(line.strip())
                            _line = list()
                            for x in _range:
                                try:
                                    value = str(line[line_map[x]])
                                except KeyError:
                                    try:
                                        value = str(data_item.default_values[line_map[x]])
                                    except KeyError:
                                        value = str()
                                _line.append(value)
                            file.write("{}\n".format(data_item.delimiter.join(_line)).encode())
            self.purge_tmp(chunks)
            data_item.created = "{}Z".format(datetime.datetime.utcnow().isoformat())
            return data_item
        except Exception as ex:
            self.purge_tmp(chunks)
            try:
                os.remove(os.path.join(self.__data_path, data_item.file))
            except Exception:
                pass
            raise ex

    def purge_tmp(self, items=None):
        for file in items or os.listdir(self.__tmp_path):
            try:
                os.remove(os.path.join(self.__tmp_path, file))
            except Exception:
                pass

    def purge_unused(self, items):
        unused = set(os.listdir(self.__data_path)) - set(items)
        for file_name in unused:
            try:
                os.remove(os.path.join(self.__data_path, file_name))
            except Exception:
                pass

    def open(self, file_name):
        path = os.path.join(self.__data_path, file_name)
        return open(path, 'rb'), os.path.getsize(path)

    def remove(self, file_name):
        os.remove(os.path.join(self.__data_path, file_name))
