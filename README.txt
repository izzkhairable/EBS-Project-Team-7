docker build -t darrenho1994/bms-flask:latest -f Dockerfile .

docker push darrenho1994/bms-flask

kubectl config set-context --current --namespace=smu-team07 

kubectl apply -f ./deployment.yaml