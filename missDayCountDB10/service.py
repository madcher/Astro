
import requests #installed?
import json
import time
import datetime #installed
import csv
import re
from area import area
import boto3
from boto3.dynamodb.conditions import Key, Attr


def handler(event, context):
    
    res=""
    token = "Token 1b3b686c7c061abe9649d3019b40c935764f3197"

        

    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')#change regions
    table = dynamodb.Table('Activetask')#change table name
    
    #response = table.put_item( Item={ 'taskID' : str(today), 'Data': mass,})
    #return res            
    
    try:
        response = table.get_item(
            Key={
                'taskID': 'miss'                    
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        
        
    mass=response['Item']["Data"]


    
    headers = {
        'content-type': "application/json",
        
        'authorization': token #Alex
        }
    massRes=[]
    for k in mass[80:90]:
        results_url = "https://api.astrodigital.com/v2.0/results?task_id="+k
    

        results_response = requests.request("GET", results_url, headers=headers, )

        results_json_data = json.loads(results_response.text)
        if ('detail'  in results_json_data):
            break

        for i in range(0,len(results_json_data["results"])):

            res+= str(json.dumps(results_json_data["results"][i]["task"]))+"\n"
            if 'properties' in results_json_data["results"][i]["value"].keys():
                for j in range(0,len(results_json_data["results"][i]["value"]["properties"]["ndvi_values"])):
                
                    massRes.append(results_json_data["results"][i]["value"]["properties"]["ndvi_values"][j]["date"])
        massRes.sort()
        for k in range(0,len(massRes)-1):
            stime1=datetime.datetime.strptime(massRes[k+1] , '%Y-%m-%d')
            stime2=datetime.datetime.strptime(massRes[k] , '%Y-%m-%d')
            if (stime1-stime2>datetime.timedelta(days=10)):
                res+=str(stime1-stime2)[0:7]+" "+str(stime1)[0:10]+" "+str(stime2)[0:10]+"\n"#
    

    
    #res = response





    #token = "Token 0db412ef12f044d4062495f3ca26bf789b6f110f"
    
    dictSlack = {
            "strChannel" : "#random",
            "strName" : "StatBot",
            "strIconUrl" : "https://astrodigital.com/images/meta/apple-touch-icon-152x152.png",
            "strTitle" : "report",
            "strHookUrl" : "https://hooks.slack.com/services/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"
    }

    def writeToSlack(dictSlack,jsonAttachments):
            jsonPayload = {
                    "channel": dictSlack["strChannel"],
                    "username": dictSlack["strName"],
                    "icon_url": dictSlack["strIconUrl"],
                    "text": dictSlack["strTitle"],
                    "attachments": jsonAttachments,
            }
            
            payload = "-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"payload\"\r\n\r\n"+json.dumps(jsonPayload)+"\r\n-----011000010111000001101001--"
            
            headers = {
                    'content-type': "multipart/form-data; boundary=---011000010111000001101001"
                    }
            response = requests.request("POST", dictSlack["strHookUrl"], data=payload, headers=headers)


    jsonAttachments = [{
            "fallback": "Required plain-text summary of the attachment.",
            "color": "#015752",
            "fields": [{
                    "title": "Missed days:",
                    "value": str(res),
                    "Date": ""
                    
            }]
    }]
    writeToSlack(dictSlack,jsonAttachments)

##
##    jsonAttachments2 = [{
##            "fallback": "Required plain-text summary of the attachment.",
##            "color": "#015752",
##            "fields": [{
##                    "title": "Missed days:",
##                    "value": str(event),
##                    "Date": ""
##                    
##            }]
##    }]
##    writeToSlack(dictSlack,jsonAttachments2)

    res=str(event)+str(res)          


    client = boto3.client('lambda')
    response = client.invoke(
        InvocationType='Event',
        FunctionName='missDayCount11',
        Payload=json.dumps({"test": str(res)})
    )      
    return res
            



