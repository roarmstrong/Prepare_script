
# coding: utf-8
from xml.etree import ElementTree
from pathlib import Path
import os
from osgeo import osr
import dateutil
from ruamel.yaml import YAML
from dateutil import parser
from datetime import timedelta
import uuid
import yaml
import logging
import click
import re
import boto3
import datacube
from datacube.scripts.dataset import create_dataset, parse_match_rules_options
from datacube.utils import changes


def format_obj_key(obj_key):
    obj_key ='/'.join(obj_key.split("/")[:-1])
    return obj_key


def get_s3_url(bucket_name, obj_key):
    return 's3://{bucket_name}/{obj_key}'.format(
        bucket_name=bucket_name, obj_key=obj_key)


def get_metadata_docs(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    logging.info("Bucket : %s", bucket_name)
    for obj in bucket.objects.filter(Prefix = 'S2-Sample-Products'):
        if obj.key.endswith('ARD-METADATA-S3.yaml'):
            obj_key = obj.key
            logging.info("Processing %s", obj_key)
            raw_string = obj.get()['Body'].read().decode('utf8')
            yaml = YAML(typ='safe',pure = True)
            yaml.default_flow_style = False
            data = yaml.load(raw_string)
            #mtl_doc = _parse_group(iter(raw_string.split("\n")))['L1_METADATA_FILE']
            #metadata_doc = make_metadata_doc(mtl_doc, bucket_name, obj_key)
            #yield obj_key, metadata_doc
            yield obj_key,data
            
            
            
def make_rules(index):
    all_product_names = [prod.name for prod in index.products.get_all()]
    rules = parse_match_rules_options(index, None, all_product_names, True)
    return rules


def add_dataset(doc, uri, rules, index):
    dataset = create_dataset(doc, uri, rules)

    try:
        index.datasets.add(dataset) # Source policy to be checked in sentinel 2 datase types 
    except changes.DocumentMismatchError as e:
        index.datasets.update(dataset, {tuple(): changes.allow_any})
    return uri

def add_datacube_dataset(bucket_name,config):
    dc=datacube.Datacube(config=config)
    index = dc.index
    rules = make_rules(index)
    
    for metadata_path,metadata_doc in get_metadata_docs(bucket_name):
        uri= get_s3_url(bucket_name, metadata_path)
        add_dataset(metadata_doc, uri, rules, index)
        logging.info("Indexing %s", metadata_path)


@click.command(help= "Enter Bucket name. Optional to enter configuration file to access a different database")
@click.argument('bucket_name')
@click.option('--config','-c',help=" Pass the configuration file to access the database",
		type=click.Path(exists=True))
def main(bucket_name, config):
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    add_datacube_dataset(bucket_name,config)
    #get_metadata_docs(bucket_name)
   
    
if __name__ == "__main__":
    main()

