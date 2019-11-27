from enum import Enum
from typing import Iterable
from spp.engine.data_access import write_data, DataAccess
from spp.utils.logging import Logger
import importlib

LOG = Logger(__name__).get()


class Platform(Enum):
    """
    Enum that indicates which platform the Pipeline will run on currently only AWS but planned are GCP and Azure
    """
    AWS = "AWS"


class PipelineMethod:
    """
    Wrapper that contains the metadata for a pipeline method that will be called as part of a pipeline
    """

    module_name = None
    method_name = None
    params = None
    data_in = None

    def __init__(self, name, module, queries, params=None):
        """
        Initialise the attributes of the class
        :param name: String
        :param module: String
        :param queries: Dict[String, spp.utils.query.Query]
        :param params: Dict[String, Any]
        """
        LOG.info("Initializing Method")
        self.method_name = name
        self.module_name = module
        self.params = params
        self.data_in = []
        for request in queries:
            name = request['name']
            query = {x: request[x] for x in request if x not in 'df_name'}
            self.data_in.append(DataAccess(name, query))

    def run(self, platform, spark=None):
        """
        Will import the method and call it.  It will then write out the outputs
        :param platform:
        :param spark:
        :return:
        """
        LOG.info("Retrieving data")
        inputs = {data.name: data.read_data(platform, spark) for data in self.data_in}
        LOG.info("Data Retrieved")
        LOG.debug("Retrieved data : {}".format(inputs))
        LOG.info("Importing Module")
        try:
            module = importlib.import_module(self.module_name)
            LOG.debug("Imported {}".format(module))
        except Exception as e:
            LOG.exception("Cant import module {}".format(self.module_name))
            raise e
        LOG.info("Calling Method")
        try:
            LOG.debug("Calling Method: {} with parameters {} {}".format(self.method_name, inputs, self.params))
            outputs = getattr(module, self.method_name)(**inputs, **self.params)
        except TypeError as e:
            LOG.exception("Incorrect Parameters for method called.")
            raise e
        except ValueError as e:
            LOG.exception("Issue with getting parameter name.")
            raise e
        except Exception as e:
            LOG.exception("Issue calling method")
            raise e
        LOG.info("Writing outputs")
        LOG.debug("Writing outputs: {}".format(outputs))
        if isinstance(outputs, Iterable):
            for output in outputs:
                write_data(output, platform, spark)
                LOG.debug("Writing output: {}".format(output))
        else:
            write_data(outputs, platform, spark)
            LOG.debug("Writing output: {}".format(outputs))
        LOG.info("Finished writing outputs Method run complete")


class Pipeline:
    """
    Wrapper to contain the pipeline methods and enable their callling
    """
    platform = None
    name = None
    methods = None
    spark = None

    def __init__(self, name, platform=Platform.AWS, is_spark=False):
        """
        Initialises the attributes of the class.
        :param name:
        :param platform: Platform
        :param is_spark: Boolean
        """
        LOG.info("Initializing Pipeline")
        self.name = name
        self.platform = Platform(platform)
        if is_spark:
            LOG.info("Starting Spark Session for APP {}".format(name))
            from pyspark.sql import SparkSession
            self.spark = SparkSession.builder.appName(name).getOrCreate()
        self.methods = []

    def add_pipeline_methods(self, name, module, queries, params):
        """
        Adds a new method to the pipeline
        :param name: String
        :param module: String
        :param queries: Dict[String, spp.utils.query.Query]
        :param params: Dict[String, Any]
        :return:
        """
        LOG.info("Adding Method to Pipeline")
        LOG.debug("Adding Method: {} , from Module {}, With parameters {}, retrieving data from {}.".format(name,
                                                                                                            module,
                                                                                                            params,
                                                                                                            queries))
        self.methods.append(PipelineMethod(name, module, queries, params))

    def run(self, platform):
        """
        Runs the methods of the pipeline
        :param platform: Platform
        :return:
        """
        LOG.info("Running Pipeline: {}".format(self.name))
        for method in self.methods:
            LOG.info("Running Method: {}".format(method.method_name))
            method.run(platform, self.spark)
            LOG.info("Method Finished: {}".format(method.method_name))


def construct_pipeline(config):

    LOG.debug("Constructing pipeline with name {}, platform {}, is_spark {}".format(
        config['name'], config['platform'], config['spark']
    ))
    pipeline = Pipeline(name=config['name'], platform=config['platform'], is_spark=config['spark'])

    for method in config['methods']:
        LOG.debug("Adding method with name {}, module {}, queries {}, params {}".format(
            method['name'], method['module'], method['data_access'], method['params']
        ))
        pipeline.add_pipeline_methods(
            name=method['name'], module=method['module'], queries=method['data_access'], params=method['params'][0]
        )

    return pipeline


def run(pipeline, config):
    LOG.info("Running pipeline {}, run {}".format(pipeline.name, config['run_id']))
    pipeline.run(platform=config['platform'])
