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

"""Populates the database directly with example data for each record type"""

import asyncio
import json
import os
from pathlib import Path

import motor.motor_asyncio
import typer

# pylint: disable=too-many-arguments

HERE: Path = Path(__file__).parent.resolve()

DEFAULT_EXAMPLES_DIR: str = HERE.parent.resolve() / "example_data"  # type: ignore

RECORD_TYPES = {
    ("analyses", "Analysis"),
    ("biospecimens", "Biospecimen"),
    ("data_access_committees", "DataAccessCommittee"),
    ("data_access_policies", "DataAccessPolicy"),
    ("datasets", "Dataset"),
    ("dataset_embedded", "DatasetEmbedded"),
    ("dataset_summary", "DatasetSummary"),
    ("disease_or_phenotypic_features", "DiseaseOrPhenotypicFeature"),
    ("experiments", "Experiment"),
    ("files", "File"),
    ("individuals", "Individual"),
    ("library_preperation_protocols", "LibraryPreparationProtocol"),
    ("members", "Member"),
    ("metadata_summary", "MetadataSummary"),
    ("phenotypic_features", "PhenotypicFeature"),
    ("projects", "Project"),
    ("protocols", "Protocol"),
    ("publications", "Publication"),
    ("samples", "Sample"),
    ("sequencing_protocols", "SequencingProtocol"),
    ("studies", "Study"),
    ("submissions", "Submission"),
}


async def populate_record(
    example_dir: str, record_type: str, db_url: str, db_name: str, collection_name: str
):
    """Populate the database with data for a specific record type"""
    file = os.path.join(example_dir, f"{record_type}.json")
    if os.path.exists(file):
        with open(file, encoding="utf-8") as records_file:
            records = json.load(records_file)
        if len(records[record_type]) > 0:
            await insert_records(db_url, db_name, collection_name, records[record_type])


async def create_text_index(db_url: str, db_name: str, collection_name: str):
    """Create a text index on a collection"""
    client = motor.motor_asyncio.AsyncIOMotorClient(db_url)
    collection = client[db_name][collection_name]
    await collection.create_index([("$**", "text")])


async def insert_records(db_url, db_name, collection_name, records):
    """Insert a set of records to the database"""
    client = motor.motor_asyncio.AsyncIOMotorClient(db_url)
    collection = client[db_name][collection_name]
    await collection.insert_many(records)


async def count_documents_in_collection(db_url, db_name, collection_name):
    """Check whether there is data in a given collection"""
    client = motor.motor_asyncio.AsyncIOMotorClient(db_url)
    collection = client[db_name][collection_name]
    count = await collection.count_documents({})
    return count


def main(
    example_dir: str = DEFAULT_EXAMPLES_DIR,
    db_url: str = "mongodb://localhost:27017",
    db_name: str = "metadata-store",
    reload: bool = False,
):
    """Populate the database with records for all record types"""
    loop = asyncio.get_event_loop()
    typer.echo("This will populate the database with records for all record types.")
    if not os.path.exists(example_dir):
        raise IOError(f"Directory '{example_dir}' does not exist.")
    for record_type, collection_name in RECORD_TYPES:
        typer.echo(f"  - working on record type: {record_type}")
        count = loop.run_until_complete(
            count_documents_in_collection(db_url, db_name, collection_name)
        )
        if count > 0 and not reload:
            raise Exception(
                f"Cannot write to a non-empty {collection_name} collection."
            )
        loop.run_until_complete(
            populate_record(example_dir, record_type, db_url, db_name, collection_name)
        )
        loop.run_until_complete(create_text_index(db_url, db_name, collection_name))
    typer.echo("Done.")


if __name__ == "__main__":
    typer.run(main)
