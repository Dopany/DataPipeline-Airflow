#!/bin/bash

# Define container names
containers=("webserver" "scheduler" "worker" "triggerer")

# Loop through each container
for container in "${containers[@]}"; do
  echo "Starting SSH service in container: $container"
  
  # Start SSH service
  docker exec -u root $container service ssh start
  
  # Check SSH service status
  ssh_status=$(docker exec -u root $container service ssh status)
  
  # Print the status
  echo "SSH status in $container: $ssh_status"
done
