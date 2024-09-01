# shapefile-infrastructures

### Process Diagram:
![DRIVE](Process.jpg)


## 1. Setting Up and Running the Microservice Locally

1.1. Clone the repository.

```shell
git clone https://github.com/dilruksha1994/shapefile-infrastructures.git
cd shapefile-infrastructures/fastapi-microservice

```

1.2. Create a conda virtual environment and activate it.

```shell
conda create -n shapefileenv python=3.8 -y
conda activate shapefileenv
```

1.3. Install the dependencies.

```shell
pip install -r requirements.txt
```

1.4. Run the FastAPI application on localhost.

```shell
uvicorn main:app --reload 
```

1.5. POST method to process the sharefile. Please refer this link (`http://127.0.0.1:8000/docs/`) to see the API documentstion.

```shell
http://127.0.0.1:8000/process-shapefile/
```


## 2. Deploying the Microservice on Azure

* Step 1: Log in to the Azure portal.
* Step 2: Create a new Azure App Service instance.
* Step 3: Deploy the FastAPI microservice using GitHub Actions.
* Step 4: Test the deployed microservice by sending a POST request to the Azure App Service URL.
```shell
https://as-shapefile-sasia.azurewebsites.net/process-shapefile/
```
* Step 5: Verify the deployment and monitor logs using the Azure App Service dashboard.


## 3. Packaging the Microservice as a Python Wheel

3.1. Navigate to the directory containing the FastAPI microservice

```shell
cd fastapi-microservice
```

3.2. Package the microservice as a Python Wheel

```shell
python setup.py bdist_wheel
```

3.3. Activate the API key for PYPI.

```shell
$env:TWINE_PASSWORD="api-key"
```

3.4. Upload the wheel file to PyPI

```shell
twine upload dist/*
```

## 4. Creating and Configuring the Databricks Notebook

* Step 1: Go to the Databricks workspace in the Azure portal.
* Step 2: Create a cluster with multi-node. (Note: This is must when accessing through Data Factory) 
* Step 3: Install the required packages, including the Python wheel for the microservice.
```shell
pip install shapefile-processor
```
* Step 4: Create a new notebook in Databricks.


## 5. Setting Up the Azure Data Factory Pipeline

* Step 1: Open Azure Data Factory and create a new pipeline.
* Step 2: Add the "Execute Databricks Notebook" activity to the pipeline.
* Step 3: Configure the linked service to the Databricks workspace.
* Step 4: Specify the path to the Databricks notebook and configure any necessary parameters.
* Step 5: Set up triggers for the pipeline to run at scheduled intervals (Scheduled daily: 7.00am).
* Step 6: Monitor the pipeline execution using Azure Data Factory’s monitoring tools.