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


def get_reviewers():
    query = reviewer.find()
    items = list(query)
    return [item["name"] for item in items]


def get_all_channels(sample):
    return natsorted(thresholds.distinct("channel"))


def get_channels():
    query = channels.find()
    data = list(query)
    return [item["name"] for item in data]


def get_all_samples():
    return natsorted(thresholds.distinct("sample"))


def get_total_samples():
    return len(thresholds.distinct("sample"))


def get_sample_status_num(channel, status="all"):
    if status == "all":
        return len(thresholds.distinct("sample"))

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


# exports.getArticles = async (req, res) => {
#   let { page, pageSize } = req.query;

#   try {
#     // If "page" and "pageSize" are not sent we will default them to 1 and 50.
#     page = parseInt(page, 10) || 1;
#     pageSize = parseInt(pageSize, 10) || 50;

#     const articles = await Articles.aggregate([
#       {
#         $facet: {
#           metadata: [{ $count: 'totalCount' }],
#           data: [{ $skip: (page - 1) * pageSize }, { $limit: pageSize }],
#         },
#       },
#     ]);

#     return res.status(200).json({
#       success: true,
#       articles: {
#         metadata: { totalCount: articles[0].metadata[0].totalCount, page, pageSize },
#         data: articles[0].data,
#       },
#     });
#   } catch (error) {
#     return res.status(500).json({ success: false });
#   }
# };


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


def get_status(sample, channel):
    query = thresholds.find_one(
        {"sample": sample, "channel": channel},
        {"_id": 0, "status": 1, "lower": 1, "upper": 1, "threshold": 1, "reviewer": 1},
    )
    # print('STATUS', query)
    return query


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
