# -*- coding: utf-8 -*-
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
    count=0
    token = "Token 0db412ef12f044d4062495f3ca26bf789b6f110f"
    headers = {
	'content-type': "application/json",
        
	'authorization': token #Alex
        #'authorization': "Token 5cd1d86622ece4d66cfe218b1b6c020e2a6ac1db" #My
	}
    today=datetime.datetime.today()
    day=today- datetime.timedelta(days=30)
    day=day.strftime('%Y-%m-%d')
    today=today.strftime('%Y-%m-%d')
    results_url = "https://api.astrodigital.com/v2.0/tasks?product=ndvi_value&page_size=1000&updated_from="+day #сайт куда делаем запрос
    #results_url = "https://api.astrodigital.com/v2.0/tasks?date_from=2017-05-01&date_to=2017-06-17&page_size=1000" #сайт куда делаем запрос

    results_response = requests.request("GET", results_url, headers=headers, )

    results_json_data = json.loads(results_response.text)

    for i in range(0,len(results_json_data["results"])):
        #print results_json_data["results"][i]["status"]#addthis
        if results_json_data["results"][i]["status"]!="DRAFT" and results_json_data["results"][i]["status"]!="COMPLETED"  :
            

                    
            res+="Task id: "+str(results_json_data["results"][i]["id"])+" \n"+str(results_json_data["results"][i]["status"])+" Task aoi: "+str(results_json_data["results"][i]["aoi"])+"\n Task date from: "+str(results_json_data["results"][i]["query"]["date_from"])+ " Task date to: "+str(results_json_data["results"][i]["query"]["date_to"])  
            count+=1
    if count==0:
        res= "No incomplited tasks with ndvi_value in last 30 days"
        
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')#change regions
    table = dynamodb.Table('Activetask')#change table name
    response = table.put_item( Item={ 'taskID' : "active"+today, 'Data': str(res),})
    
    

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
            "color": "#a6364f",
            "fields": [{
                    "title": "Incomplited tasks:",
                    "value": str(res),
                    "Date": str(today)
                    
            }]
    }]
    writeToSlack(dictSlack,jsonAttachments)  
    return res
            



