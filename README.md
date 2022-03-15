# k8s-Scheduler 

A Simple python based scheduler to schedule kubernetes jobs on crontab schedules. 

This module will help schedule two kinds of jobs ,

### Periodic 

These are jobs which are supposed to run on a crontab schedule. This package would launch kubernetes pods 
as per the crontab schedule and monitor its runs.

### Continuous runs 

These are jobs which are supposed to be running continuously. Like a stream data input. This package would 
launch and monitor such continuous runs. If any of the run fails for any reason , this package would reschedule it. 

## Installation 
To install the scheduler run below command, 

```
pip install k8s-scheduler 
```
## Pre requisites 

As the name suggests it's a job scheduler for kubernetes , so you would need a k8s instance apart from below mandatory and optional requirements.

**Mongodb** - This acts as a data store for scheduler and results backend. 

**EFL / ELK Stack** - For logging and retrieving logs for a pod which is complete / running 

## Example usage 

Use the package to create a schedule entry in the backend , and use the run_scheduler method to start the scheduler in backrgound mode.

```python
from k8s_scheduler import Scheduler
from k8s_scheduler.LogHandler import LogHandler

scheduler = Scheduler(host="mongo_db_host",
                      username="user_name",
                      password="password",
                      db_name="test_schedule")

# Create schedules in the mongodb collection
job_id_1 = scheduler.create_schedule(schedule=test_job_1)
job_id_2 = scheduler.create_schedule(schedule=test_job_2)
job_id_3 = scheduler.create_schedule(schedule=test_job_3)

# Start Scheduler application 
scheduler.start_scheduler()
```

#### Schedule object type

Below is the template for the scheduler object.

```python
schedule_rec = {
        "schedule_name": "test-schedule-3-always", # Name of the schedule
        "schedule_enabled": 1,  # 1 for enabled 0 for disabled 
        "schedule_description": "test always schedule with nginx and with service",
        "schedule_type": "always", # always is for streaming continuous jobs , periodic is for crontab based schedules 
        "parallel_execution": 0, # If two instances of the same job can run together
        "schedule_crontab": { # Crontab schedule
                            "minute": "*/2",
                            "hour": "*",
                            "day_of_month": "*",
                            "month": "*",
                            "day_of_week": "*"
                            },
        "kubernetes_deployment_options": {
                                        "name": "nginx-always-service",  # name of the deployment
                                        "container_name": "nginx-always", # Container name
                                        "container_image": "nginx:latest", # Image 
                                        "restart_policy": "", # k8s Restart policy 
                                        "ttl_seconds_after_finished": 10, # Seconds until the job needs to be purged 
                                        "env_vars": [], # Env vars for the deployment 
                                        "deploy_service": 1,  # If a service needs to be deployed ? 1=yes 0=No
                                        "service_name": "nginx-service", # Name of the service 
                                        "port": 8080, # Port exposed 
                                        "target_port": 80 # Port exposed 
                                        }
        }

```

### Scheduler options 

Below are the defaults when starting the scheduler, any of these params can be modified when creating a scheduler instance 

```python
scheduler = Scheduler(db_name="k8s_scheduler",  # Name of the Mongodb Database
                      scheduler_collection_name="test_coll", # Collection name for the scheduler
                      result_db_collection='result_coll', # Collection name for the result store
                      scheduler_poll_interval=10, # Polling interval for scheduler in seconds 
                      k8s_worker_namespace="test-namespace", # k8s namespace in which pods are to be deployed 
                      k8s_config_file_path='/var/snap/microk8s/current/credentials/client.config', # k8s config file if running outside cluster
                      **kwargs # connection args for mongodb 
                      )
```


## Log Retrieval and schedules history.  

We can retrieve logs of the jobs by connecting to ELK/EFK stack as below 

```python
log_handler = LogHandler(elastic_search_server='10.1.179.109',  # Elastic server
                         elastic_search_port='9200', # port 
                         worker_namespace='test-namespace', # namespace of the workers 
                         index='logstash*') # logstash index 

log_handler.get_logs(schedule_name="nginx-always", # Name of the schedule  
                     output_json=True) # If True Returns log as json object , if False prints log to console 


```

## Testing the application  

To test the application we can use microk8s to spin up a k8s cluster and install required backends. 

Install microk8s / k8s flavour

    sudo snap install microk8s --classic
	microk8s enable helm3 ingress dashboard dns storage registry fluentd
	sudo snap alias microk8s.kubectl kubectl
	sudo snap alias microk8s.helm3 helm

Install backends 

	helm install test-mongodb bitnami/mongodb -n test-mongodb --create-namespace --set architecture=replicaset

Once the stack is up use make file to create and clean the dns entries so that you can connect to database from outside the cluster. 

