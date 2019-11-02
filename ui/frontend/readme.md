https://github.com/PaulMaddox/aws-appmesh-helm


## To disable items seperatley
aws-appmesh-inject:
  enableStatsD: false
  enableStatsDTags: false
  enableStatsDExporter: false
  enableXRay: false

helm install -n aws-appmesh --namespace appmesh-system -f ./override_yaml_filename https://github.com/PaulMaddox/aws-appmesh-helm/releases/latest/download/aws-appmesh.tgz



kubectl create ns appmesh-demo

# enable auto-injection of AWS App Mesh sidecars for this namespace
kubectl label namespace appmesh-demo appmesh.k8s.aws/sidecarInjectorWebhook=enabled

# deploy the demo
helm install -n aws-appmesh-demo --namespace appmesh-demo https://github.com/PaulMaddox/aws-appmesh-helm/releases/latest/download/aws-appmesh-demo.tgz