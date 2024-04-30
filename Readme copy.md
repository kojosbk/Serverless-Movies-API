
**Step 1: Set Up Your Development Environment**

1. **Install Visual Studio Code**:
   - Download and install VS Code from the official Visual Studio Code website.

2. **Install Python**:
   - Ensure Python is installed on your system. You can download it from the Python official website.
   - After installation, verify by opening a command prompt and typing:
     ```
     python --version
     ```
     This should display the Python version installed.

3. **Install Azure Functions Extension for Visual Studio Code**:
   - Open Visual Studio Code.
   - Go to Extensions (sidebar) or press `Ctrl+Shift+X`.
   - Search for "Azure Functions" and click on the install button for the Azure Functions extension by Microsoft.

4. **Set Up Azure CLI**:
   - Download and install the Azure CLI from the Azure CLI official page.
   - Once installed, open a command prompt or terminal.
   - Log in to your Azure account by executing:
     ```
     az login
     ```
     This command will open a web page where you can enter your Azure credentials to authenticate.

5. **Confirm Azure Functions Core Tools**:
   - Azure Functions Core Tools are needed for local development. Install them by running:
     ```
     npm install -g azure-functions-core-tools@4 --unsafe-perm true
     ```
   - Ensure that you have Node.js installed to use npm (Node Package Manager). You can download it from Node.js official website.

6. **Configure Python in VS Code**:
   - Open VS Code.
   - Press `Ctrl+Shift+P` to open the command palette.
   - Type and select `Python: Select Interpreter`.
   - Choose the Python version you installed earlier.

7. **Additional Tools (Optional)**:
   - It's helpful to install Git for version control. You can download Git from Git's official site.
   - For managing Python packages, ensure that pip is installed (it usually comes with Python). Check by running `pip --version` in the command prompt.

This setup prepares your development environment to start creating the serverless movies API project using Azure and Python in Visual Studio Code on a Windows 10 system. Once you're ready, proceed to the next steps of project development, such as creating Azure resources and coding the functions.

**Step 2: Create Azure Resources**

1. **Create a Resource Group**:
   - Open your command prompt or terminal.
   - Run the following command to create a resource group:
     ```
     az group create --name <ResourceGroupName> --location <Region>
     ```
   - Replace `<ResourceGroupName>` with your desired name and `<Region>` with the Azure region that is best suited for you.

2. **Create an Azure Cosmos DB Account**:
   - In your command prompt or terminal, run:
     ```
     az cosmosdb create --name <CosmosDBName> --resource-group <ResourceGroupName> --kind GlobalDocumentDB --locations regionName=<Region> failoverPriority=0 isZoneRedundant=False
     ```
   - Adjust `<CosmosDBName>`, `<ResourceGroupName>`, and `<Region>` as necessary.

3. **Create a Database and Container in Cosmos DB**:
   - For CLI, run:
     ```
     az cosmosdb sql database create --account-name <CosmosDBName> --resource-group <ResourceGroupName> --name <DatabaseName>
     az cosmosdb sql container create --account-name <CosmosDBName> --resource-group <ResourceGroupName> --database-name <DatabaseName> --name <ContainerName> --partition-key-path "/partitionKey"
     ```
   - Replace `/partitionKey` with the appropriate partition key based on your data.

4. **Create an Azure Storage Account**:
   - Create the storage account by running:
     ```
     az storage account create --name <StorageAccountName> --resource-group <ResourceGroupName> --location <Region> --sku Standard_LRS
     ```
   - Replace `<StorageAccountName>` with a unique name as Azure storage account names need to be globally unique.

5. **Create a Blob Container**:
   - First, retrieve your storage account key by running:
     ```
     az storage account keys list --account-name <StorageAccountName> --resource-group <ResourceGroupName> --query "[0].value" -o tsv
     ```
   - With the key, create the blob container:
     ```
     az storage container create --name moviecovers --account-name <StorageAccountName> --account-key <YourAccountKey>
     ```
   - Replace `<YourAccountKey>` with the key you retrieved.

This setup of Azure resources is crucial as it establishes the backbone of your serverless application infrastructure. In the next step, you'll start preparing and uploading your movie data and images to these resources, and then move on to developing your serverless functions.

**Step 3: Prepare Your Data

**

1. **Prepare Movie Data**:
   - Create a JSON dataset of movies structured to fit into your Cosmos DB collection, including fields like title, releaseYear, genre, and a placeholder for coverUrl.
   - Example JSON structure:
     ```json
     [
         {
             "title": "Inception",
             "releaseYear": "2010",
             "genre": "Science Fiction, Action",
             "coverUrl": "<Placeholder for cover URL>"
         },
         {
             "title": "The Shawshank Redemption",
             "releaseYear": "1994",
             "genre": "Drama, Crime",
             "coverUrl": "<Placeholder for cover URL>"
         }
     ]
     ```
   - Add more movies as needed.

