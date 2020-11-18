import requests
import json
import base64
import sys
import configparser
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import pprint

class AzureRest:
    pass

    @staticmethod
    def extract_config_information():
        config = configparser.ConfigParser()
        config.read('azure_config.cfg')
        # defining the api-endpoint
        azure_user = config['bconfig']['azure_user']
        organization = config['bconfig']['organization']
        project = config['bconfig']['project']
        pat = config['bconfig']['pat']
        build_name = config['bconfig']['build_name']
        organization_url = config['bconfig']['organization_url']
        return {'azure_user': azure_user, 'organization': organization, 'project': project,
                'pat': pat, 'build_name': build_name, 'organization_url': organization_url}

    def set_payload(self, definition_id=None):
        payload = {
            "definition": {"id": definition_id},
            "parameters": "{\"testinfo\":\"DevOPS CICD TEST\"}"
        }
        return payload

    @staticmethod
    def process_build_information():
        config_values = AzureRest.extract_config_information()
        credentials = BasicAuthentication('', config_values['pat'])
        connection = Connection(base_url=config_values['organization_url'], creds=credentials)
        # Get a client (the "core" client provides access to projects, teams, etc)
        build_client = connection.clients.get_build_client()
        get_builds_response = build_client.get_builds(project=config_values['project'])
        index = 0
        while get_builds_response is not None:
            for builds in get_builds_response.value:
                pprint.pprint("[" + str(index) + "] " + str(builds.definition.id))
                index += 1
                if builds.definition.name == config_values['build_name']:
                    definition_id = builds.definition.id
                    break
                else:
                    definition_id = None

            if get_builds_response.continuation_token is not None and get_builds_response.continuation_token != "":
                # Get the next page of projects
                get_builds_response = build_client.get_builds(project=config_values['project'],
                                                              continuation_token=get_builds_response.continuation_token)
            else:
                # All projects have been retrieved
                get_builds_response = None
        return definition_id


def main():
    try:
        ap = AzureRest()
        config_values = ap.extract_config_information()
        build_to_trigger = ap.process_build_information()
        print(build_to_trigger)
        payload = ap.set_payload(build_to_trigger)
        credentials = BasicAuthentication('', config_values['pat'])
        connection = Connection(base_url=config_values['organization_url'], creds=credentials)
        # Get a client (the "core" client provides access to projects, teams, etc)
        build_client = connection.clients.get_build_client()
        queue_builds_response = build_client.queue_build(build=payload, project=config_values['project'])
        print(queue_builds_response)
        sys.exit(0)

    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
