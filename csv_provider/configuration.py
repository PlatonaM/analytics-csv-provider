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

__all__ = ("conf",)


import simple_env_var


@simple_env_var.configuration
class Conf:

    @simple_env_var.section
    class Logger:
        level = "info"

    @simple_env_var.section
    class Storage:
        db_path = "/storage/db"
        data_path = "/storage/data"
        tmp_path = "/storage/tmp"

    @simple_env_var.section
    class Data:
        db_api_url = "http://test"
        export_api_url = "http://test"
        time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        db_api_time_format = "2006-01-02T15:04:05.000000Z07:00"
        start_year = 1970
        chunk_size = 50000
        compression = True

    @simple_env_var.section
    class Jobs:
        max_num = 5
        check = 5

    @simple_env_var.section
    class Auth:
        api_url = "http://test"
        client_id = None
        client_secret = None
        user_id = None


conf = Conf(load=False)
