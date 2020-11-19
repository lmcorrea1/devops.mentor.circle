import requests
import json
import base64
import sys
import configparser
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import pprint

class AzureRestAgents:
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
        organization_url = config['bconfig']['organization_url']
        pool_name = config['agents']['pool_name']
        agent_name = config['agents']['agent_name']
        return {'azure_user': azure_user, 'organization': organization, 'project': project,
                'pat': pat, 'organization_url': organization_url, 'pool_name': pool_name, 'agent_name': agent_name}

    def set_payload(self, definition_id=None):
        payload = {
            "definition": {"id": definition_id},
            "parameters": "{\"testinfo\":\"DevOPS CICD TEST\"}"
        }
        return payload

    @staticmethod
    def process_pool_information(pool_name=None):
        config_values = AzureRestAgents.extract_config_information()
        credentials = BasicAuthentication('', config_values['pat'])
        connection = Connection(base_url=config_values['organization_url'], creds=credentials)
        # Get a client (the "core" client provides access to projects, teams, etc)
        agent_client = connection.clients.get_task_agent_client()
        if pool_name is not None and pool_name != "":
            get_pools_respose = agent_client.get_agent_pools()
            while get_pools_respose is not None:
                for pools in get_pools_respose:
                    pprint.pprint("[" + str(pools.id) + "] " + str(pools.name))
                    if pools.name == config_values['pool_name']:
                        pool_id = pools.id
                        pool_info = agent_client.get_agents(pool_id=pool_id)
                        break
                    else:
                        pool_info = None
                return pool_info
        else:
            get_all_pools_respose = agent_client.get_agent_pools()
            return get_all_pools_respose

    def extract_agent_information(self, agents_list=None, agent_name=None):
        if agents_list is not None and agents_list != "":
            if agent_name is not None and agent_name != "":
                while agents_list is not None:
                    for agents in agents_list:
                        if agents.name == agent_name:
                            pprint.pprint("ID[" + str(agents.id) + "] " + str(agents.name) + "[" + str(agents.status) + "]")
                    break
            else:
                for agents in agents_list:
                    pprint.pprint("ID[" + str(agents.id) + "] " + str(agents.name) + "[" + str(agents.status) + "]")
        else:
            print("No Agent information received")


def main():
    try:
        ap = AzureRestAgents()
        config_values = ap.extract_config_information()
        pools_information = ap.process_pool_information(pool_name=config_values['pool_name'])
        #print(pools_information)
        ap.extract_agent_information(agents_list=pools_information, agent_name=config_values['agent_name'])
        sys.exit(0)

    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
