import logging
import os
import json
import requests
import azure.functions as func
from azure.cosmos import CosmosClient

# Retrieve environment variables
cosmos_endpoint = os.getenv('COSMOS_ENDPOINT')
cosmos_key = os.getenv('COSMOS_KEY')
cosmos_database_id = os.getenv('COSMOS_DATABASE_ID')
cosmos_container_id = os.getenv('COSMOS_CONTAINER_ID')
mistral_api_key = os.getenv('mistral_api_key')

# Initialize Cosmos client
client = CosmosClient(cosmos_endpoint, cosmos_key)

# Access the database and container
database = client.get_database_client(cosmos_database_id)
container = database.get_container_client(cosmos_container_id)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Extract the movie title from the route parameters
    movie_title = req.route_params.get('title')
    if not movie_title:
        return func.HttpResponse("Please provide a movie title.", status_code=400)

    # Query the Cosmos DB for the specified movie title
    query = f"SELECT * FROM c WHERE c.title = @title"
    parameters = [{"name": "@title", "value": movie_title}]
    movie_data = list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))

    if not movie_data:
        return func.HttpResponse(f"No movie found with the title: {movie_title}", status_code=404)

    # Extract movie information for the prompt
    movie_info = movie_data[0]
    user_prompt = (
        f"Write a concise summary for the movie '{movie_info['title']}', "
        # f"released in {movie_info['releaseYear']}, with the genre {movie_info['genre']}, "
        f"in no more than 3-4 sentences."
    )

    # Prepare the request to the Mistral API
    mistral_url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {mistral_api_key}"
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": user_prompt}],
        "temperature": 0.7,
        "top_p": 1,
        "max_tokens": 200,
        "stream": False,
        "safe_prompt": False
    }

    # Make the request to generate the summary
    try:
        response = requests.post(mistral_url, headers=headers, json=payload)
        response_data = response.json()

        # Extract the summary content and replace newline characters with HTML <br> tags
        summary = response_data['choices'][0]['message']['content']
        formatted_summary = summary.replace('\n', '<br>')

        # Add the generated summary to the movie information
        movie_info['generatedSummary'] = formatted_summary

        # Construct the final output with the correct format
        final_output = [{
            "title": movie_info["title"],
            "releaseYear": movie_info["releaseYear"],
            "genre": movie_info["genre"],
            "coverUrl": movie_info["coverUrl"],
            "generatedSummary": formatted_summary
        }]

        # Return the formatted movie data as JSON
        return func.HttpResponse(json.dumps(final_output, indent=4), mimetype="application/json")

    except Exception as e:
        logging.error(f"Error calling Mistral API: {str(e)}")
        return func.HttpResponse("Error generating movie summary.", status_code=500)
