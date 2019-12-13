
Code for the Project
-------------------------
This folder contains all the code files for our project.

This README file introduces how to deploy the backend service on cloud servers and covers important technical details in our development

The online code execution is available at http://ec2-3-90-220-109.compute-1.amazonaws.com:8888

### 1. Deployment
#### 1.1 Platform
The backend service is supposed to be deployed on a cluster of host machines are connected to a common network. In our example we deploy the code on multiple AWS virtual machines. 

#### 1.2 Docker Preparation
On each host VM, docker should be installed:
```shell
sudo apt install docker.io
```
Select one of the host as master node, initialize docker swarm on the node, in our case it's address is 172.31.24.67
```shell
sudo docker swarm init --advertise-addr=172.31.24.67
```

sudo docker service create --replicas 1 --name oj_master --constraint 'node.hostname == ip-172-31-24-67' -t --network oj_network oj_node /bin/bash -p 8888:8888 -p 8086:8086

sudo docker service create --replicas 1 --name oj_worker1 --constraint 'node.hostname == ip-172-31-25-219' -t --network oj_network oj_node python3 /root/4287-Final/website/execution.py -n eth0 -m 172.31.24.67 -p 8086

sudo docker service create --replicas 1 --name oj_worker2 --constraint 'node.hostname == ip-172-31-34-157' -t --network oj_network oj_node python3 /root/4287-Final/website/execution.py -n eth0 -m 172.31.24.67 -p 8086

sudo docker service create --replicas 1 --name oj_worker3 --constraint 'node.hostname == ip-172-31-36-122' -t --network oj_network oj_node python3 /root/4287-Final/website/execution.py -n eth0 -m 172.31.24.67 -p 8086


### 2. Master-Worker Communication
There is a network create for the swarm cluster so all the nodes can communicate with each other through the network. 

Each worker node should know the ip address of the master node and port that the master node listens to.
Every 10 seconds, a worker node sends a signal message including its own ip address in the network and its port for recieving the request to the master node. 

The master node keeps listeninig to worker nodes' signals to know about the available worker nodes. Whenever the master node starts, it will always acquire all the available worker nodes' addresses.

When there is a code execution task, the master node will select one of the worker nodes and send the request to the port specified in the signal message. Then master node will pending on the message from port+1 of the worker node. 

### 3. Master Node

For handling requests from the frontend, we use Python Flask for the server implementation

For scheduing the worker nodes, we use a queue the save the available worker. There is thread keep listeninig to worker nodes' signal. If there a new worker is found, the infomation of that worker will be pushed to the queue. When there is a new request, the Flask request handler will get to head of the workers queue and use that code. If the queue is empty, the handler will pend until there is one available.

When a worker's signal is recieved, the time of recieve is recorded for that worker. Everytime the master pick up a worker, it will check whether the timestamp. It the last time of recieving that worker's signal is more than 15 seconds ago, the worker will be discarded. 

When the master send a request to a worker, the master will pend on the result from the worker. If it taks too long to hear back from the worker, master will return an error message to the frontend. If the master get the result from the worker the result data is too large which means the output is too long, then master will return a 'output limit exceeded' message to the frontend. 

### 4. Worker Node
