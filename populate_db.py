import os
from pymongo import MongoClient
import pandas as pd

import sys
import argparse


def cmdline_args():
    # Make parser object
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    p.add_argument("data", type=str, help="Path to dataframe")
    p.add_argument("database", type=str, help="Name of the database, dont forget to run kubectl -n <namespace> port-forward service/<mongodb-service> 5555:27017")
    p.add_argument("collection", type=str, help="Name of the collection")
    p.add_argument("--host", type=str, help="Mongo DB Host", default="0.0.0.0")
    p.add_argument("--port", type=int, help="Port number", default=5555)
    p.add_argument("--username", type=str, help="username", default="username")
    p.add_argument("--password", type=str, help="password", default="password")
    p.add_argument(
        "-v",
        "--verbosity",
        type=int,
        choices=[0, 1, 2],
        default=0,
        help="increase output verbosity (default: %(default)s)",
    )
    return p.parse_args()


if __name__ == "__main__":

    if sys.version_info < (3, 5, 0):
        sys.stderr.write("You need python 3.5 or later to run this script\n")
        sys.exit(1)

    try:
        args = cmdline_args()
        print(args)
    except:
        print('Try $python <script_name> "Hello" 123 --enable')

    client = MongoClient(
        host=args.host, port=args.port, username=args.username, password=args.password
    )
    df = pd.read_csv(args.data, index_col=0)
    data = df.to_dict(orient="records")  # make it json line

    # populate db
    db = client[args.database]
    collection = db[args.collection]
    
    import pdb; pdb.set_trace()

    # Insert data into MongoDB
    result = collection.insert_many(data)
