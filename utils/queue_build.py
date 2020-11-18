import requests
import json
import base64
import sys
import configparser

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
        build_def_id = config['bconfig']['build_def_id']
        pat = config['bconfig']['pat']
        return {'azure_user': azure_user, 'organization': organization, 'project': project,
                'build_def_id': build_def_id, 'pat': pat}

    def set_payload(self):
        config_values = AzureRest.extract_config_information()
        payload = {
            "definition": {"id": config_values['build_def_id'], "project": config_values['project']},
            "parameters": "{\"testinfo\":\"DevOPS CICD TEST\"}"
        }
        return payload

    @staticmethod
    def set_header():
        config_values = AzureRest.extract_config_information()
        azure_user = config_values['azure_user']
        pat = config_values['pat']
        aut = azure_user + ":" + pat
        api_key = base64.b64encode(aut.encode()).decode()
        http_headers = {'Content-Type': 'application/json',
                        'Authorization': "Basic %s" % api_key}
        return http_headers

    @staticmethod
    def set_api_endpoint():
        config_values = AzureRest.extract_config_information()
        organization = config_values['organization']
        project = config_values['project']
        api_end_point = "https://dev.azure.com/{0}/{1}/_apis/build/builds/?api-version=5.1".format(organization, project)
        return api_end_point

    # sending post request and saving response as response object
    @staticmethod
    def rest_api_request(http_method=None, url=None, data=None, headers=None):
        if http_method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            if http_method == 'GET':
                httpresp = requests.get(url, headers=headers, verify=False)
            elif http_method == 'POST':
                httpresp = requests.post(url, data, headers=headers, verify=False)
            elif http_method == 'PUT':
                httpresp = requests.put(url, data, headers=headers, verify=False)
            elif http_method == 'PATCH':
                httpresp = requests.patch(url, data, headers=headers, verify=False)
            elif http_method == 'DELETE':
                httpresp = requests.delete(url, headers=headers, verify=False)
            return httpresp
        else:
            raise Exception('Invalid HTTP method:{}'.format(http_method))


def main():
    try:
        ap = AzureRest()
        payload = ap.set_payload()
        http_headers = ap.set_header()
        api_endpoint = ap.set_api_endpoint()
        r = ap.rest_api_request('POST', api_endpoint, json.dumps(payload), http_headers)
        pastebin_url = json.loads(r.text)
        print(json.dumps(pastebin_url, indent=4, sort_keys=True))
        #print("The response IS :%s" % pastebin_url)

    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
