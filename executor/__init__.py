import azure.functions as func
from .. import storage_client
import asyncio
import json
import logging 
from copy import copy

async def get_compared_object(url, token):
    _, result = await storage_client.http_get_with_token(f'{url}/inputs.json', token)
    result.update({"source_url":url})
    return result

async def post_results(token, data):
    url = data.pop('source_url')
    data.update({"source_org_id": storage_client.storage_account})
    _, result = await storage_client.http_put_with_token(f'{url}/out/{storage_client.storage_account}.json',
                                                         json.dumps(data), token)

    return result


async def executor(req: func.HttpRequest):
    logging.info('Python HTTP trigger function processed a request.')
    

    token = await storage_client.get_storage_token()
    queue = await storage_client.get_queue(token)
    
    compared_objects = [await get_compared_object(item['storage_url'], token) for item in queue]
    objects = await storage_client.load_storage_objects(token)

    
    results = []
    for compared_object in compared_objects:
        was_compared = False
        for obj in objects:
            if compared_object.get('name') == obj.get('name'):
                obj.update({'source_url': compared_object.get('source_url')})  
                was_compared = True
                results.append(copy(obj))
        if was_compared == False:
            results.append({'source_url': compared_object.get('source_url')})
    
    await asyncio.gather(*[post_results(token, item) for item in results])
    
    await storage_client.erase_queue(token)

    resp = {
        "org_id": storage_client.storage_account,
        "items_processed": len(results)        
    }

    # return function result
    return func.HttpResponse(status_code=200, body=json.dumps(resp))

def main(req: func.HttpRequest) -> func.HttpResponse:
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(executor(req))