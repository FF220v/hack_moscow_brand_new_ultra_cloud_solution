import azure.functions as func
from .. import storage_client
import requests
from aiohttp import ClientSession
import asyncio
import json
import logging 
from bs4 import BeautifulSoup
import datetime
       

"""{
urls:[url1, url2, url3]
entity_id: "uuid4"
org_id: "testorg"
}"""

async def executor(req: func.HttpRequest):
    logging.info('Python HTTP trigger function processed a request.')
    
    content = req.get_json()

    # getting request params
    urls = content.get("urls")
    entity_id = content.get("entity_id")
    org_id = content.get("org_id")

    # creating in&out in storage
    token = await storage_client.get_storage_token()
    temp_storage_url = await storage_client.create_temp_storage(token, entity_id)

    payload = {
        'org_id': org_id,
        'storage_url': temp_storage_url
    }

    # invokation of the queuers
    responses = await asyncio.gather(*[storage_client.http_post(url=url, data=json.dumps(payload)) for url in urls])
    resp = {
        "responses":[r for r in responses] 
    }
    # return function result
    return func.HttpResponse(status_code=200, body=json.dumps(resp))

def main(req: func.HttpRequest) -> func.HttpResponse:
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(executor(req))
