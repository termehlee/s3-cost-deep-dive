import boto3
import json

region_code = {
    'us-east-1': 'USE1', # US East (N. Virginia)
    'us-east-2': 'USE2', # US East (Ohio)
    'us-west-1': 'USW1', # US West (N. California)
    'us-west-2': 'USW2', # US West (Oregon)
    'ap-east-1': 'APE1', # Asia Pacific (Hong Kong)
    'ap-south-1': 'APS1', # Asia Pacific (Mumbai)
    'ap-northeast-1': 'APN1', # Asia Pacific (Tokyo)
    'ap-northeast-2': 'APN2', # Asia Pacific (Seoul)
    'ap-southeast-1': 'APS1', # Asia Pacific (Singapore)
    'ap-southeast-2': 'APS2', # Asia Pacific (Sydney)
    'ap-southeast-3': 'APS3', # Asia Pacific (Jakarta)
    'ap-northeast-3': 'APN3', # Asia Pacific (Osaka)
    'af-south-1': 'AFS1', # Africa (Cape Town)
    'ca-central-1': 'CAN1', # Canada (Central)
    'ca-west-1': 'CAN2', # Canada (Calgary)
    'eu-central-1': 'EUC1', # Europe (Frankfurt)
    'eu-central-2': 'EUC2', # Europe (Zurich)
    'eu-south-1': 'EUS1', # Europe (Milan)
    'eu-west-1': 'EU', # Europe (Ireland)
    'eu-west-2': 'EUW2', # Europe (London)
    'eu-west-3': 'EUW3', # Europe (Paris)
    'eu-south-2': 'EUS2', # Europe (Spain)
    'eu-north-1': 'EUN1', # Europe (Stockholm)
    'sa-east-1': 'SAE1', # South America (São Paulo)
    'me-south-1': 'MES1', # Middle East (Bahrain)
    'me-central-1': 'MEC1', # Middle East (UAE)
    'il-central-1': 'ILC1', # Israel (Tel Aviv)
}

# checked
s3_volume_types = {
    'STANDARD': 'Standard',
    'STANDARD_IA': 'Standard - Infrequent Access',
    'ONEZONE_IA': 'One Zone - Infrequent Access',
    'INTELLIGENT_TIERING': 'Intelligent-Tiering',
    'GLACIER': 'Amazon Glacier',
    'DEEP_ARCHIVE': 'Glacier Deep Archive',
    'GLACIER_IR': 'Glacier Instant Retrieval'
}

s3_storage_classes = {
    'S3 Standard': 'STANDARD',
    'S3 Standard - Infrequent Access': 'STANDARD_IA',
    'S3 One Zone - Infrequent Access': 'ONEZONE_IA',
    'S3 Intelligent-Tiering': 'INTELLIGENT_TIERING',
    'S3 Glacier Flexible Retrieval': 'GLACIER',
    'S3 Glacier Deep Archive': 'DEEP_ARCHIVE',
    'S3 Glacier Instant Retrieval': 'GLACIER_IR'
}

s3_req_filters = {
    'STANDARD': {
        'PUT': {
            'group': 'S3-API-Tier1'
        },
        'storage': {
            'usageType': 'TimedStorage-ByteHrs'
        },
        'GET': {
            'group': 'S3-API-Tier2'
        }
    },
    'STANDARD_IA': {
        'PUT': {
            'group': 'S3-API-SIA-Tier1'
        },
        'storage': {
            'usageType': 'TimedStorage-SIA-ByteHrs'
        },
        'GET': {
            'group': 'S3-API-SIA-Tier2'
        },
        'retrieval': {
            'group': 'S3-API-SIA-Retrieval'
        }
    },
    'ONEZONE_IA': {
        'PUT': {
            'group': 'S3-API-ZIA-Tier1'
        },
        'storage': {
            'usageType': 'TimedStorage-ZIA-ByteHrs'
        },
        'GET': {
            'group': 'S3-API-ZIA-Tier2'
        },
        'retrieval': {
            'group': 'S3-API-ZIA-Retrieval'
        }
    },
    'INTELLIGENT_TIERING': {
        'PUT': {
            'group': 'S3-API-INT-Tier1'
        },
        'storage': {
            'usageType': 'TimedStorage-INT-FA-ByteHrs'
        },
        'GET': {
            'group': 'S3-API-INT-Tier2'
        }
    },
    'GLACIER': {
        'PUT': {
            'group': 'S3-API-GLACIER-Tier1',
            'operation': 'PutObject'
        },
        'storage': {
            'usageType': 'TimedStorage-GlacierByteHrs'
        },
        'GET': {
            'group': 'S3-API-GLACIER-Tier2'
        },
        'retrieval': {
            'feeCode': 'S3-Standard-Retrieval',
            'operation': 'RestoreObject'
        },
        'retrievalreq': {
            'group': 'S3-API-Tier3',
            'operation': 'RestoreObject'
        }
    },
    'GLACIER_IR': {
        'PUT': {
            'group': 'S3-API-GIR-Tier1'
        },
        'storage': {
            'usageType': 'TimedStorage-GIR-ByteHrs'
        },
        'GET': {
            'group': 'S3-API-GIR-Tier2'
        },
        'retrieval': {
            'group': 'S3-API-GIR-Retrieval'
        }
    },
    'DEEP_ARCHIVE': {
        'PUT': {
            'group': 'S3-API-Tier3',
            'operation': 'S3-GDATransition'
        },
        'storage': {
            'usageType': 'TimedStorage-INT-DAA-ByteHrs'
        },
        'GET': {
            'group': 'S3-API-GDA-Tier2'
        },
        'retrieval': {
            'feeCode': 'S3-Standard-Retrieval',
            'operation': 'DeepArchiveRestoreObject'
        },
        'retrievalReq': {
            'group': 'S3-API-Tier3',
            'operation': 'RestoreObject' # need to figure out what this is 
        }
    }
}

