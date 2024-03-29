# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
# for the German Human Genome-Phenome Archive (GHGA)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Entrypoint of the package"""

import asyncio

from ghga_service_chassis_lib.api import run_server

from .api.main import app  # noqa: F401 pylint: disable=unused-import
from .config import CONFIG, Config


async def run_async(config: Config = CONFIG):
    """Run the service asynchronously"""
    await run_server(app="metadata_search_service.__main__:app", config=config)


def run(config: Config = CONFIG):
    """Run the service synchronously for the console_scripts entry point"""
    asyncio.run(run_async(config))


if __name__ == "__main__":
    run()
