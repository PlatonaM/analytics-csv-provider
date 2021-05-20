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

from csv_provider.logger import initLogger
from csv_provider.configuration import conf
from csv_provider import handlers
from csv_provider import api
from csv_provider import util
import auth_client
import falcon


initLogger(conf.Logger.level)

util.init_storage((conf.Storage.db_path, conf.Storage.tmp_path, conf.Storage.data_path))

auth_handler = auth_client.Client(
    url=conf.Auth.api_url,
    client_secret=conf.Auth.client_secret,
    client_id=conf.Auth.client_id,
    user_id=conf.Auth.user_id
)
db_handler = handlers.DB(st_path=conf.Storage.db_path)
data_handler = handlers.Data(
    auth_handler=auth_handler,
    data_path=conf.Storage.data_path,
    tmp_path=conf.Storage.tmp_path,
    db_api_url=conf.Data.db_api_url,
    export_api_url=conf.Data.export_api_url,
    time_format=conf.Data.time_format,
    db_api_time_format=conf.Data.db_api_time_format,
    start_year=conf.Data.start_year,
    chunk_size=conf.Data.chunk_size,
    usr_id=conf.Auth.user_id,
    compression=conf.Data.compression
)
jobs_handler = handlers.Jobs(
    db_handler=db_handler,
    data_handler=data_handler,
    check_delay=conf.Jobs.check,
    max_jobs=conf.Jobs.max_num
)

app = falcon.API()

app.req_options.strip_url_path_trailing_slash = True

routes = (
    ("/data", api.DataCollection(db_handler=db_handler)),
    ("/data/{source_id}", api.DataResource(db_handler=db_handler, data_handler=data_handler)),
    ("/data/{source_id}/file", api.CSV(db_handler=db_handler, data_handler=data_handler)),
    ("/jobs", api.Jobs(db_handler=db_handler, jobs_handler=jobs_handler)),
    ("/jobs/{job_id}", api.Job(db_handler=db_handler, jobs_handler=jobs_handler))
)

for route in routes:
    app.add_route(*route)

data_handler.purge_tmp()
jobs_handler.start()
