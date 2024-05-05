import azure.functions as func
import os
import json
from azure.cosmos import CosmosClient, exceptions

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Retrieve the year from the URL path
    year = req.route_params.get('year')

    if not year:
        return func.HttpResponse("Year must be specified in the URL path, e.g., /getmoviesbyyear/2010", status_code=400)

    endpoint = os.environ['COSMOS_ENDPOINT']
    key = os.environ['COSMOS_KEY']
    client = CosmosClient(endpoint, key)
    database_name = 'MoviesDatabase'
    container_name = 'MoviesContainer'
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    try:
        query = "SELECT c.title, c.releaseYear, c.genre, c.coverUrl FROM c WHERE c.releaseYear = @year"
        parameters = [{'name': '@year', 'value': year}]

        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))

        result = [item for item in items]
        return func.HttpResponse(body=json.dumps(result, indent=4), status_code=200, headers={"Content-Type": "application/json"})
    except exceptions.CosmosHttpResponseError as e:
        return func.HttpResponse("Error connecting to Cosmos DB: " + str(e), status_code=500)
