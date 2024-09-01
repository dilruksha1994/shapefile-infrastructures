import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
import geopandas as gpd
import os
import tempfile
from azure.storage.blob import BlobServiceClient
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress Azure SDK HTTP logs
azure_http_logger = logging.getLogger('azure.core.pipeline.policies.http_logging_policy')
azure_http_logger.setLevel(logging.WARNING)

app = FastAPI()

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Shapefile Processing API"}

# Azure Blob Storage connection details
connection_string = "DefaultEndpointsProtocol=https;AccountName=stshapefilesasia;AccountKey=ICGwTGIstDGHQcac/TrRKSYoIzfuTw7flxQP4p5f3XR/bJCF8uwpIo+I9j2xd989wWoLhNdEWCMQ+AStu1eWZA==;EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Database connection details
db_name = "postgres"
user = "shapefileadmin"
password = "Dil@1994"
host = "psql-shapefile-sasia.postgres.database.azure.com"
port = "5432"
password = quote_plus(password)
db_connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

engine = create_engine(db_connection_string, pool_pre_ping=True)

class ShapefileRequest(BaseModel):
    container_name: str = Field(default="shapefiles", title="Azure Blob Storage container name")
    blob_name: str = Field(default="HE_Regions.shp", title="Shapefile blob name")

@app.post("/process-shapefile/")
async def process_shapefile(background_tasks: BackgroundTasks, request: ShapefileRequest = ShapefileRequest()):
    try:
        # Pass the entire request object to the background task
        background_tasks.add_task(process_and_store_shapefile, request)        
        return {"status": "Shapefile is being processed..."}
    except Exception as e:
        logger.error(f"An error occurred while starting the processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def process_and_store_shapefile(request: ShapefileRequest):
    try:
        logger.info("Shapefile processing started...")
        # Define the shapefile components
        file_names = ["HE_Regions.shp", "HE_Regions.shx", "HE_Regions.dbf", "HE_Regions.prj", "HE_Regions.cpg"]

        with tempfile.TemporaryDirectory() as tmpdirname:
            for file_name in file_names:
                # Download each component of the shapefile
                blob_client = blob_service_client.get_blob_client(container=request.container_name, blob=file_name)
                file_path = os.path.join(tmpdirname, file_name)
                with open(file_path, "wb") as file:
                    file.write(blob_client.download_blob().readall())

            # Load the shapefile using GeoPandas
            gdf = gpd.read_file(os.path.join(tmpdirname, "HE_Regions.shp"))

            # Convert geometry to WKT format for storage in PostgreSQL
            gdf['wkt_geometry'] = gdf['geometry'].apply(lambda x: x.wkt)
            logger.info("Data read successfully from the AZ Blob Storage...")

        with engine.connect() as conn:
            conn = conn.execution_options(isolation_level="AUTOCOMMIT")

            # Step 5: Truncate the Table
            truncate_query = "TRUNCATE TABLE shapefile_data;"
            try:
                conn.execute(text(truncate_query))
                logger.info("Table truncated successfully...")
            except Exception as e:
                logger.error(f"An error occurred during truncation: {e}")
                return

            # Step 6: Insert Shapefile Data into PostgreSQL
            insert_query = """
            INSERT INTO shapefile_data (name, geometry) VALUES (:name, :geometry);
            """
            try:
                for _, row in gdf.iterrows():
                    conn.execute(
                        text(insert_query),
                        {"name": row["NAME"], "geometry": row["wkt_geometry"]}
                    )
                logger.info("Data inserted successfully to the PostgreSQL DB table...")
            except Exception as e:
                logger.error(f"An error occurred during insertion: {e}")

        logger.info("Shapefile processing successfully finished.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during shapefile processing: {e}")

@app.get("/status/")
async def check_status():
    return {"status": "Service is running"}
