from src.k8s_scheduler import Scheduler
from src.k8s_scheduler.LogHandler import LogHandler

scheduler = Scheduler(host="test-mongodb-0.test-mongodb-headless.test-mongodb.svc.cluster.local:27017,test-mongodb-1.test-mongodb-headless.test-mongodb.svc.cluster.local:27017",
                      username="root",
                      password="LF0t9E3KOv",
                      db_name="test_schedule")

log_handler = LogHandler(elastic_search_server='10.1.179.109',
                         elastic_search_port='9200',
                         worker_namespace='test-namespace',
                         index='logstash*')


test_job_1 = {
        "schedule_name": "test_schedule1",
        "schedule_enabled": 1,
        "schedule_description": "Test periodic schedule with hello-world ",
        "schedule_type": "periodic",
        "parallel_execution": 0,
        "schedule_crontab": {
                            "minute": "*/2",
                            "hour": "*",
                            "day_of_month": "*",
                            "month": "*",
                            "day_of_week": "*"
                            },
        "kubernetes_deployment_options": {
                                        "name": "test-schedule-periodic-1",
                                        "container_name": "hello-world",
                                        "container_image": "hello-world:latest",
                                        "restart_policy": "",
                                        "ttl_seconds_after_finished": 10,
                                        "env_vars": [],
                                        "deploy_service": 0,
                                        "service_name": "",
                                        "port": 10,
                                        "target_port": 10
                                        }
        }

test_job_2 = {
        "schedule_name": "test-schedule-2-always",
        "schedule_enabled": 1,
        "schedule_description": "test always schedule with nginx without service ",
        "schedule_type": "always",
        "parallel_execution": 0,
        "schedule_crontab": {
                            "minute": "*/2",
                            "hour": "*",
                            "day_of_month": "*",
                            "month": "*",
                            "day_of_week": "*"
                            },
        "kubernetes_deployment_options": {
                                        "name": "nginx-always",
                                        "container_name": "nginx-always",
                                        "container_image": "nginx:latest",
                                        "restart_policy": "Never",
                                        "ttl_seconds_after_finished": 10,
                                        "env_vars": [],
                                        "deploy_service": 0,
                                        "service_name": "",
                                        "port": 10,
                                        "target_port": 10
                                        }
        }

test_job_3 = {
        "schedule_name": "test-schedule-3-always",
        "schedule_enabled": 1,
        "schedule_description": "test always schedule with nginx and with service",
        "schedule_type": "always",
        "parallel_execution": 0,
        "schedule_crontab": {
                            "minute": "*/2",
                            "hour": "*",
                            "day_of_month": "*",
                            "month": "*",
                            "day_of_week": "*"
                            },
        "kubernetes_deployment_options": {
                                        "name": "nginx-always-service",
                                        "container_name": "nginx-always",
                                        "container_image": "nginx:latest",
                                        "restart_policy": "",
                                        "ttl_seconds_after_finished": 10,
                                        "env_vars": [],
                                        "deploy_service": 1,
                                        "service_name": "nginx-service",
                                        "port": 8080,
                                        "target_port": 80
                                        }
        }

job_id_1 = scheduler.create_schedule(schedule=test_job_1)
job_id_2 = scheduler.create_schedule(schedule=test_job_2)
job_id_3 = scheduler.create_schedule(schedule=test_job_3)

scheduler.start_scheduler()

log_handler.get_logs(schedule_name="nginx-always")

