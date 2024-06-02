from typing import List

import numpy as np
import pandas as pd
import pymongo
import streamlit as st
from bson.objectid import ObjectId
from natsort import natsorted

from config import Database


@st.cache_resource
def init_connection():
    return pymongo.MongoClient(
        host=Database.HOST,
        port=Database.PORT,
        username=Database.USERNAME,
        password=Database.PASSWORD,
    )


client = init_connection()
db = client["validation"]
channels = db["channels"]
reviewer = db["reviewer"]
expression = db["expression"]
thresholds = db["thresholds"]
expression.create_index([("sample", pymongo.ASCENDING)])


def get_reviewers() -> List[str]:
    """Returns the list of reviewers"""
    query = reviewer.find()
    return [item["name"] for item in list(query)]


def get_channels() -> List[str]:
    query = channels.find()
    return [item["name"] for item in list(query)]


def get_all_samples():
    return natsorted(thresholds.distinct("sample"))


def get_total_samples():
    return len(thresholds.distinct("sample"))


def get_sample_status_num(channel, status="all"):
    if status == "all":
        return len(thresholds.distinct("sample"))

    status = float("nan") if status == "not reviewed" else status
    query = thresholds.find(
        {"$and": [{"status": status}, {"channel": channel}]}
    ).distinct("sample")
    return len(query)


def paginated_samples(page, page_size, channel, status="all"):
    #  { "$project": { "_id": 0, "sample": 1}}
    if status == "all":
        query = thresholds.aggregate(
            [
                {"$group": {"_id": "$sample"}},
                {"$sort": {"sample": 1, "_id": 1}},
                {"$skip": (page - 1) * page_size},
                {"$limit": page_size},
            ]
        )
    else:
        status = float("nan") if status == "not reviewed" else status
        query = thresholds.aggregate(
            [
                {"$match": {"status": status, "channel": channel}},
                {"$group": {"_id": "$sample"}},
                {"$sort": {"sample": 1, "_id": 1}},
                {"$skip": (page - 1) * page_size},
                {"$limit": page_size},
            ]
        )
    return [res["_id"] for res in list(query)]


def get_samples(channel, filter_samples=True):
    if filter_samples:
        query = {"$and": [{"status": float("nan")}, {"channel": channel}]}
        data = list(thresholds.find(query))
        # print('GETSAMPLE', data)
    else:
        query = {"channel": channel}
        data = list(thresholds.find(query))
    return natsorted(np.unique([item["sample"] for item in data]))


def get_thresholds_by_channel(channel):
    query = thresholds.find({"channel": channel})
    data = list(query)
    return pd.DataFrame(data)


def get_thresholds(sample):
    query = expression.find({"sample": sample})
    data = list(query)
    return pd.DataFrame(data)


def get_threshold(sample, channel):
    query = thresholds.find_one(
        {"sample": sample, "channel": channel}, {"_id": 0, "threshold": 1}
    )
    return query["threshold"]


def get_lower(sample, channel):
    query = thresholds.find_one(
        {"sample": sample, "channel": channel}, {"_id": 0, "lower": 1}
    )
    return query["lower"]


def get_entry(sample, channel, variable):
    query = thresholds.find_one(
        {"sample": sample, "channel": channel}, {"_id": 0, variable: 1}
    )
    return query[variable]


def get_status(sample, channel):
    query = thresholds.find_one(
        {"sample": sample, "channel": channel},
        {"_id": 0, "status": 1, "lower": 1, "upper": 1, "threshold": 1, "reviewer": 1},
    )
    # print('STATUS', query)
    return query


def get_channel_stats(channel):
    query = list(
        thresholds.aggregate(
            [
                {"$match": {"channel": channel}},
                {"$group": {"_id": "$status", "total": {"$sum": 1}}},
            ]
        )
    )

    results = {}
    for item in query:
        if isinstance(item["_id"], str):
            results[item["_id"]] = item["total"]
        else:
            results["not reviewed"] = item["total"]

    return results


def get_statistics(channel):
    # results = list(
    #     thresholds.aggregate(
    #         [
    #             {"$match": {"channel": "CD8"}},
    #             {"$group": {"_id": "$status", "total": {"$sum": 1}}},
    #         ]
    #     )
    # )

    completed = thresholds.count_documents(
        {
            "$and": [
                {"$or": [{"status": "reviewed"}, {"status": "bad"}]},
                {"channel": channel},
            ]
        }
    )
    bad = thresholds.count_documents(
        {"$and": [{"$or": [{"status": "bad"}]}, {"channel": channel}]}
    )
    reviewed = thresholds.count_documents(
        {"$and": [{"$or": [{"status": "reviewed"}]}, {"channel": channel}]}
    )
    total = thresholds.count_documents({"channel": channel})
    statistics = {
        "completed": completed,
        "bad": bad,
        "reviewed": reviewed,
        "total": total,
    }

    return statistics


def update_status(sample, channel, status, threshold, lower, upper, reviewer, cells):
    query = thresholds.find_one({"sample": sample, "channel": channel}, {"_id": 1})
    _id = ObjectId(query["_id"])
    updates = {
        "$set": {
            "threshold": threshold,
            "status": status,
            "lower": lower,
            "upper": upper,
            "reviewer": reviewer,
            "cells": cells,
        },
    }
    res = thresholds.update_one({"_id": _id}, updates)
    return res


@st.cache_data(ttl=600)
def get_sample_expression(sample, primary_channel, secondary_channel):
    query = expression.find(
        {"sample": sample},
        {"_id": 0, primary_channel: 1, secondary_channel: 1, "X": 1, "Y": 1, "cell": 1},
    )
    data = list(query)
    return pd.DataFrame(data)


if __name__ == "__main__":
    import pdb

    pdb.set_trace()
