# Kubectl Commands Cheat Sheet

This file contains all the `kubectl` commands we have used and discussed so far, categorized by their purpose.

## Basic Deployment Management
Apply a YAML configuration file to the cluster:
`kubectl apply -f deployment.yaml`

Restart a deployment to force it to pull the latest `latest` image:
`kubectl rollout restart deployment/aceest-fitness`

Update the Docker image of a deployment directly via command line:
`kubectl set image deployment/aceest-fitness fitness-app=2024tm93562/aceest-fitness:v2`

## Monitoring Rollouts (Rolling Updates)
Watch the status of a rollout in real-time:
`kubectl rollout status deployment/aceest-fitness`

View the revision history of a deployment:
`kubectl rollout history deployment/aceest-fitness`

Undo a rollout (rollback to the previous working version):
`kubectl rollout undo deployment/aceest-fitness`

View the history and scaling of ReplicaSets during an update:
`kubectl get rs`

## Networking & Access
Create a direct bridge from your local Windows machine to a Kubernetes service:
`kubectl port-forward service/fitness-service 30001:5000`

If the service is in a specific namespace:
`kubectl port-forward service/fitness-service 30002:5000 -n blue-green-deployment`

## Cluster Inspection
List all pods, services, deployments, and replicasets in the default namespace:
`kubectl get all`

Watch pods continuously as they are created/terminated:
`kubectl get pods -w`

View pods with extra details (like their internal IP addresses and nodes):
`kubectl get pods -o wide`

View the nodes running in your cluster:
`kubectl get nodes -o wide`

## Blue-Green Specific Commands (Namespaces & Patching)
Create a new namespace if it doesn't exist:
`kubectl get namespace blue-green-deployment || kubectl create namespace blue-green-deployment`

Check which environment (blue or green) the service is currently routing traffic to:
`kubectl get svc fitness-service -n blue-green-deployment -o jsonpath="{.spec.selector.version}"`

Update (patch) a service's selector instantly to switch traffic (using a patch file to avoid PowerShell quoting issues):
`kubectl patch service fitness-service --patch-file patch.json -n blue-green-deployment`


 `kubectl port-forward service/fitness-service 30002:5000 -n blue-green-deployment`


  `kubectl get svc fitness-service -n blue-green-deployment -o jsonpath="{.spec.selector.version}"`

  `while($true) { curl.exe -s http://localhost:30002 ; Start-Sleep -Seconds 3 }`
