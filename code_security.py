__author__ = "Simon Melotte"

import json
import os
import requests
import urllib.parse
from re import search
from datetime import datetime

def getRepositories(base_url, token):
    url = "https://%s/code/api/v1/repositories" % ( base_url )
    headers = {"content-type": "application/json; charset=UTF-8", 'Authorization': 'Bearer ' + token }    
    response = requests.get(url, headers=headers)
    repositories = response.json()
    for repository in repositories:
        output("""REPOSITORIES: id="{}" fullRepositoryName="{}/{}" repository="{}" owner="{}" source="{}" """.format(repository['id'],repository['owner'], repository['repository'] , repository['repository'], repository['owner'], repository['source'] ) )    


## sourceType = Github, Bitbucket, Gitlab, AzureRepos, cli, AWS, Azure, GCP, githubEnterprise, gitlabEnterprise, bitbucketEnterprise, terraformCloud, tfcRunTasks, githubActions, circleci, codebuild, jenkins, kubernetesWorkloads, Kubernetes, admissionController
def getBlameAuthors(base_url, token, repoName, sourceType):
    url = "https://%s/code/api/v1/errors/gitBlameAuthors" % ( base_url)
    querystring  = {'fullRepoName': repoName, 'sourceType': sourceType}
    headers = {"content-type": "application/json; charset=UTF-8", 'Authorization': 'Bearer ' + token }    
    response = requests.get(url, headers=headers, params=querystring)
    authors = response.json()

    output("""Code API returns: {}""".format(response.text) )    

## sourceType = Github, Bitbucket, Gitlab, AzureRepos, cli, AWS, Azure, GCP, githubEnterprise, gitlabEnterprise, bitbucketEnterprise, terraformCloud, tfcRunTasks, githubActions, circleci, codebuild, jenkins, kubernetesWorkloads, Kubernetes, admissionController
def getErrorsFiles(base_url, token, policies, repoName, sourceType):
    url = "https://%s/code/api/v1/errors/files" % ( base_url)
    payload = {"repository": repoName, "sourceTypes": [sourceType] }
    headers = {"content-type": "application/json", 'Authorization': 'Bearer ' + token }    
    response = requests.post(url, headers=headers, json=payload)

    files = response.json()
    for file in files["data"]:
        getErrorsPerFile(base_url, token, policies, "807098694255043584_njannasch-pan/kubernetes-goat", "githubActions", file["filePath"])

## sourceType = Github, Bitbucket, Gitlab, AzureRepos, cli, AWS, Azure, GCP, githubEnterprise, gitlabEnterprise, bitbucketEnterprise, terraformCloud, tfcRunTasks, githubActions, circleci, codebuild, jenkins, kubernetesWorkloads, Kubernetes, admissionController
def getErrorsPerFile(base_url, token, policies, repoName, sourceType, filePath):
    url = "https://%s/code/api/v1/errors/file" % ( base_url)    
    payload = {"repository": repoName, "sourceTypes": [sourceType] , "filePath": filePath, "types": ["Errors"]}
    headers = {"content-type": "application/json", 'Authorization': 'Bearer ' + token }    
    response = requests.post(url, headers=headers, json=payload)

    errors = response.json()
    for error in errors["data"]:
        policy = getPolicyDetail(policies, error['errorId'])        
        output("""filePath="{}" errorId="{}" frameworkType="{}" isFixable="{}" name="{}" severity="{}" """.format(error['filePath'],error['errorId'], error['frameworkType'] , error['isFixable'], policy["title"], policy["pcSeverity"] )  )   


def getPolicyDetail(policies, policyId):  
    for policy in policies["policyMetadata"]:
        if policies["policyMetadata"][policy]["id"] == policyId:
            return policies["policyMetadata"][policy]
      

def getPoliciesDetail(base_url, token):
    url = "https://%s/code/api/v1/checkov/runConfiguration?module=pc" % ( base_url)
    headers = {"content-type": "application/json", 'Authorization': 'Bearer ' + token }    
    response = requests.get(url, headers=headers)
    return response.json()

def output(myString):
    eventFile = open("events.log", "a")
    eventFile.write("""{} - {}\n""".format(datetime.now(), myString) )
    print ("""{}""".format(myString) )
    eventFile.close()  

def login_cwp(base_url, access_key, secret_key): 
    url = "https://%s/api/v1/authenticate" % ( base_url )

    payload = json.dumps({
        "username": access_key,
        "password": secret_key
    })
    headers = {"content-type": "application/json; charset=UTF-8"}    
    response = requests.post(url, headers=headers, data=payload)
    return response.json()["token"]

def login_saas(base_url, access_key, secret_key): 
    url = "https://%s/login" % ( base_url )

    payload = json.dumps({
        "username": access_key,
        "password": secret_key
    })
    headers = {"content-type": "application/json; charset=UTF-8"}    
    response = requests.post(url, headers=headers, data=payload)
    return response.json()["token"]

def getParamFromJson(config_file):
    f = open(config_file,)
    params = json.load(f)
    api_endpoint = params["api_endpoint"]
    pcc_api_endpoint = params["pcc_api_endpoint"]
    access_key_id = params["access_key_id"]
    secret_key = params["secret_key"]
    # Closing file
    f.close()
    return api_endpoint, pcc_api_endpoint, access_key_id, secret_key;

def main():    
    CONFIG_FILE= os.environ['HOME'] + "/.prismacloud/credentials-legacy.json"
    API_ENDPOINT, PCC_API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY = getParamFromJson(CONFIG_FILE)
    token = login_saas(API_ENDPOINT, ACCESS_KEY_ID, SECRET_KEY)    
    
    ## List all repositories
    # getRepositories(API_ENDPOINT, token)
    
    ## Get all policies metadata
    policies = getPoliciesDetail(API_ENDPOINT, token)

    ## Get all errors for a given repository
    getErrorsFiles(API_ENDPOINT, token, policies, "example-pan/kubernetes-goat", "githubActions")

if __name__ == "__main__":
    main()