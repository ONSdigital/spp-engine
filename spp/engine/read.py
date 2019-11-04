from pyspark.sql import SparkSession
from .query import Query
import pandas as pd
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def read_db(connection, database, table, select=None, where=None, keep_semicolon=False):

    """
    Reads a DataFrame from a database connected to the Spark metastore or a connection object.
    :param connection: Spark session or DB connection object
    :param database: Database name
    :param table: Table name
    :param select: Column or [columns] to select
    :param where: Filter condition
    :param keep_semicolon: If True, query is generated with a semicolon suffix
    :returns Spark/Pandas DataFrame:
    """

    # TODO: Look into whether the semicolon is ever necessary
    query = str(Query(database, table, select, where))
    query = query if keep_semicolon else query[:-1]

    logger.info(f"Reading from {database} database")
    logger.info(f"Query: {query}")
    logger.info(f"Connection: {str(connection)}")

    if isinstance(connection, SparkSession):
        return connection.sql(query)
    else:
        return pd.read_sql(query, connection)


def read_file(location, spark=None):

    """
    Reads a DataFrame from a file.
    :param location: File location
    :param spark: If not None, use Spark
    :returns Spark/Pandas DataFrame:
    """

    file_format = location.split('.')[-1]  # cvs, json, parquet...
    logger.info(f"Reading from file")
    logger.info(f"Location: {location}")
    if spark:
        return spark.read.load(location, format=file_format)
    else:
        import s3fs  # Leave this in to check optional dependency explicitly
        return getattr(__import__('pandas'), f'read_{file_format}')(location)
