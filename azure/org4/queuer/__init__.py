import azure.functions as func
from .. import storage_client
import asyncio
import json
import logging 

async def executor(req: func.HttpRequest):
    logging.info('Python HTTP trigger function processed a request.')
    
    content = req.get_json()

    # getting request params
    storage_url = content.get("storage_url")
    org_id = content.get("org_id")
    
    payload = {
        "storage_url":storage_url,
        "org_id":org_id
    }
    
    token = await storage_client.get_storage_token()
    queue = await storage_client.update_queue(token, payload)

    resp = {
        "org_id": storage_client.storage_account,
        "queue_size": len(queue)
    }

    # return function result
    return func.HttpResponse(status_code=200, body=json.dumps(resp))

def main(req: func.HttpRequest) -> func.HttpResponse:
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(executor(req))
