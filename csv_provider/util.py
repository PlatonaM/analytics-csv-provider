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

__all__ = ("Compress", )


import zlib
import typing


class Compress:
    def __init__(self, io_obj: typing.BinaryIO, level: int = zlib.Z_DEFAULT_COMPRESSION, method: int= zlib.DEFLATED, wbits: int = zlib.MAX_WBITS | 16, memLevel: int = zlib.DEF_MEM_LEVEL, strategy: int = zlib.Z_DEFAULT_STRATEGY):
        self.__io_obj = io_obj
        self.__comp_obj = zlib.compressobj(level=level, method=method, wbits=wbits, memLevel=memLevel, strategy=strategy)

    def write(self, b: bytes):
        return self.__io_obj.write(self.__comp_obj.compress(b))

    def flush(self):
        self.__io_obj.write(self.__comp_obj.flush())
        return self.__io_obj.flush()

    def close(self):
        self.__io_obj.write(self.__comp_obj.flush())
        return self.__io_obj.close()

    def __getattr__(self, attr):
        return getattr(self.__io_obj, attr)