2. **Upload Movie Data to Azure Cosmos DB**:
   - Use the Azure portal or a data migration tool to import your `movies.json` file into the Cosmos DB container you created.

3. **Prepare and Upload Movie Cover Images**:
   - Gather cover images for each movie, ensuring each image is named to easily associate with the movie data.
   - Ensure images are in a supported format (e.g., jpg, png).

4. **Upload Images to Azure Blob Storage**:
   - Navigate to the folder containing your images and use:
     ```
     az storage blob upload-batch --account-name <StorageAccountName> --destination moviecovers --source <path-to-your-images>
     ```
   - Replace `<path-to-your-images>` with the path to your images folder.

5. **Update Movie Data with Cover URLs**:
   - After uploading the images, update your movie data in Cosmos DB with the appropriate coverUrl that points to the blob storage URLs.

**Step 4: Develop Serverless Functions using CLI**

1. **Install Azure Functions Core Tools**:
   - Install the Azure Functions Core Tools globally using npm, ensuring Node.js is installed first:
     ```
     npm install -g azure-functions-core-tools@4 --unsafe-perm true
     ```

2. **Create an Azure Functions App**:
   - Navigate to the folder where you want to create your function app and run:
     ```
     func init <FunctionAppName> --python
     ```
   - This command initializes a new Azure Functions project with Python as the programming language. Replace `<FunctionAppName>` with your desired name.

3. **Create Function: GetMovies**:
   - Create your HTTP-triggered function, GetMovies, to handle fetching movies from the database:
     ```
     cd <FunctionAppName>
     func new --name GetMovies --template "HTTP trigger" --authlevel anonymous
     ``

4. **Implement the Function**:
   - Rename the `function_app.py` file to `init.py` and edit the `GetMovies/__init__.py` file to include the code that connects to Cosmos DB and fetches movie data.
   - Basic implementation example provided in the original text.

After these steps, continue with local testing, deployment, and management using the Azure CLI as detailed in the provided steps.

Continuing from the setup of your Azure Functions app, here’s how to properly structure your project directory and ensure the content of each file is set correctly before running `func start`.

**Project Folder Structure**

Your Azure Functions project should be structured as follows to ensure proper discovery and execution of your functions:

```
Serverless-Movies-API/
│   host.json
│   local.settings.json
│   requirements.txt
│
└───MoviesAPI/                    # Azure Functions Project Root
    └───GetMovies/               # Function Folder
        │   __init__.py          # Function Code
        │   function.json        # Function Configuration
        │   sample.dat           # Optional: Additional data files
    └───AnotherFunction/         # Additional Functions
        │   __init__.py
        │   function.json
```

**Files Content**

1. **host.json**: This file configures the function app, including versioning and extension bundles. Here's a typical example:

```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

2. **local.settings.json**: Contains all local settings, including environment variables and connection strings used during development. It should look something like this:

```json
{
    "IsEncrypted": false,
    "Values": {
        "AzureWebJobsStorage": "<YOUR_STORAGE_CONNECTION_STRING>",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "COSMOS_ENDPOINT": "<YOUR_COSMOS_DB_ENDPOINT>",
        "COSMOS_KEY": "<YOUR_COSMOS_DB_KEY>"
    }
}
```
Replace placeholders with actual connection strings and keys.

3. **requirements.txt**: Lists all Python packages required for your functions. For example:

```
azure-functions
azure-cosmos
```

4. **Function Folder (`GetMovies/__init__.py`)**: This Python file contains the code that will be executed when the function is triggered. Here’s an example of what it might look like:

```python
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
```

5. **Function Configuration (`GetMovies/function.json`)**: Defines the triggers, bindings, and other configuration settings. A simple HTTP trigger might look like this:

```json
{
    "scriptFile": "__init__.py",
    "bindings": [
      {
        "authLevel": "anonymous",
        "type": "httpTrigger",
        "direction": "in",
        "name": "req",
        "methods": ["get"]
      },
      {
        "type": "http",
        "direction": "out",
        "name": "$return"
      }
    ]
  }
```

**Setting Up and Running**

Before running `func start`, ensure the following:

- Your local.settings.json is properly configured with all necessary connection strings and environment variables.
- Your Python environment has all dependencies installed listed in `requirements.txt`. You can install these using pip:

  ```bash
  pip install -r requirements.txt
  ```

- The folder structure is correctly set up with each function in its own subdirectory.

Once everything is set up:

1. **Navigate to the Azure Functions project directory** (`Serverless-Movies-API/MoviesAPI/`).
2. **Run the command**:

   ```
   func start
   ```

This will start the Azure Functions runtime and serve your functions locally. Check the console output to ensure no errors are thrown and that your functions are successfully loaded and available.

With your functions running, you can now use a tool like Postman or curl to send requests to the endpoints provided by your functions and verify that they respond as expected.
