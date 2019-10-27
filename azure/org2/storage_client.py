from aiohttp import ClientSession
import asyncio
import json
import logging 
from bs4 import BeautifulSoup
import datetime

# Authorization things
token_url = 'https://login.microsoftonline.com/common/oauth2/token'
ps_client_id = '04b07795-8ddb-461a-bbee-02f9e1bf7b46'

### Hardcoded stuff ###
username = 'admin@futuregadgetslab.onmicrosoft.com'
password = 'San987873'
#######################

storage_account = 'testorg2'

container_url = f'https://{storage_account}.blob.core.windows.net/genx'

def get_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


async def http_get(url, headers=None, params=None):
    async with ClientSession() as session:
        result = await session.get(url, headers=headers, params=params)
        data = await result.text()
        try:
            data = json.loads(data)
        except Exception:
            logging.info('Cannot convert data to json. Returning raw text')
        return result.status, data


async def http_post(url, data=None, headers=None, params=None):
    async with ClientSession() as session:
        result = await session.post(url, data=data, headers=headers, params=params)
        resp_data = await result.text()
        try:
            resp_data = json.loads(resp_data)
        except Exception:
            logging.info('Cannot convert data to json. Returning raw text')
        return result.status, resp_data


async def http_put(url, data=None, headers=None, params=None):
    async with ClientSession() as session:
        result = await session.put(url, data=data, headers=headers, params=params)
        resp_data = await result.text()
        try:
            resp_data = json.loads(resp_data)
        except Exception:
            logging.info('Cannot convert data to json. Returning raw text')
        return result.status, resp_data


def http_get_with_token(url, token, params=None):
    return http_get(url,
                    headers={'x-ms-version':'2018-03-28',
                            'Authorization': token},
                    params=params)


async def http_post_with_token(url, data, token, params=None):
    return await http_post(url,
                           data=data,
                           headers={'x-ms-version':'2018-03-28',
                                    'Authorization': token},
                           params=params)


async def http_put_with_token(url, data, token, params=None):
    return await http_put(url,
                           data=data,
                           headers={'x-ms-version':'2018-03-28',
                                    'Authorization': token,
                                    'x-ms-blob-type': 'BlockBlob'},
                           params=params)


async def get_storage_token():
    status, result = await http_post(token_url,
                                     data={'username': username,
                                           'password': password,
                                           'client_id': ps_client_id,
                                           'grant_type': 'password',
                                           'resource': 'https://storage.azure.com'}
                                    )
    if status != 200:
        logging.error(f'Cannot acquire token: {status}, {result}')
        raise Exception()
    return ' '.join(["Bearer", result['access_token']])  


async def get_storage_paths(token):
    _, result = await http_get_with_token(f'{container_url}/?restype=container&comp=list',
                                          token)
    soup = BeautifulSoup(result, "lxml-xml")
    entities = soup.find_all(name='Name')
    paths = []
    for entity in entities:
        path = str(entity.string)
        if path.startswith('storage'):
            paths.append(path)
    return paths


async def get_queue(token):
    _, result = await http_get_with_token(f'{container_url}/queue.json',
                                          token)
    return result


async def update_queue(token, data):
    queue = await get_queue(token)
    queue.append(data)
    _, result = await http_put_with_token(f'{container_url}/queue.json',
                                          json.dumps(queue),
                                          token)
    return queue


async def erase_queue(token):
    _, result = await http_put_with_token(f'{container_url}/queue.json',
                                          json.dumps([]),
                                          token)
    return result


async def get_tasks(token):
    _, result = await http_get_with_token(f'{container_url}/tasks.json',
                                          token)
    return result


async def post_tasks(token, data):
    _, result = await http_put_with_token(f'{container_url}/tasks.json',
                                          json.dumps(data),
                                          token)
    return result


async def get_part(part_path, token):
    _, result = await http_get_with_token(f'{container_url}/{part_path}',
                                          token)
    return result


async def get_part_by_id(token, entity_id):
    _, result = await http_get_with_token(f'{container_url}/storage/{entity_id}.json',
                                          token)
    return result


async def create_temp_storage(token, entity_id):
    timestamp = get_timestamp()
    data = await get_part_by_id(token, entity_id)
    storage_url = f'{container_url}/temp/{timestamp}'
    _, result = await http_put_with_token(f'{storage_url}/inputs.json', json.dumps(data), token)
    return storage_url    


async def load_storage_objects(token):
    paths = await get_storage_paths(token)
    return await asyncio.gather(*[get_part(path, token) for path in paths])
       

async def main():
    token = await get_storage_token()
    print(await update_queue(token,{"data":"data"}))
    print(await get_queue(token))

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
