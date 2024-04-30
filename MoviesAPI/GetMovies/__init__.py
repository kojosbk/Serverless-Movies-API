import azure.functions as func
import os
import json
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
        # Query that selects only the necessary attributes
        query = "SELECT c.title, c.releaseYear, c.genre, c.coverUrl FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        # Prepare the result to include only the specified fields
        result = [
            {"title": item["title"], "releaseYear": item["releaseYear"],
             "genre": item["genre"], "coverUrl": item["coverUrl"]}
            for item in items
        ]

        # Convert the result to JSON string
        json_result = json.dumps(result, indent=4)  # Pretty print the JSON for readability

        return func.HttpResponse(body=json_result, status_code=200, headers={"Content-Type": "application/json"})
    except exceptions.CosmosHttpResponseError as e:
        return func.HttpResponse("Error connecting to Cosmos DB: " + str(e), status_code=500)
