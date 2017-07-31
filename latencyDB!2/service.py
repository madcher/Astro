# -*- coding: utf-8 -*-


##
##1. Вывести список  тасков с ndvi_value за последние 30 дней - в GETtasks
##запросе тебе нужно указать product=ndvi_values - их в одной таске может быть несколько. По одной на feature в feature Collection.
##
##2. Убедиться, что присутствуют все результаты в диапазоне date_from - date_to.
##Могут быть пропуски по 1-2 результата
##
##3. Посмотреть насколько запаздывает самый свежий результат. Должно быть не более 14 дней.
##Если больше - нужно алертить = писать task_id, result_id в отдельный файл.
##
##—

import requests #installed?
import json
import time
import datetime #installed
import csv
import re
from area import area
import boto3
from boto3.dynamodb.conditions import Key, Attr

headers = {
	'content-type': "application/json",

	'authorization': "Token 0db412ef12f044d4062495f3ca26bf789b6f110f" #Alex
        #'authorization': "Token 5cd1d86622ece4d66cfe218b1b6c020e2a6ac1db" #My
	}
# вход на сайт

def handler(event, context):
    res=""
    token = "Token 0db412ef12f044d4062495f3ca26bf789b6f110f"
    headers = {
	'content-type': "application/json",
        
	'authorization': token #Alex
        #'authorization': "Token 5cd1d86622ece4d66cfe218b1b6c020e2a6ac1db" #My
	}
    
    results_url = "https://api.astrodigital.com/v2.0/results?status=INPROGRESS&page_size=1000" #сайт куда делаем запрос
    #results_url = "https://api.astrodigital.com/v2.0/tasks?date_from=2017-05-01&date_to=2017-06-17&page_size=1000" #сайт куда делаем запрос

     
    results_response = requests.request("GET", results_url, headers=headers, )
    today = datetime.datetime.today()
    #stime='2099-06-23T23:53:39Z'
    
    difference = today - today
    
    results_json_data = json.loads(results_response.text)

    if ('detail'  in results_json_data):
        if(results_json_data['detail']=='Not found.'):
            time.sleep(15)
            
    for i in range(0,len(results_json_data["results"])):
        #print results_json_data["results"][i]["status_time"]
        stime=results_json_data["results"][i]["status_time"]
        stime=datetime.datetime.strptime(stime , '%Y-%m-%dT%H:%M:%SZ')
        
        difference1 = today - stime
        if difference1>difference:
            difference=difference1
        #print "Timeout:", difference, "Result ID:", results_json_data["results"][i]['id']
        #print json.dumps(results_json_data, sort_keys=True, indent=4, separators=(',', ': '))
        if (difference>datetime.timedelta(days=1)):
            res+="Result ID: "+str(results_json_data["results"][i]['id'])+" \n"+"Timeout: "+str(difference)+"\n \n"
        #----------------------------------------------------------------------------------------------
    today=datetime.datetime.today()    
    today=today.strftime('%Y-%m-%d')

    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')#change regions
    table = dynamodb.Table('Activetask')#change table name
    response = table.put_item( Item={ 'taskID' : "latency"+str(today), 'Data': str(res),})

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
            "color": "#009494",
            "fields": [{
                    "title": "Latency report",
                    "value": str(res),
                    "Date": str(today)
                    
            }]
    }]
    writeToSlack(dictSlack,jsonAttachments)  


    
    return res        
