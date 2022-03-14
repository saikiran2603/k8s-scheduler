import datetime
from dateutil import parser
from dateutil.tz import *

from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{'host': '10.1.179.109', 'port': '9200'}],
    http_compress=True,  # enables gzip compression for request bodies
    use_ssl=False)

# Search for the document.
query_2 = {
    'size': 100,
    "query": {
        "match_phrase": {
            "kubernetes.namespace_name": "test-namespace"
        },
        # "match_phrase": {
        #     "kubernetes.pod_name": "test-schedule-periodic-1*"
        # }
        "match_phrase": {
            "kubernetes.pod_name": "nginx-always-service"
        }
    }
}

response = client.search(
    body=query_2,
    index='logstash*')

print('\nSearch results:')
print(response)
for row in response['hits']['hits']:
    # print(row)
    print("{} / {} - {} - {}".format(row['_source']['@timestamp'], parser.parse(row['_source']['@timestamp']).astimezone(tzlocal()), row['_source']['kubernetes']['pod_name'], row['_source']['message']))
    # print(row['_source']['message'])

# print(datetime.datetime.now())