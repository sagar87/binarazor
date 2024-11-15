
# CHANGE PORT FOR MONGO EXPRESS: mongo_express.yaml
# CHANGE AWS_URL in secrets.yaml
# CHANGE PROJECT in secrets.yaml

NAMESPACE=valerkri-binarazor
THRESHOLDS="~/Downloads/valerkri_thresholds_sprot.csv"
EXPRESSION="~/Downloads/valerkri_expression_sprot.csv"

# CHANGE PORT FOR MONGO EXPRESS: mongo_express.yaml
# CHANGE AWS_URL in secrets.yaml
# CHANGE PROJECT in secrets.yaml

# export DEPLOY_MONGO_EXPRESS_PORT
source ./.venv/bin/activate
# set up mongo db
kubectl -n ${NAMESPACE} apply -f  kubernetes/pvc.yaml
kubectl -n ${NAMESPACE} apply -f  kubernetes/mongo-secret.yaml
kubectl -n ${NAMESPACE} apply -f  kubernetes/mongo.yaml
kubectl -n ${NAMESPACE} apply -f  kubernetes/mongo-configmap.yaml

read -p "CHANGE MONGOEXPRESS PORT"

kubectl -n ${NAMESPACE} apply -f  kubernetes/mongo-express.yaml

read -p "Wait until services are created.... Press enter to continue"

# populate db
kubectl -n ${NAMESPACE} port-forward service/mongodb-service 5555:27017 &
./.venv/bin/python set_up_db.py validation --port 5555
./.venv/bin/python populate_db.py ${THRESHOLDS} validation thresholds  --port 5555
./.venv/bin/python populate_db.py ${EXPRESSION} validation expression --port=5555

# DEPLOY Binarizer
kubectl -n ${NAMESPACE} apply -f kubernetes/secret.yml

read -p "Check binarazor secrets.... Press enter to continue"
kubectl -n ${NAMESPACE} apply -f kubernetes/deployment-streamlit.yaml
# DO INGRESS MANUALLY
# kubectl -n ${NAMESPACE} apply -f kubernetes/ingress.yaml


kill $(jobs -p)