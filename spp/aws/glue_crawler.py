import boto3
import time
from spp.utils.logging import Logger

LOG = Logger(__name__).get()


def crawl(crawler_name):
    LOG.info("crawler : {}".format(crawler_name)+" starts..")
    client = boto3.client('glue', region_name='eu-west-2')
    client.start_crawler(Name=crawler_name)
    while client.get_crawler(Name=crawler_name)['Crawler']['State'] in \
            ["RUNNING", "STOPPING"]:
        time.sleep(10)
    LOG.info("crawler : {}".format(crawler_name)+" completed")
