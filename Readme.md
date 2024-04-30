### Step 1: Set Up Your Development Environment

#### 1. Install Visual Studio Code:
   - Download and install VS Code from the [official Visual Studio Code website](https://code.visualstudio.com/).

#### 2. Install Python:
   - Ensure Python is installed on your system. You can download it from the [Python official website](https://www.python.org/downloads/).
   - After installation, you can verify the installation by opening a command prompt and typing:
     ```bash
     python --version
     ```
     This should display the Python version installed.

#### 3. Install Azure Functions Extension for Visual Studio Code:
   - Open Visual Studio Code.
   - Go to Extensions (sidebar) or press `Ctrl+Shift+X`.
   - Search for "Azure Functions" and click on the install button for the Azure Functions extension by Microsoft.

#### 4. Set Up Azure CLI:
   - Download and install the Azure CLI from the [Azure CLI official page](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).
   - Once installed, open a command prompt or terminal.
   - Log in to your Azure account by executing the following command:
     ```bash
     az login
     ```
   - This command will open a web page where you can enter your Azure credentials to authenticate.

#### 5. Confirm Azure Functions Core Tools:
   - Azure Functions Core Tools are needed for local development. Install them by running the following command in your command prompt:
     ```bash
     npm install -g azure-functions-core-tools@4 --unsafe-perm true
     ```
   - Ensure that you have Node.js installed to use npm (Node Package Manager). You can download it from [Node.js official website](https://nodejs.org/).

#### 6. Configure Python in VS Code:
   - Open VS Code.
   - Press `Ctrl+Shift+P` to open the command palette.
   - Type and select `Python: Select Interpreter`.
   - Choose the Python version you installed earlier.

#### 7. Additional Tools (Optional):
   - It's helpful to install Git for version control. You can download Git from [Git's official site](https://git-scm.com/downloads).
   - For managing Python packages, ensure that `pip` is installed (it usually comes with Python). Check by running `pip --version` in the command prompt.

This setup prepares your development environment to start creating the serverless movies API project using Azure and Python in Visual Studio Code on a Windows 10 system. Once you're ready, you can proceed to the next steps of project development, such as creating Azure resources and coding the functions.


### Step 2: Create Azure Resources

In this step, you'll set up the necessary Azure resources for your serverless movie API. These resources include a resource group, Azure Cosmos DB for your NoSQL database, and Azure Storage for storing movie cover images.

#### 1. Create a Resource Group:
A resource group in Azure is a container that holds related resources for an Azure solution. Here's how to create one via Azure CLI:

- Open your command prompt or terminal.
- Run the following command to create a resource group:
  ```bash
  az group create --name MoviesAPIResourceGroup --location eastus
  ```
  Replace `eastus` with the Azure region that is best suited for you.

#### 2. Create an Azure Cosmos DB Account:
Azure Cosmos DB is a globally distributed, multi-model database service. To create a Cosmos DB account with a SQL API (which is simple and effective for many applications), execute:

- In your command prompt or terminal, run:
  ```bash
  az cosmosdb create --name moviesapi-cosmosdb --resource-group MoviesAPIResourceGroup --kind GlobalDocumentDB --locations regionName=eastus failoverPriority=0 isZoneRedundant=False
  ```
  Adjust `regionName` and `eastus` if necessary to match your preferred location settings.

#### 3. Create a Database and Container in Cosmos DB:
After creating your Cosmos DB account, you need to create a database and a container (which acts like a table in relational databases).

- You can do this using the Azure portal for ease of use, or continue using the CLI.
- For CLI, run:
  ```bash
  az cosmosdb sql database create --account-name moviesapi-cosmosdb --resource-group MoviesAPIResourceGroup --name MoviesDatabase
  az cosmosdb sql container create --account-name moviesapi-cosmosdb --resource-group MoviesAPIResourceGroup --database-name MoviesDatabase --name MoviesContainer --partition-key-path "/partitionKey"
  ```
  Replace `"/partitionKey"` with the appropriate partition key based on your data. For simplicity, you might use something like `/releaseYear`.

#### 4. Create an Azure Storage Account:
You'll use Azure Storage to store the movie cover images.

- Create the storage account by running:
  ```bash
  az storage account create --name moviesapistorage --resource-group MoviesAPIResourceGroup --location eastus --sku Standard_LRS
  ```
  Replace `moviesapistorage` with a unique name as Azure storage account names need to be globally unique.

#### 5. Create a Blob Container:
Once the storage account is set up, create a blob container to hold your movie images.

- First, retrieve your storage account key by running:
  ```bash
  az storage account keys list --account-name moviesapistorage --resource-group MoviesAPIResourceGroup --query "[0].value" -o tsv
  ```
- With the key, create the blob container:
  ```bash
  az storage container create --name moviecovers --account-name moviesapistorage --account-key YourAccountKey
  ```
  Replace `YourAccountKey` with the key you retrieved.

This setup of Azure resources is crucial as it establishes the backbone of your serverless application infrastructure. In the next step, you'll start preparing and uploading your movie data and images to these resources, and then move on to developing your serverless functions.



### Step 3: Prepare Your Data

Now that your Azure resources are set up, the next step involves preparing and uploading your movie data and cover images to Azure Cosmos DB and Azure Storage, respectively.

#### 1. Prepare Movie Data:
You'll need to create a JSON dataset of movies. This data should be structured to fit into your Cosmos DB collection and must include fields like `title`, `releaseYear`, `genre`, and a placeholder for `coverUrl`.

- Create a JSON file (`movies.json`) with data formatted as follows:
  ```json
  [
      {
          "title": "Inception",
          "releaseYear": "2010",
          "genre": "Science Fiction, Action",
          "coverUrl": ""
      },
      {
          "title": "The Shawshank Redemption",
          "releaseYear": "1994",
          "genre": "Drama, Crime",
          "coverUrl": ""
      },
      {
          "title": "The Dark Knight",
          "releaseYear": "2008",
          "genre": "Action, Crime, Drama",
          "coverUrl": ""
      }
      // Add more movies as needed
  ]
  ```

#### 2. Upload Movie Data to Azure Cosmos DB:
You can use the Azure portal or Azure Cosmos DB data migration tool (dt.exe) for uploading. For simplicity, you might use the portal:

- Go to the Azure portal.
- Navigate to your Cosmos DB account > Data Explorer.
- Open the database and container you created.
- Use the "Upload Item" feature to import your `movies.json` file.

#### 3. Prepare and Upload Movie Cover Images:
Gather the cover images for each movie. Make sure each image is named in a way that it can be easily associated with the movie data, like using the movie title.

- Ensure images are in a supported format (e.g., jpg, png).
- Store these images in a folder.

#### 4. Upload Images to Azure Blob Storage:
You can use Azure Storage Explorer, a convenient GUI tool, or Azure CLI to upload the images to the blob container you created earlier.

- If using Azure CLI, navigate to the folder containing your images and use:
  ```bash
  az storage blob upload-batch --account-name moviesapistorage --destination moviecovers --source ./path-to-your-images
  ```
  Replace `./path-to-your-images` with the path to your images folder.

#### 5. Update Movie Data with Cover URLs:
After uploading the images, you need to update your movie data in Cosmos DB with the appropriate `coverUrl` that points to the blob storage URLs.

- Access each blob in the Azure portal or use Azure Storage Explorer to copy the URL.
- Update each movie entry in Cosmos DB with the URL in the `coverUrl` field.

This step involves a mix of manual and automated tasks to ensure that your data is correctly formatted, uploaded, and linked between your Azure Cosmos DB and Azure Storage accounts. With your data and images set up, you'll next develop the Azure Functions that will serve as the backend for your Serverless Movies API.


To create and manage Azure Functions directly from the command line (CLI), you can use the Azure Functions Core Tools and Azure CLI. This approach allows you to handle everything without needing the Visual Studio Code interface. Here’s how you can do it:

### Step 4: Develop Serverless Functions using CLI

#### 1. Install Azure Functions Core Tools:
If not already installed, you can install the Azure Functions Core Tools globally using npm (Node Package Manager). Ensure Node.js is installed before proceeding.

```bash
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

#### 2. Create an Azure Functions App:
Navigate to the folder where you want to create your function app and run:

```bash
func init MoviesAPI --python
```

This command initializes a new Azure Functions project named `MoviesAPI` with Python as the programming language.

#### 3. Create Function: GetMovies
Create your first HTTP-triggered function, `GetMovies`, which will handle fetching movies from the database.

```bash
cd MoviesAPI
func new --name GetMovies --template "HTTP trigger" --authlevel anonymous
```

This sets up a new function with HTTP trigger and no authorization required for simplicity.

#### 4. Implement the Function:
rename the function_app.py file to '__init__.py' Edit the `GetMovies/__init__.py` file to include the code that connects to Cosmos DB and fetches movie data. Here is a basic implementation example:

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
The error message you're seeing, `KeyError: 'COSMOS_ENDPOINT'`, indicates that the Azure Functions environment does not have access to the environment variable `COSMOS_ENDPOINT`. This problem typically occurs because the environment variables are not set in the local settings file of your Azure Functions project or are not accessible by your function app.

To resolve this, you'll need to ensure that all required environment variables are correctly defined in your `local.settings.json` file, which is used for local development. Here’s how to set this up:

### Define Environment Variables in `local.settings.json`

Navigate to the root of your Azure Functions project and locate the `local.settings.json` file. This file should include configuration settings that are used when running your functions locally. Here's how you can structure the file with your Cosmos DB credentials:

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

- Replace `<YOUR_STORAGE_CONNECTION_STRING>` with the connection string to your Azure Storage account. This is necessary for internal use by Azure Functions.
- Replace `<YOUR_COSMOS_DB_ENDPOINT>` and `<YOUR_COSMOS_DB_KEY>` with your actual Azure Cosmos DB endpoint URL and key.

The error message `Could not find top-level function app instances in function_app.py` suggests that the Functions runtime is not finding any Azure Functions in the specified Python file.

Based on the verbose output, it seems like the Functions runtime is trying to locate the functions in `function_app.py`. However, the provided `__init__.py` file code looks like it should be within a function folder. Usually, each Azure Function you define would be in its own subfolder with its own `__init__.py`, `function.json`, and any other necessary files.

Here's how a typical Azure Functions Python project structure should look like:

```
Serverless-Movies-API/
│   host.json
│   local.settings.json
│   requirements.txt
│
└───MoviesAPI/
    └───GetMovies/   # This is the function name
        │   __init__.py
        │   function.json
        │   ...
    └───AnotherFunction/
        │   __init__.py
        │   function.json
        │   ...
```

In `GetMovies/__init__.py`, you would have your Python function code as you provided:

```python
import azure.functions as func
import os
from azure.cosmos import CosmosClient, exceptions

# ... (rest of your code)

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Function implementation
```

And `GetMovies/function.json` would define the trigger and bindings for that function:

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

**Here’s what you should do to resolve the issue:**

1. **Check the Structure**: Ensure your Azure Function app follows the correct project structure, as shown above. Each function should be in its own subdirectory with its `__init__.py` and `function.json`.

2. **Verify `function.json`**: Each function directory should contain a `function.json` that correctly defines the bindings.

3. **Ensure Function Discovery**: The Functions runtime discovers functions based on the presence of these `function.json` files. If they are not present or not correctly formatted, the function won't be discovered.

4. **Ensure Correct Filenames**: The function entry point should be named `__init__.py` within its respective function folder.

5. **Function App Name**: The folder name in the project (`MoviesAPI` in your case) does not directly relate to how functions are discovered. Instead, the runtime looks at subfolders that contain a `function.json`.

6. **Local Settings**: Ensure that your `local.settings.json` has the correct values for all required environment variables and connection strings.

After making the necessary adjustments, try running `func start --verbose` again. If the functions are set up correctly, the runtime should find and index them, and the output will indicate that functions are loaded and available.

### Step 2: Restart Azure Functions

After updating `local.settings.json`, restart your Azure Functions runtime:

- Close the current terminal or command prompt session.
- Open a new terminal or command prompt session.
- Navigate to your Azure Functions project directory.
- Start the function app again using the command:
  ```bash
  func start
  ```

### Step 3: Verify Functionality

Once restarted, Azure Functions should now be able to pick up the environment variables from `local.settings.json` and not throw the `KeyError`. Verify by checking the console output to ensure no errors are being thrown related to missing environment variables.

### Additional Tips

- **Ensure Correct Paths**: Make sure that the file paths and references in your project are correct. File path issues can sometimes cause environment variables not to load properly.
- **Use Secure Practices**: For production environments, you'll need to use secure methods to manage these keys and secrets, such as Azure Key Vault.
- **Debugging**: If further issues arise, consider adding print statements before the error points to log the environment variables and ensure they are being loaded correctly.

This setup should address the `KeyError` by ensuring all necessary configurations are available to your Azure Functions environment.
#### 5. Local Testing:
Run the function locally to test its functionality.

```bash
func start
```

Use a tool like Postman or curl to send requests to the local server and verify responses.

#### 6. Deploy Functions to Azure:
First, log in to Azure if not already logged in.

```bash
az login
```

Deploy your function app to Azure.

```bash
func azure functionapp publish [FunctionAppName]
```
Replace `[FunctionAppName]` with the name of the function app you wish to deploy. This command deploys your code to Azure Functions.

By following these steps, you can fully manage your Azure Functions development process through the command line, providing a flexible and scriptable approach to deploying serverless applications.