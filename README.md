# Binarisation app

## What is this

The binarisation app allows to quickly gate individual markers TMAs.

## 1. Data preparation

The TMA image data needs to be in zarr format, preprocessed using `spatialproteomics`.

```bash
python prepare_data.py --input_folder <input folder containing all TMA zarrs> --output <directory in which the output is saved to>
```

The `prepare_data.py` scripts creates:

1. A `expression.csv` which contains the expression data from each core and is used to set up MongoDB.
2. A `thresholds.csv` which contains sets up and is used to set up the MongoDB.
3. A `zarr` file for each channel which should be uploaded to S3 storage.

Next, Upload the `zarr`s created by `prepare_data.py` to S3-storage into a dedicated folder (for the binarazor).
Optionally, upload also the original `zarrs` to S3-storage into a separate folder (for the multirazor).

## 2. Set up Kubernetes

If you use EMBL Kubernetes:

- Set up a new tenant.
- Create a new namespace.

```
kubectl --user=oidc create namespace <tenant>-binarazor
```

## 3. Deploy Binarazor

### 3.1 Set up MongoDB

- First create a persistent volume. This is where the data of MongoDB is saved to.

```
kubectl -n <namespace> apply -f  kubernetes/pvc.yaml
```

- Deploy Mongo DB.

```
kubectl -n <namespace> apply -f  kubernetes/mongo-secret.yaml
kubectl -n <namespace> apply -f  kubernetes/mongo.yaml
kubectl -n <namespace> apply -f  kubernetes/mongo-configmap.yaml
```

- Before we can deploy we need to set a unique NodePort. Edit the `nodePort` in `kubernetes/mongo-express.yaml` accordingly. Then deploy MongoDB.

```
kubectl -n <namespace> apply -f  kubernetes/mongo-express.yaml
```

### 3.2 Populate the database

- Next we need to populate the database with the data (`csv`'s) we created in step 1. In order to this, we need to port forward the MongoDB service.

```
kubectl -n <namespace> port-forward service/mongodb-service 5555:27017 &
```

- Next we can populate the database using the `populate_db.py` script.

```
python populate_db.py <path to thresholds.csv> validation thresholds  --port 5555
python populate_db.py <path to expression.csv> validation expression --port=5555
```

- Create collections for channels and reviewers.

```
python set_up_db.py validation --port 5555
```

- Port forward Mongo Express and populate the collections with the channels of interest and the users of the app.

### 3.3 Deploy Binarazor

- Upload secrets.

```
kubectl -n <namespace> apply -f  kubernetes/secret.yaml
```

- Change data in binarzor secrets. Use for example OpenLens.

  - `AWS_PATH`: Path to the S3 folder in which the channel zarrs are.
  - `MULTI_PATH`: Path to the S3 folder in which the core zarrs are.
  - `PROJECT`: Project name.

- Finally deploy the binarazor.

```
kubectl -n <namespace> apply -f kubernetes/deployment-streamlit.yaml
```

- Set up an ingress. Modify it accordingly.

```
kubectl -n <namespace> apply -f kubernetes/ingress.yaml
```

- If you use EMBL Kubernetes get in touch with IT support and ask for exposing your application to the Web.
