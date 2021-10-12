docker build -t darrenho1994/bms-flask:latest -f Dockerfile .

docker push darrenho1994/bms-flask

kubectl config set-context --current --namespace=smu-team07 

kubectl apply -f ./deployment.yaml


How to access pod files:
1. kubectl exec --stdin --tty capexample-app-58d8cbb99c-n8d9f -- /bin/bash 

2. type redis-cli

3. auth kPppOZp2hC

4. select 0


keys * (to search alll keys in my db)

FLUSHALL (to DELETE KEYS FROM ALL DATABASE)

FLUSHDB (to delete keys of the selected Redis Database) < use this