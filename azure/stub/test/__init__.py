import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
	import os
	a=str(os.getcwd())
	b=str(os.listdir('.'))
	return func.HttpResponse(f'{a}, {b}',status_code=200)