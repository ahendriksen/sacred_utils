# -*- coding: utf-8 -*-

import os
from pymongo import MongoClient
import gridfs
# from bson.objectid import ObjectId
import tempfile


def get_sacred_database(host=None, user=None, password=None):
    user = os.environ.get('MONGO_SACRED_USER') if not user else user
    if password is None:
        password = os.environ.get('MONGO_SACRED_PASS')
    host = os.environ.get('MONGO_SACRED_HOST') if not host else host

    assert user, 'Setting $MONGO_USER is required'
    assert password, 'Setting $MONGO_PASS is required'
    assert host, 'Setting $MONGO_HOST is required'

    url = f"mongodb://{user}:{password}@{host}:27017/" \
          "sacred?authMechanism=SCRAM-SHA-1"

    client = MongoClient(url)
    database = client['sacred']
    return database


def get_run_collection(**kwargs):
    database = get_sacred_database(**kwargs)
    return database['runs']


def get_run(id, **kwargs):
    runs = get_run_collection(**kwargs)
    if not runs:
        raise LookupError('could not open mongo db')

    run = runs.find_one({'_id': id})
    if not run:
        raise LookupError('could not find id')
    return run


def get_config_from_id(id, **kwargs):
    run = get_run(id, **kwargs)
    return run['config']


def list_run_artifacts(id, do_print=False, **kwargs):
    run = get_run(id, **kwargs)
    artifacts = run['artifacts']

    if do_print:
        print("file id                   name")
        print("==================================================")
        for artifact in artifacts:
            print("{file_id}: {name}".format(**artifact))
    else:
        return artifacts


def print_run_artifacts(id, **kwargs):
    list_run_artifacts(id, do_print=True, **kwargs)


def get_artifact_by_id(id, **kwargs):
    database = get_sacred_database(**kwargs)
    fs = gridfs.GridFS(database)
    handle = fs.get(id)
    tmp = tempfile.TemporaryFile()
    tmp.write(handle.read())
    tmp.seek(0)
    return tmp


def get_artifact(run_id, artifact_name=None, artifact_id=None, **kwargs):
    artifacts = list_run_artifacts(run_id)
    if artifact_name is None and artifact_id is None:
        raise ValueError('name and artifact_id cannot both be None')
    elif artifact_name:
        artifact_id = next(artifact['file_id']
                           for artifact in artifacts
                           if artifact['name'] == artifact_name)
        if not artifact_id:
            raise LookupError(
                f"Artifact with name {artifact_name} does not exist")

    return get_artifact_by_id(artifact_id)
