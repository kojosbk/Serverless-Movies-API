import azure.functions as func
import os
from azure.cosmos import CosmosClient, exceptions

endpoint = os.environ['COSMOS_ENDPOINT']
key = os.environ['COSMOS_KEY']
client = CosmosClient(endpoint, key)
database_name = 'MoviesDatabase'
container_name = 'MoviesContainer'
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        return func.HttpResponse(body=str(items), status_code=200)
    except exceptions.CosmosHttpResponseError as e:
        return func.HttpResponse("Error connecting to Cosmos DB: " + str(e), status_code=500)
