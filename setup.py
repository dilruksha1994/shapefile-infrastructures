from setuptools import setup, find_packages

setup(
    name='shapefile_processor',
    version='0.1.0',
    description='A microservice to process shapefiles and store data in PostgreSQL',
    author='Dilruksha R.',
    author_email='dilruksharajapaksha@gmail.com',
    packages=find_packages(),
    install_requires=[
        'azure-storage-blob',
        'geopandas',
        'psycopg2',
        'sqlalchemy',
        'fastapi',
        'uvicorn',
        'twine',
    ],
    entry_points={
        'console_scripts': [
            'shapefile-processor=main:app',
        ],
    },
)
