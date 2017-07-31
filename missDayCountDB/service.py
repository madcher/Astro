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

            'authorization': "Token 0db412ef12f044d4062495f3ca26bf789b6f110f" #Alex
            #'authorization': "Token 5cd1d86622ece4d66cfe218b1b6c020e2a6ac1db" #My
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
        
    






    #token = "Token 0db412ef12f044d4062495f3ca26bf789b6f110f"
    token = "Token 1b3b686c7c061abe9649d3019b40c935764f3197"
    ndvi(token)
    client = boto3.client('lambda')
    response = client.invoke(
        InvocationType='Event',
        FunctionName='missDauCount2',
        Payload=json.dumps({"test": "test"})
    )  
    return res
            



