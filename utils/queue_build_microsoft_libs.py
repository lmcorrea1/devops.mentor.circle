import requests
import json
import base64
import sys
import configparser
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from setup_logger import logger

class AzureRest:
    pass

    @staticmethod
    def extract_config_information():
        '''

        Returns:
            Dict: with the obtained information from the config file.

        '''
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
    def process_build_information(project, build_name, pat, organization_url):
        '''

        Args:
            project (str): azure project where the build resides
            build_name (str): build name from above project
            pat (str): personal access token needed to trigger the build
            organization_url (str): organization url to search for project and build.

        Returns:
            int: number that represents the azure build

        '''
        credentials = BasicAuthentication('', pat)
        connection = Connection(base_url=organization_url, creds=credentials)
        # Get a client (the "core" client provides access to projects, teams, etc)
        build_client = connection.clients.get_build_client()
        get_builds_response = build_client.get_builds(project=project)
        index = 0
        while get_builds_response is not None:
            for builds in get_builds_response.value:
                logger.info(f"[{index}] {builds.definition.id}")
                index += 1
                if builds.definition.name == build_name:
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
        build_to_trigger = ap.process_build_information(config_values['project'], config_values['build_name'],
                                                        config_values['pat'], config_values['organization_url'])
        print(build_to_trigger)
        payload = ap.set_payload(build_to_trigger)
        credentials = BasicAuthentication('', config_values['pat'])
        connection = Connection(base_url=config_values['organization_url'], creds=credentials)
        # Get a client (the "core" client provides access to projects, teams, etc)
        build_client = connection.clients.get_build_client()
        queue_builds_response = build_client.queue_build(build=payload, project=config_values['project'])
        logger.info(f"{queue_builds_response}")

    except Exception as e:
        print(e)


if __name__ == '__main__':
    sys.exit(main())
