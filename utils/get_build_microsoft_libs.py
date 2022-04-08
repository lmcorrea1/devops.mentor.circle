import datetime
import sys
import configparser
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from setup_logger import logger
# otro commit 

#conflict11
#conflict12
#git test Cherry
class AzureBuildInfo:
    pass

    @staticmethod
    def extract_config_information():
        '''
        reads configuration file and sets variables

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

    @staticmethod
    def process_build_information(project, build_name, pat, organization_url):
        '''
        retreives all builds from the specified project and returns build info
        if build_name found
        Args:
            project (str): azure project where the build resides
            build_name (str): build name from above project
            pat (str): personal access token needed to trigger the build
            organization_url (str): organization url to search for project and build.

        Returns:
            int: number that represents the azure build

        '''
        ## commit testing
        credentials = BasicAuthentication('', pat)
        connection = Connection(base_url=organization_url, creds=credentials)
        # Get a client (the "core" client provides access to projects, teams, etc)
        build_client = connection.clients.get_build_client()
        get_builds_response = build_client.get_builds(project=project)
        flag = 0
        while get_builds_response is not None:
            for builds in get_builds_response.value:
                #logger.info(f"[{index}] {builds.id}")
                if builds.definition.name == build_name:
                    build_name = builds.definition.name
                    source_branch = builds.source_branch
                    requested_by =  builds.requested_by.unique_name
                    build_id = builds.id
                    queue_time = builds.queue_time.strftime("%d-%b-%Y %H:%M:%S.%f")
                    start_time = builds.start_time.strftime("%d-%b-%Y %H:%M:%S.%f")
                    finish_time = builds.finish_time.strftime("%d-%b-%Y %H:%M:%S.%f")
                    result = builds.result
                    status = builds.status
                    flag = 1
                    break

            if get_builds_response.continuation_token is not None and get_builds_response.continuation_token != "":
                # Get the next page of projects
                get_builds_response = build_client.get_builds(project=config_values['project'],
                                                              continuation_token=get_builds_response.continuation_token)
            else:
                # All projects have been retrieved
                get_builds_response = None
        if flag == 0:
            logger.warning(f"did not find any information related to build {build_name}")
            return None

        return {'build_id': build_id, 'build_name': build_name, 'requested_by': requested_by, 'source_branch':source_branch, 'queue_time': queue_time, 'start_time': start_time,
                'finish_time': finish_time, 'result': result, 'status': status}


def main():
    try:
        ap = AzureBuildInfo()
        config_values = ap.extract_config_information()
        logger.info(f"Getting Build Information")
        build_info = ap.process_build_information(config_values['project'], config_values['build_name'],
                                                        config_values['pat'], config_values['organization_url'])
        print(build_info)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    sys.exit(main())
