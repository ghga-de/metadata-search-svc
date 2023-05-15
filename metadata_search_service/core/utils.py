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
"""Core utilities for the Metadata Search Service"""

import time
from typing import Any, Dict, Set

DEFAULT_FACET_FIELDS: Dict[str, Set[Any]] = {
    "Dataset": {
        "type",
        "has_study.type",
        "has_study.ega_accession",
        "has_study.has_project.alias",
    },
    "Project": {"alias"},
    "Study": {"type"},
    "Experiment": {"type"},
    "Biospecimen": {"has_phenotypic_feature.concept_name"},
    "Sample": set(),
    "Publication": set(),
    "File": {"format"},
    "Individual": {"sex", "has_phenotypic_feature.concept_name"},
}


def get_time_in_millis() -> int:
    """
    Get current time in milliseconds.

    Returns:
        Time in milliseconds
    """
    return int(round(time.time() * 1000))


def format_facet_key(key: str):
    """
    Format a facet key for better readability.

    Args:
        key: The facet key

    Returns:
        The formatted facet key
    """
    formatted_fields = {
        "type": "Dataset Type",
        "has_study.type": "Study Type",
        "has_study.ega_accession": "Study ID",
        "has_study.has_project.alias": "Project",
    }

    return formatted_fields[key]
