#!/usr/bin/env python3

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

"""Get OpenAPI spec from FastAPI app and write it as yaml to stdout

    Usage:
        `.devcontainer/openapi_from_app.py > openapi.yaml`
"""


import sys

import yaml

# Please adapt to package name:
from metadata_search_service.api.main import app

# get openapi spec as dict:
openapi_spec = app.openapi()

# convert to yaml and write to stdout:
with sys.stdout as stream:
    print("# This file was autogenerated, please do not modify.", file=stream)
    openapi_yaml = yaml.safe_dump(openapi_spec, stream)
