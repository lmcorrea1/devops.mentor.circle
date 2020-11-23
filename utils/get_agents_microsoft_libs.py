import sys
import configparser
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from setup_logger import logger

class AzureRestAgents:
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
        organization_url = config['bconfig']['organization_url']
        pool_name = config['agents']['pool_name']
        agent_name = config['agents']['agent_name']
        return {'azure_user': azure_user, 'organization': organization, 'project': project,
                'pat': pat, 'organization_url': organization_url, 'pool_name': pool_name, 'agent_name': agent_name}

    @staticmethod
    def process_pool_information(pool_name=None):
        '''
        retreives all pools from thee provided organization and finds the pool
        name provided in the parameters.
        Args:
            pool_name (str): pool to search the agents

        Returns:
            list: list with all pools agents

        '''
        config_values = AzureRestAgents.extract_config_information()
        credentials = BasicAuthentication('', config_values['pat'])
        connection = Connection(base_url=config_values['organization_url'], creds=credentials)
        # Get a client (the "core" client provides access to projects, teams, etc)
        agent_client = connection.clients.get_task_agent_client()
        if pool_name is not None and pool_name != "":
            get_pools_respose = agent_client.get_agent_pools()
            while get_pools_respose is not None:
                for pools in get_pools_respose:
                    if pools.name == config_values['pool_name']:
                        pool_id = pools.id
                        pool_info = agent_client.get_agents(pool_id=pool_id)
                        break
                    else:
                        pool_info = None
                return pool_info
        else:
            logger.warning("Pool Name is not set")
            return None
            #get_all_pools_respose = agent_client.get_agent_pools()

    def extract_agent_information(self, agents_list=None, agent_name=None):
        '''
        this will process the list of agents and return the agent status

        Args:
            agents_list (list) : receives the agent list
            agent_name (str): agent name

        Returns:
            list: agents and its status or single agent if agent_name provided.

        '''
        if agents_list is not None and agents_list != "":
            if agent_name is not None and agent_name != "":
                for agents in agents_list:
                    if agents.name == agent_name:
                        return f"id:{agents.id} name:{agents.name} status:{agents.status}"
                        break
                else:
                    logger.warning(f"No Agent {agent_name} Found")
                    return None
            else:
                agents_info = []
                for agents in agents_list:
                    agents_info.append(f"id:{agents.id} name:{agents.name} status:{agents.status}")
                return agents_info
        else:
            logger.warning(f"No Agent information received from the Pool")
            return None


def main():
    '''

    Returns:
        list of agents and its status or single agent if agent_name provided.

    '''
    try:
        ap = AzureRestAgents()
        config_values = ap.extract_config_information()
        pools_information = ap.process_pool_information(pool_name=config_values['pool_name'])
        result = ap.extract_agent_information(agents_list=pools_information, agent_name=config_values['agent_name'])
        if result:
            print(result)
    except Exception as e:
        return e

if __name__ == '__main__':
    sys.exit(main())
