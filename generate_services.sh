#!/bin/bash

# Ask for user input on the number of services
read -p "Enter the number of services to create: " num_services
read -p "Enter the number of targets for each service to have: " num_targets

# Check if the input is an integer
if ! [[ "$num_services" =~ ^[0-9]+$ ]] ; then
   echo "Error: The number of services must be an integer."
   exit 1
fi

if ! [[ "$num_targets" =~ ^[0-9]+$ ]] ; then
   echo "Error: The number of targets must be an integer."
   exit 1
fi

# Create or clear existing hosts.txt file
> service-app/hosts.txt

# Loop to create deployment and service files and populate hosts.txt
for i in $(seq 1 $num_services); do
    service_name="service$i"
    sidecar_name="${service_name}-sidecar"

    # Add service name to hosts.txt
    echo $service_name >> service-app/hosts.txt

    # Generate Deployment YAML
    cat <<EOF > "k8s/deployments/${service_name}-deployment.yaml"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $service_name
spec:
  replicas: 1
  selector:
    matchLabels:
      app: $service_name
  template:
    metadata:
      labels:
        app: $service_name
    spec:
      containers:
      - name: $service_name
        image: service:latest
        imagePullPolicy: IfNotPresent
        env:
          - name: SERVICE_NAME
            value: $service_name
          - name: NUM_TARGETS
            value: "$num_targets"
        ports:
        - containerPort: 5000
      - name: $service_name-sidecar
        image: sidecar:latest
        imagePullPolicy: IfNotPresent
        env:
          - name: SERVICE_NAME
            value: $service_name
        ports:
        - containerPort: 5001
EOF

    # Generate Service YAML
    cat <<EOF > "k8s/services/${service_name}-service.yaml"
apiVersion: v1
kind: Service
metadata:
  name: $service_name
spec:
  selector:
    app: $service_name
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000
  type: ClusterIP
EOF

done

echo "Generated $num_services services in k8s/deployments and k8s/services."

