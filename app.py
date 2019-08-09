from __future__ import print_function
import os
import sys
# import json
from kubernetes import client, config, watch
from kubernetes.client.models.v1_event_list import V1EventList
from flask_jsonpify import jsonify
from flask import Flask
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)

with app.app_context():
    config.load_kube_config(
        os.path.join(os.environ["HOME"], '.kube/config'))

    v1 = client.CoreV1Api()


class Pods(Resource):
    def get(self):
        result = []
        ret = v1.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            # print("%s\t%s\t%s" % (i.status.phase, i.metadata.namespace, i.metadata.name))
            try:
                size = len(i.status.container_statuses)
                containerCount = 0
                for container in i.status.container_statuses:
                    if(container.state.running != None):
                        containerCount = containerCount + 1
                    ready = str(containerCount) + '/' + str(size)
                    print("%s\t%s" % (i.metadata.name, ready))
                    Pod = {
                        "name": i.metadata.name,
                        "ready": ready,
                    }
                    result.append(Pod)
            except Exception as e:
                print('Error', e, size, file=sys.stderr)
        return jsonify(result)


class Events(Resource):
    def get(self):
        result = []
        # stream = watch.Watch().stream(v1.list_namespaced_pod, "default")
        # for event in stream:
        #     print("Event: %s %s %s " % (
        #         event['type'],  event['object'].kind, event['object'].metadata.name))
        #     # print("%s" %(stream.object))
        allNamespacesEvents = v1.list_event_for_all_namespaces()
        for item in allNamespacesEvents.items:
            # if item.type == "Warning" or item.type == "error":
            Event = {
                "name": item.metadata.name,
                "type": item.type,
                "message": item.message,

            }
            result.append(Event)

        return result


api.add_resource(Pods, '/pods')  # Route_1
api.add_resource(Events, '/events')  # Route_2
if __name__ == '__main__':
    app.run(port='5007')
