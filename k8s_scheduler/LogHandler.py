import datetime
from dateutil import parser
from dateutil.tz import *
from opensearchpy import OpenSearch


class LogHandler:

    def __init__(self, elastic_search_server, elastic_search_port, worker_namespace='test-namespace',
                 index='logstash*'):
        elastic_search_server = elastic_search_server
        elastic_search_port = elastic_search_port
        self.worker_namespace = worker_namespace
        self.search_index = index

        self.client = OpenSearch(
            hosts=[{'host': elastic_search_server, 'port': elastic_search_port}],
            http_compress=True,  # enables gzip compression for request bodies
            use_ssl=False)

    def get_logs(self, schedule_name, output_json=False):
        print("Getting logs ")
        search_query = {"size": 500,
                        "query": {
                            "bool": {
                                "must": [],
                                "filter": [
                                    {
                                        "match_all": {}
                                    },
                                    {
                                        "match_phrase": {
                                            "kubernetes.namespace_name": self.worker_namespace
                                        }
                                    },
                                    {
                                        "match_phrase": {
                                            "kubernetes.pod_name": schedule_name
                                        }
                                    },
                                    # {
                                    #     "range": {
                                    #         "@timestamp": {
                                    #             "gte": "2022-03-13T19:18:22.234Z",
                                    #             "lte": "2022-03-14T10:18:22.234Z",
                                    #             "format": "strict_date_optional_time"
                                    #         }
                                    #     }
                                    # }
                                ],
                                "should": [],
                                "must_not": []
                            }
                        }
                        }

        response = self.client.search(body=search_query, index=self.search_index)
        if output_json:
            json_output = []
            # Returning json output
            for row in response['hits']['hits']:
                json_output.append({"timestamp": parser.parse(row['_source']['@timestamp']).astimezone(tzlocal()),
                                    "pod_name": row['_source']['kubernetes']['pod_name'],
                                    "output": row['_source']['message']
                                    })
            return json_output
        else:
            # Printing output to console
            for row in response['hits']['hits']:
                print("{} - {} - {}".format(parser.parse(row['_source']['@timestamp']).astimezone(tzlocal()),
                                            row['_source']['kubernetes']['pod_name'],
                                            row['_source']['message']))
