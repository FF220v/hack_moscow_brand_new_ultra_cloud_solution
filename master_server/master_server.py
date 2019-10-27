from flask import Flask, request, Response
import requests
import json
import asyncio
from aiohttp import ClientSession
import logging
from sys import stdout

logger = logging.getLogger("Master Server")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("logs.txt")
sh = logging.StreamHandler(stream=stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
sh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)

async def http_post(url, data=None, headers=None, params=None):
    async with ClientSession() as session:
        result = await session.post(url, data=data, headers=headers, params=params)
        resp_data = await result.text()
        try:
            resp_data = json.loads(resp_data)
        except Exception:
            pass
        return result.status, resp_data


MAX_QUEUE_SIZE = 5

app = Flask(__name__)

org_init_func_endpoints_dict = {
    'testorg1':'https://init1.azurewebsites.net/api/init?code=bwC1lIOwBM0eumtEUSIqChf2EJeLlR3q1m91DOvVcWjaeqPaYuySZg==',
    'testorg2':'https://init2.azurewebsites.net/api/init?code=cKY5Csq5cOpZVHSj0v8U/2Sx3NjtW9gMFCVdvT6ot9zTPxRHnIBXBQ==',
    'testorg3':'https://init3.azurewebsites.net/api/init?code=n2Q53AK2PuY7uIcx883ecqKStNF9QTL/JR7fbtu2gW7R3ZMaWQvT/g==',
    'testorg4':'https://init4.azurewebsites.net/api/init?code=upW2sP3Im3iouTgz6X4DcVPP5366LcO9m6JllyTvRm1ZMa1Yx0yx8g==',
    'testorg5':'https://init5.azurewebsites.net/api/init?code=r9vv9e5RVGwmXSaExhfJEkaEQjH2Jiy2tJpUyKQLmsKpGLbWa/EXmA=='
}

org_queue_func_endpoints_dict = {
    'testorg1':'https://init1.azurewebsites.net/api/queuer?code=wscBOoygQHMiTmHi0CuG05itGe051VEuHRI1x4SrqFWZEwzEg/LL1w==',
    'testorg2':'https://init2.azurewebsites.net/api/queuer?code=HwR7L0xMAyP3mbkMVihYUR338OU0x8y7hurj4jcusuGsui6rIgJ3qg==',
    'testorg3':'https://init3.azurewebsites.net/api/queuer?code=MAgVOhguqwjBoKj66/ft4RFK4sHe4wn8D6RY8vP6UZkvAOyKAFXC3Q==',
    'testorg4':'https://init4.azurewebsites.net/api/queuer?code=J4z92ac4AX8FWEJgGCaGpXSarRYvJhnQttFfsXwuzLvbNa44FzvKlA==',
    'testorg5':'https://init5.azurewebsites.net/api/queuer?code=XYHkB2IooWpOYECv75Sfq4DvSMERUYohymaPyx1ha3jyaF6ibBl2Ng=='
}


org_exec_func_endpoints_dict = {
    'testorg1':'https://init1.azurewebsites.net/api/exec?code=A0ZaV7JIXOyNaFgBEcaG1S0zgtjCOTnM5CqjYETw16h4cTh7a6o2Fg==',
    'testorg2':'https://init2.azurewebsites.net/api/exec?code=HwR7L0xMAyP3mbkMVihYUR338OU0x8y7hurj4jcusuGsui6rIgJ3qg==',
    'testorg3':'https://init3.azurewebsites.net/api/exec?code=8n81RrQOlctpkL4javkka1WfZpaFvHOnnv2kTAYItRPGiIbbZaQPSg==',
    'testorg4':'https://init4.azurewebsites.net/api/exec?code=CqzaYiuVwlaR/f8mJAXACtXH8OVC2VMYQ7giDaln97Tzrua1kOZMOQ==',
    'testorg5':'https://init5.azurewebsites.net/api/exec?code=kH5/kfaZFQ4rIJK8Bhy2aMkpwqZOqTuaBIMJoWAgOmJKvZT6suAjbA=='
}


def get_init_url_by_org_id(org_id):
    return org_init_func_endpoints_dict.get(org_id)

def start_init(context):
    org_id = context['org_id']
    queue_urls = [url for key, url in org_queue_func_endpoints_dict.items()
                  if key != org_id]
    payload = {
        'org_id': org_id,
        'urls': queue_urls,
        'entity_id': context['entity_id']
    }
    return requests.post(get_init_url_by_org_id(org_id), json=payload)


async def invoke_org_exec(org_id):
    return await http_post(org_exec_func_endpoints_dict[org_id])

async def invoke_executors(orgs_to_invoke):
    return await asyncio.gather(*[invoke_org_exec(org_id) for org_id in orgs_to_invoke])


@app.route('/process', methods=['POST'])
def process():
    context = request.get_json()
    logger.info(f'Incoming request with context: {context}')
    queues = start_init(context)
    queues = json.loads(queues.text).get('responses')
    logger.info(f'Tasks put to queues: {queues}')
    orgs_to_invoke = [r[1]['org_id'] for r in queues if r[1]['queue_size']>=MAX_QUEUE_SIZE]
    logger.info(f'Following orgs are being prepared for start: {orgs_to_invoke}')
    loop = asyncio.new_event_loop()
    executors = loop.run_until_complete(invoke_executors(orgs_to_invoke))
    logger.info(f'Following executors finished work: {executors}')
    return {"queues":queues, "executors":executors}
    

if __name__ == "__main__":
    logger.info("Starting master server...")
    app.run(host='0.0.0.0', port=8080)