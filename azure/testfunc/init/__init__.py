import logging
import urllib
import azure.functions as func

"""{
urls:[url1, url2, url3]
entity_id: "uuid4"
org_id: "testorg"
}"""

def getParam(paramName: str, req: func.HttpRequest):
    param = req.params.get(paramName)
    if not param:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            param = req_body.get(paramName)
    return param

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # getting request params
    urls = getParam("urls", req)
    entity_id = getParam("entity_id", req)
    org_id = getParam("org_id", req)

    # creating in&out in storage

    # preparing data from storage

    # invokation of the queuers
    for current in urls:
        urllib.request.urlopen(current)

    # return function result
    return func.HttpResponse("done")
