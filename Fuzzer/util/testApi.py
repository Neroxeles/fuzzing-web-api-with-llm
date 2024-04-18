from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

configuration = swagger_client.Configuration()
configuration.host = 'http://localhost:3002'

def api_sale_get():
	api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
	try:
		api_response = api_instance.sale_get()
		pprint(api_response)
	except ApiException as e:
		print("Exception when calling DefaultApi->sale_get: %s\n" % e)

def api_sale_order_item_delete(item: int):
	api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
	# item = 56 # int | The item in the list that should be deleted # removed
	try:
		api_instance.sale_order_item_delete(item)
	except ApiException as e:
		print("Exception when calling DefaultApi->sale_order_item_delete: %s\n" % e)

def api_sale_order_item_put(item: int, product_id: any, amount: any):
	api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
	body = swagger_client.OrderItemBody(product_id=product_id, amount=amount) # OrderItemBody | none
	# item = 56 # int | The item in the list that should be deleted # removed
	try:
		api_response = api_instance.sale_order_item_put(body, item)
		pprint(api_response)
	except ApiException as e:
		print("Exception when calling DefaultApi->sale_order_item_put: %s\n" % e)

def api_sale_order_post(product_id: any, amount: any):
	api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
	body = swagger_client.SaleOrderBody(product_id=product_id, amount=amount) # SaleOrderBody | none
	try:
		api_response = api_instance.sale_order_post(body)
		pprint(api_response)
	except ApiException as e:
		print("Exception when calling DefaultApi->sale_order_post: %s\n" % e)

def api_users_get():
	api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
	try:
		api_response = api_instance.users_get()
		pprint(api_response)
	except ApiException as e:
		print("Exception when calling DefaultApi->users_get: %s\n" % e)

def api_users_put(name: str):
	api_instance = swagger_client.DefaultApi(swagger_client.ApiClient(configuration))
	body = swagger_client.UsersBody(name=name) # UsersBody | none
	try:
		api_response = api_instance.users_put(body)
		pprint(api_response)
	except ApiException as e:
		print("Exception when calling DefaultApi->users_put: %s\n" % e)