pricing = boto3.client('pricing',region_name='us-east-1')

## Function to get S3 pricing
def get_s3_pricing(filters):
    response = pricing.get_products(
        ServiceCode='AmazonS3',
        Filters=filters
    )
    if response['PriceList'] == {}:
        print('critical:', 'No products returned for {filter}')

    price_list = json.loads(response['PriceList'][0])
    for price_dimension in price_list['terms']['OnDemand'].values():
        for description, rate_value in price_dimension['priceDimensions'].items():
            #Ensure we are only getting one price from tiered storage costs
            if rate_value["beginRange"] == "0":
                pricing_data = float(rate_value["pricePerUnit"]["USD"])
                unit = rate_value["unit"]
    print('info:', f"Price for {description} is ${pricing_data} per {unit}")
    return pricing_data

# Function to append filter for AWS Price List
def add_pricing_filter(filter, field, value):
    if filter is None:
        filter = []
    updated_filter = filter.copy()
    updated_filter.append({'Type': 'TERM_MATCH', 'Field': field, 'Value': value})
    # print('filter info', updated_filter)
    return updated_filter

# Function to retrieve ingestion pricing
def get_s3_put_cost(storage_class, region):
    filter = [{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region}]
    for field, value in s3_req_filters[storage_class]['PUT'].items():
        filter = add_pricing_filter(filter, field, value)
    put_cost = get_s3_pricing(filter)
    return put_cost

# Function to retrieve storage pricing
def get_s3_storage_cost(storage_class, region):
    filter = [{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region}]
    prefix = ""
    if region != 'us-east-1':
        prefix = region_code[region] + "-"
    for field, value in s3_req_filters[storage_class]['storage'].items():
        filter = add_pricing_filter(filter, field, prefix+value)
    storage_cost = get_s3_pricing(filter)
    return storage_cost

# Function to retrieve get cost
def get_s3_get_cost(storage_class, region):
    filter = [{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region}]
    for field, value in s3_req_filters[storage_class]['GET'].items():
        filter = add_pricing_filter(filter, field, value)
    get_cost = get_s3_pricing(filter)
    return get_cost

# Function to retrieve retrieval gb cost
def get_s3_retrieval_cost(storage_class, region):
    filter = [{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region}]
    if 'retrievalReq' in s3_req_filters.get(storage_class, {}):
        for field, value in s3_req_filters[storage_class]['retrieval'].items():
            filter = add_pricing_filter(filter, field, value)
        retrieval_cost = get_s3_pricing(filter)
    else:
        retrieval_cost = 0
    return retrieval_cost

# Function to retrieve retrieval cost
def get_s3_retrieval_req_cost(storage_class, region):
    filter = [{'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region}]
    if 'retrievalReq' in s3_req_filters.get(storage_class, {}):
        for field, value in s3_req_filters[storage_class]['retrievalReq'].items():
            filter = add_pricing_filter(filter, field, value)
        retrieval_req_cost = get_s3_pricing(filter)
        if storage_class == 'GLACIER':
            retrieval_req_cost *= 2
    else :
        retrieval_req_cost = 0
    return retrieval_req_cost
