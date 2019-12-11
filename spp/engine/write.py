import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def spark_write(df, data_target, counter,**kwargs):
    """
    Writes a Spark DataFrame to a file.
    :param df: Spark DataFrame
    :param location: File location
    :param kwargs: Other keyword arguments to pass to df.write.save()
    """
   # _write_log(location)
    if counter >= 1:
        tmp_path =   "/data" + str(counter)
    else:
        tmp_path =  ''

    df.repartition(*data_target['partition_by']).write.save(path = data_target['location']+tmp_path, format=data_target['format'], partitionBy= data_target['partition_by'], **kwargs)


def pandas_write(df, location, **kwargs):
    """
    Writes a Pandas DataFrame to a file.
    :param df: Pandas DataFrame
    :param location: File location
    :param kwargs: Other keyword arguments to pass to df.to_{format}()
    """
    _write_log(location)
    import s3fs  # Leave this in to check optional dependency explicitly
    return getattr(df, "to_{}".format(_get_file_format(location)))(location, **kwargs)


def _get_file_format(location):
    # ToDo
    format = "parquet"
    # return location.split('.')[-1]
    return format


def _write_log(location):
    logger.info(f"Writing to file")
    logger.info(f"Location: {location}")
