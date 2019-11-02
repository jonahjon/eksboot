#aws eks --region us-west-2 update-kubeconfig --name eksboot --role-arn arn:aws:iam::164382793440:role/service-role/kubectl-test

#curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get > get_helm.sh

#############################
## Install Helm and Tiller ##
#############################
chmod +x get_helm.sh

./get_helm.sh

kubectl apply -f helm_rbac.yaml

pwd=$(pwd)

export HELM_HOME=$pwd

helm init --service-account tiller


#############################
## Install HPA Metrics server
#############################
helm install stable/metrics-server \
    --name metrics-server \
    --version 2.0.4 \
    --namespace metrics

kubectl get apiservice v1beta1.metrics.k8s.io -o yaml

# kubectl get hpa
# kubectl get hpa -w   | watch
# kubectl autoscale deployment php-apache --cpu-percent=50 --min=1 --max=10



#########################
##  Cluster AutoScaler ##
#########################
wget https://eksworkshop.com/scaling/deploy_ca.files/cluster_autoscaler.yml

export ASG_NAME=$(aws autoscaling describe-auto-scaling-groups --query 'AutoScalingGroups[].[AutoScalingGroupName]' --output text | grep eksctl-eksboot)
export AWS_DEFAULT_REGION=$(aws configure get region)

envsubst <cluster_autoscaler.yml.template >cluster_autoscaler.yml

kubectl apply -f cluster_autoscaler.yml --tail 10


#########################
##  Appmesh/Prom/Grafana/Xray ##
#########################

helm install -n aws-appmesh --namespace appmesh-system https://github.com/PaulMaddox/aws-appmesh-helm/releases/latest/download/aws-appmesh.tgz

# Replace this with app namespace
kubectl label namespace default appmesh.k8s.aws/sidecarInjectorWebhook=enabled

kubectl get pods -n appmesh-system

#kubectl create ns appmesh-demo

#kubectl -n appmesh-system port-forward svc/grafana 3000:3000

#helm install -n aws-appmesh-demo --namespace appmesh-demo https://github.com/PaulMaddox/aws-appmesh-helm/releases/latest/download/aws-appmesh-demo.tgz


#########################
# Alb Ingress ##
#########################

### WIP ###

# cd alb-Ingress/
# aws iam create-policy \
# --policy-name ALBIngressControllerIAMPolicy \
# --policy-document file://iam-policy.json

# kubectl -n kube-system describe configmap aws-auth -o jsonpath='{.items[*].status.addresses[?(@.type=="ExternalIP")].address}'



# aws iam list-roles --query 'Roles[].Arn' | grep *eksctl-eksboot* )