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
    headers = {
            'content-type': "application/json",

            'authorization': "" #Alex
            #'authorization': "b" #My
            }
    # вход на сайт
    mass=[]

    def ndvi(token):
        headers = {
            'content-type': "application/json",
            
            'authorization': token #Alex
            }
                    
        today=datetime.datetime.today()
        today=today- datetime.timedelta(days=30)
        today=today.strftime('%Y-%m-%d')
        results_url = "https://api.astrodigital.com/v2.0/results?product=ndvi_value&page_size=100&updated_from="+today #сайт куда делаем запрос

        results_response = requests.request("GET", results_url, headers=headers, )

        results_json_data = json.loads(results_response.text)

        if ('detail'  in results_json_data):
            if(results_json_data['detail']=='Not found.'):
                time.sleep(15)

        for i in range(0,len(results_json_data["results"])):

            mass.append(json.dumps(results_json_data["results"][i]["task"]))

        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')#change regions
        table = dynamodb.Table('Activetask')#change table name
        response = table.put_item( Item={ 'taskID' : "miss", 'Data': mass,})
        return res            
        
    






    #token = ""
    token = ""
    ndvi(token)
    client = boto3.client('lambda')
    response = client.invoke(
        InvocationType='Event',
        FunctionName='missDauCount2',
        Payload=json.dumps({"test": "test"})
    )  
    return res
            



