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

"""Test the api module"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from metadata_search_service.api.main import app

from ..fixtures.mongodb import MongoAppFixture, mongo_app_fixture  # noqa: F401


def test_index(mongo_app_fixture: MongoAppFixture):  # noqa: F811
    """Test the index endpoint"""

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.text == '"Index for Metadata Search Service."'


@pytest.mark.parametrize(
    "query,document_type,return_facets,skip,limit,conditions",
    [
        (
            {"query": "*"},
            "Dataset",
            False,
            0,
            10,
            {
                "data": {
                    "title": [
                        "Dataset for head and neck cancer RNA",
                        "Dataset for hepatopancreaticobiliary malignancy RNA",
                        "Dataset for soft tissue tumor RNA",
                    ]
                },
                "count": 3,
                "facets": {},
            },
        ),
        (
            {"query": "*"},
            "Dataset",
            True,
            0,
            10,
            {
                "data": {
                    "title": [
                        "Dataset for head and neck cancer RNA",
                        "Dataset for hepatopancreaticobiliary malignancy RNA",
                        "Dataset for soft tissue tumor RNA",
                    ]
                },
                "count": 3,
                "facets": {
                    "type": {
                        "Whole genome sequencing": 1,
                        "Exome sequencing": 1,
                        "Transcriptome profiling by high-throughput sequencing": 1,
                    }
                },
            },
        ),
        (
            {"query": "*"},
            "Dataset",
            True,
            0,
            1,
            {
                "data": {
                    "title": [
                        "Dataset for head and neck cancer RNA",
                        "Dataset for hepatopancreaticobiliary malignancy RNA",
                        "Dataset for soft tissue tumor RNA",
                    ]
                },
                "count": 3,
                "facets": {
                    "type": {
                        "Whole genome sequencing": 1,
                        "Exome sequencing": 1,
                        "Transcriptome profiling by high-throughput sequencing": 1,
                    }
                },
            },
        ),
        (
            {"query": "*"},
            "Study",
            True,
            0,
            10,
            {
                "data": {
                    "title": [
                        "Comprehensive Genomic and Transcriptomic Analysis of Rare Cancers for Guiding of Therapy (H021)",
                    ]
                },
                "count": 1,
                "facets": {"type": {"cancer_genomics": 1}},
            },
        ),
        (
            {"query": "*", "filters": [{"key": "type", "value": "Exome sequencing"}]},
            "Dataset",
            True,
            0,
            10,
            {
                "data": {"title": ["Dataset for head and neck cancer RNA"]},
                "count": 1,
                "facets": {"type": {"Exome sequencing": 1}},
            },
        ),
        (
            {
                "query": "*",
                "filters": [
                    {"key": "type", "value": "Whole genome sequencing"},
                    {"key": "has_study.type", "value": "cancer_genomics"},
                    {"key": "has_study.has_project.alias", "value": "NCT_MASTER"},
                ],
            },
            "Dataset",
            True,
            0,
            10,
            {
                "data": {"title": ["Dataset for soft tissue tumor RNA"]},
                "count": 1,
                "facets": {"type": {"Whole genome sequencing": 1}},
            },
        ),
        (
            {"query": "metastasis"},
            "Dataset",
            True,
            0,
            10,
            {
                "data": {
                    "title": [
                        "Dataset for head and neck cancer RNA",
                        "Dataset for hepatopancreaticobiliary malignancy RNA",
                        "Dataset for soft tissue tumor RNA",
                    ]
                },
                "count": 3,
                "facets": {
                    "type": {
                        "Whole genome sequencing": 1,
                        "Exome sequencing": 1,
                        "Transcriptome profiling by high-throughput sequencing": 1,
                    }
                },
            },
        ),
    ],
)
def test_search(  # noqa: C901
    mongo_app_fixture: MongoAppFixture,  # noqa: F811
    query,
    document_type,
    return_facets,
    skip,
    limit,
    conditions,
):
    """Test search"""
    client = mongo_app_fixture.app_client
    url = f"/rpc/search?document_type={document_type}&return_facets={return_facets}&skip={skip}&limit={limit}"
    response = client.post(
        url,
        json=query,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["hits"]) > 0
    if conditions["data"]:
        data_keys = conditions["data"].keys()
        for i in range(0, len(data["hits"])):
            hit = data["hits"][i]
            doc = hit["content"]
            for key in data_keys:
                if i >= len(conditions["data"][key]):
                    break
                assert doc[key] == conditions["data"][key][i]

    if conditions["count"]:
        assert data["count"] == conditions["count"]

    if return_facets:
        assert len(data["facets"]) > 0
        facets = {}
        if conditions["facets"]:
            for facet in data["facets"]:
                facets[facet["key"]] = {
                    x["option"]: x["count"] for x in facet["options"]
                }
            for facet_name in conditions["facets"]:
                assert facet_name in facets
                for key, value in conditions["facets"][facet_name].items():
                    assert (
                        key in facets[facet_name] and facets[facet_name][key] == value
                    )
