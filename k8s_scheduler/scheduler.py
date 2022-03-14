import random
import time
import os
from multiprocessing import Process
from .connection import ConnectionManager
from .SchedulerBackend import SchedulerBackend
from .ResultsBackend import ResultBackend
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException
from croniter import croniter
from croniter import croniter_range
from datetime import datetime, timedelta


class Scheduler:

    def __init__(self,
                 db_name="k8s_scheduler",
                 scheduler_collection_name="test_coll",
                 result_db_collection='result_coll',
                 scheduler_poll_interval=10,
                 k8s_worker_namespace="test-namespace",
                 k8s_config_file_path='/var/snap/microk8s/current/credentials/client.config',
                 **kwargs):

        self.db_name = db_name
        self.mongo_connection_settings = kwargs
        self.scheduler_collection_name = scheduler_collection_name
        self.scheduler_poll_interval = scheduler_poll_interval
        self.k8s_config_file_path = k8s_config_file_path
        self.k8s_worker_namespace = k8s_worker_namespace
        self.result_collection_name = result_db_collection

        self.db_scheduler_connection, self.result_db_connection = self.get_mongo_connection()
        self.scheduler_backend = SchedulerBackend()
        self.result_backend = ResultBackend()
        self.k8s_client, self.k8s_batch_client = self.get_kubernetes_client()
        self.create_worker_namespace_if_not_exists()

    def get_kubernetes_client(self):
        # Configure Kubernetes client
        if 'KUBERNETES_SERVICE_HOST' in os.environ:
            config.load_incluster_config()
        else:
            config.load_kube_config(self.k8s_config_file_path)

        k8s_client = client.ApiClient()
        v1 = client.CoreV1Api(k8s_client)
        apps_v1 = client.AppsV1Api()
        batch_api = client.BatchV1Api(k8s_client)
        return v1, batch_api

    def create_worker_namespace_if_not_exists(self):
        namespace_list = self.k8s_client.list_namespace()
        namespaces = [item.metadata.name for item in namespace_list.items]

        if self.k8s_worker_namespace in namespaces:
            print("Namespace exists ")
        else:
            self.k8s_client.create_namespace(
                client.V1Namespace(metadata=client.V1ObjectMeta(name=self.k8s_worker_namespace)))

    def get_mongo_connection(self):
        connection_manager = ConnectionManager(db_name=self.db_name, **self.mongo_connection_settings)
        connection = connection_manager.get_connection()
        self.db_scheduler_connection = connection[self.scheduler_collection_name]
        self.result_db_connection = connection[self.result_collection_name]
        return self.db_scheduler_connection, self.result_db_connection

    def create_schedule(self, **kwargs):
        """
        Creates a Schedule entry
        :param kwargs:
        schedule -
        {
        "schedule_name": "",
        "schedule_enabled": 0,
        "schedule_description": "",
        "schedule_type": "periodic/always",
        "parallel_execution": 0,
        "schedule_crontab": {
                            "minute": "",
                            "hour": "",
                            "day_of_week": "",
                            "day_of_month": "",
                            "month_of_year": ""
                            },
        "kubernetes_deployment_options": {
                                        "name": "",
                                        "container_name": "",
                                        "container_image": "",
                                        "restart_policy": "",
                                        "ttl_seconds_after_finished": 10,
                                        "env_vars": [],
                                        "deploy_service": 0
                                        "service_name": ""
                                        "port": 10
                                        "target_port": 10
                                        }
        }

        :return:
        """
        return self.scheduler_backend.create_schedule(self.db_scheduler_connection, kwargs['schedule'])

    def disable_schedule(self, schedule_id):
        return self.scheduler_backend.disable_schedule(self.db_scheduler_connection, schedule_id)

    def purge_schedule(self, schedule_id):
        return self.scheduler_backend.purge_schedule(self.db_scheduler_connection, schedule_id)

    def create_k8s_job(self, job_name, container_name, container_image, restart_policy="Never", ttl_seconds_after_finished=10, env_vars=[]):
        body = client.V1Job(api_version="batch/v1", kind="Job")
        body.metadata = client.V1ObjectMeta(namespace=self.k8s_worker_namespace, name=job_name)
        body.status = client.V1JobStatus()
        template = client.V1PodTemplate()
        template.template = client.V1PodTemplateSpec()
        env_list = []
        for env_name, env_value in env_vars:
            env_list.append(client.V1EnvVar(name=env_name, value=env_value))
        container = client.V1Container(name=container_name, image=container_image, env=env_list)
        template.template.spec = client.V1PodSpec(containers=[container], restart_policy=restart_policy)
        body.spec = client.V1JobSpec(ttl_seconds_after_finished=ttl_seconds_after_finished, template=template.template)

        try:
            api_response = self.k8s_batch_client.create_namespaced_job(self.k8s_worker_namespace, body, pretty='true')
            print("*********************** Job Created : {} ******************************".format(job_name))
            # print(api_response)
            # job_resp = self.k8s_batch_client.read_namespaced_job(name=job_name, namespace=self.k8s_worker_namespace)
            # print(job_resp)
        except ApiException as e:
            print("Exception when calling Create Namespaced Job : %s\n" % e)

    def create_k8s_pod(self, pod_name, container_name, container_image, restart_policy='Never', env_vars=[]):
        pod_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'labels': {
                    'bot': pod_name
                },
                'name': pod_name
            },
            'spec': {
                'containers': [{
                    'image': container_image,
                    'pod-running-timeout': '5m0s',
                    'name': container_name,
                    'env': env_vars
                }],
                'restartPolicy': restart_policy,
            }
        }
        try:
            api_response = self.k8s_client.create_namespaced_pod(self.k8s_worker_namespace, pod_manifest, pretty='true')
            print("*********************** Pod Created : {} ******************************".format(pod_name))
            # print(api_response)
            # pod_resp = self.k8s_client.read_namespaced_pod(name=pod_name, namespace=self.k8s_worker_namespace)
            # print(pod_resp)
        except ApiException as e:
            print("Exception when calling Create Namespaced Pod : %s\n" % e)

    def create_k8s_service(self, service_name, port, target_port):
        manifest = {
            "kind": "Service",
            "apiVersion": "v1",
            "metadata": {
                "name": service_name
            },
            "spec": {
                "selector": {
                    "app": service_name
                },
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": port,
                        "targetPort": target_port
                    }
                ]
            }
        }
        try:
            api_response = self.k8s_client.create_namespaced_service(self.k8s_worker_namespace, manifest, pretty='true')
            print("*********************** Service Created : {} ******************************".format(service_name))

        except ApiException as e:
            print("Exception when calling Create Namespaced Service : %s\n" % e)

    def parse_crontab(self, minute, hour, day_of_month, month, day_of_week, base=datetime.now()):
        cron_expression = minute + " " + hour + " " + day_of_month + " " + month + " " + day_of_week
        iter = croniter(cron_expression, base)
        return iter.get_next(datetime), iter.all_next(datetime), iter.all_prev(datetime)

    def check_crontab_schedule(self, minute, hour, day_of_month, month, day_of_week, start_date , end_date):
        cron_expression = minute + " " + hour + " " + day_of_month + " " + month + " " + day_of_week
        schedule = list(croniter_range(start_date, end_date, cron_expression))

        if bool(len(schedule)):
            return bool(len(schedule)), schedule[0]
        else:
            return bool(len(schedule)), None

    def check_periodic_schedules(self, schedule_rec, result_db_collection):
        # print("Checking Periodic Schedules ")
        k8s_rec = schedule_rec['kubernetes_deployment_options']

        if schedule_rec['parallel_execution'] == 0:
            # Jobs are not to be executed in parallel , check if job is running

            try:
                job_status = self.k8s_batch_client.read_namespaced_job_status(name=k8s_rec['name'], namespace=self.k8s_worker_namespace)
                if job_status.status.active == 1:
                    # Job is running
                    job_active = True
                elif job_status.status.active is None and job_status.status.succeeded == 1:
                    # Job is completed waiting for timeout to purge the job
                    job_active = True
                else:
                    # Handle exception case
                    job_active = True
            except ApiException:
                job_active = False
        else:
            # Job can run in parallel change the job name and add a unique identifier to job name
            job_active = False
            k8s_rec['name'] = k8s_rec['name'] + "-" + "" + str(random.randint(1000,9999))

        if job_active is False:
            create_job_args = {"job_name": k8s_rec['name'],
                               "container_name": k8s_rec['container_name'],
                               "container_image": k8s_rec['container_image'],
                               "env_vars": k8s_rec['env_vars']}

            if k8s_rec['ttl_seconds_after_finished'] != "":
                create_job_args['ttl_seconds_after_finished'] = k8s_rec['ttl_seconds_after_finished']

            if k8s_rec['restart_policy'] != "":
                create_job_args['restart_policy'] = k8s_rec['restart_policy']

            self.create_k8s_job(**create_job_args)
            self.result_backend.insert_result_record(result_db_collection, {"schedule_name": k8s_rec['name'],
                                                                            "schedule_date": datetime.now()})

    def check_stream_jobs(self, schedule_rec, result_db_collection):
        # print("Checking Stream Schedules ")
        k8s_rec = schedule_rec['kubernetes_deployment_options']

        # In case of stream pods , no need to check if pod is running , no parallel execution happens. Check if pod is not running, and launch if not.
        # Also if restart policy is Never , then delete the job and launch again

        try:
            pod_status = self.k8s_client.read_namespaced_pod_status(name=k8s_rec['name'], namespace=self.k8s_worker_namespace)
            if pod_status.status.phase in ["Running", "Pending"]:
                launch_pod = False
            elif pod_status.status.phase == 'Succeeded':
                print("Deleting pod and recreating it ")
                self.k8s_client.delete_namespaced_pod(name=k8s_rec['name'], namespace=self.k8s_worker_namespace)
                self.k8s_client.delete_namespaced_service(name=k8s_rec['service_name'], namespace=self.k8s_worker_namespace)
                launch_pod = True
            elif pod_status.status.phase == 'Failed':
                print("Deleting pod and recreating it ")
                self.k8s_client.delete_namespaced_pod(name=k8s_rec['name'], namespace=self.k8s_worker_namespace)
                self.k8s_client.delete_namespaced_service(name=k8s_rec['service_name'], namespace=self.k8s_worker_namespace)
                launch_pod = True
            else:
                # Handle case when the pod does not launch at all
                launch_pod = False
        except ApiException:
            # Pod is not scheduled , Schedule the pod.
            launch_pod = True

        if launch_pod:
            # pod_name, container_name, container_image, restart_policy='Always', env_vars=[]
            launch_pod_args = {"pod_name": k8s_rec['name'],
                               "container_name": k8s_rec['container_name'],
                               "container_image": k8s_rec['container_image'],
                               "env_vars": k8s_rec['env_vars']}

            if k8s_rec['restart_policy'] != "":
                launch_pod_args['restart_policy'] = k8s_rec['restart_policy']

            self.create_k8s_pod(**launch_pod_args)
            self.result_backend.insert_result_record(result_db_collection, {"schedule_name": k8s_rec['name'],
                                                                            "schedule_date": datetime.now()})

            # check if service needs to be launched.
            if k8s_rec['deploy_service'] == 1:
                self.create_k8s_service(service_name=k8s_rec['service_name'],
                                        port=k8s_rec['port'],
                                        target_port=k8s_rec['target_port'])

    def check_schedules(self, test):
        schedule_db_collection, result_db_collection = self.get_mongo_connection()
        print("******************** Starting Scheduler ******************************************")
        while True:
            start_time = datetime.now()
            records = schedule_db_collection.find({})
            for rec in records:
                if rec['schedule_type'] == 'periodic':
                    # check crontab schedule and determine if the job is to be executed or not
                    run_schedule, schedule_date = self.check_crontab_schedule(start_date=start_time,
                                                                              end_date=start_time + timedelta(seconds=self.scheduler_poll_interval),
                                                                              **rec['schedule_crontab'])
                    if run_schedule:
                        print("Running Scheduled job as per schedule - {} at current time {} ".format(schedule_date, datetime.now()))
                        self.check_periodic_schedules(rec, result_db_collection)
                elif rec['schedule_type'] == 'always':
                    self.check_stream_jobs(rec, result_db_collection)
                else:
                    print("Unknown Type of schedule - " + str(rec))

            # Determine how many seconds the program should sleep now , calculate elapsed time till now and compute total sleep time
            elapsed_time = datetime.now() - start_time
            sleep_time = self.scheduler_poll_interval - elapsed_time.seconds
            print("Scheduler ({}) : Sleeping for {} seconds of {} seconds scheduled sleep time".format(datetime.now(), sleep_time, self.scheduler_poll_interval))
            time.sleep(sleep_time)

    def start_scheduler(self):
        p = Process(target=self.check_schedules, args=('Peter',))
        p.start()
