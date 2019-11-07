class DataAccess:
    """
    Wrapper that calls the differing Data Access methods depending on the platform that the pipeline is running on and
    whether it is utilising Apache Spark or is a pure python project
    """

    query = None
    name = None

    def __int__(self, name, query):
        """
        Takes in the Query object that is used to access the data
        :param name: String
        :param query: spp.utils.query.Query
        :return:
        """
        self.query = query
        self.name - name

    def read_data(self, platform, spark=None):
        """
        Will call the specific data retrieval method depending on the Platform and whether it is spark or not
        using the query supplies when instantiation the class.
        :param platform: Platform
        :param spark: SparkSession
        :return:
        """
        if spark is None:
            # TODO import the correct data access class and call get data to return in
            return
        else:
            # TODO spark version of the above
            return


def write_data(output, platform, spark=None):
    """
    This method may be removed as further requirements determine whether this should be a generic function
    :param output: Dataframe
    :param platform: Platform
    :param spark: SparkSession
    :return:
    """
    if spark is None:
        # TODO write outputs
        return
    else:
        # TODO Spark Version
        return
