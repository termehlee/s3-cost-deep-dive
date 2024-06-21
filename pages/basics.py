import streamlit as st
import pandas as pd
import plotly.express as px  # interactive charts
import math
from st_pages import add_page_title, add_indentation
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.layouts import TreeLayout
import images

add_indentation()
add_page_title(layout="wide")
st.markdown("""
            This flow map depicts the basic S3 cost components that this workshop will cover. Overall, there are 5 main components:
             1. Storage & requests
             2. Data transfer
             3. Security access & control
             4. Management & insights
             5. Replication
             6. Transform & query  \n
            In this workshop, we will focus on **storage & requests**, **data transfer** and **management & insights**.
            """)

pricing_id = {
    '1': 'S3 Cost Components',
    '2': 'Storage & requests',
    '3': 'Data transfer',
    '4': 'Security access & control',
    '5': 'Management & insights',
    '6': 'Replication',
    '7': 'Transform & query',
    '8': 'Storage pricing',
    '9': 'Request & data retrievals',
    '10': 'PUT, COPY, POST, LIST requests',
    '11': 'GET, SELECT, and all other requests',
    '12': 'Lifecycle Transition requests',
    '13': 'Data Retrieval',
    '14': 'Data Retrieval requests',
    '15': 'Data retrievals per GB',
    '16': 'Data transfer IN from Internet',
    '17': 'Data transfer OUT to Internet',
    '18': 'Data transfer OUT to other Regions',
    '26': 'Storage management',
    '27': 'Storage insights',
    '28': 'S3 Inventory',
    '29': 'S3 Object Tagging',
    '30': 'S3 Batch Operations',
    '31': 'Batch Operations - Jobs',
    '32': 'Batch Operations - Objects',
    '33': 'Batch Operations - Manifest',
    '34': 'S3 Storage Lens',
    '35': 'Free metrics',
    '36': 'Advanced metrics',
    '37': 'S3 Storage Class Analysis'
}

pricing_description = {
    '1': 'Overview of basic cost components involved in Amazon S3 pricing. Click on each seperate node to learn more!',
    '2': 'This component covers the costs associated with storing data and making requests to Amazon S3. Each cost differs according to the storage classes you are interacting with - Amazon S3 offers a range of storage classes designed for different use cases. Below are the main storage classes available in Amazon S3:',
    '3': 'This component covers the costs for transferring data in and out of Amazon S3. You pay for all bandwidth into and out of Amazon S3, except for the following:  \n 1. Data transferred out to the internet for the first 100GB per month, aggregated across all AWS Services and Regions (except China and GovCloud)  \n 2. Data transferred in from the internet.  \n 3. Data transferred between S3 buckets in the same AWS Region.  \n 4. Data transferred from an Amazon S3 bucket to any AWS service(s) within the same AWS Region as the S3 bucket (including to a different account in the same AWS Region).  \n 5. Data transferred out to Amazon CloudFront (CloudFront).',
    '4': 'Costs related to securing and controlling access to S3 data (hidden).',
    '5': "This component covers the costs for management and analytics features in S3 that are enabled on your account's buckets.",
    '6': 'Replication: Costs for replicating data across different S3 locations (hidden).',
    '7': 'Transform & query: Costs for transforming and querying data in S3 (hidden).',
    '8': "You pay for storing objects in your S3 buckets. The rate you’re charged depends on your objects' size, how long you stored the objects during the month, and the storage class selected.  \n For S3 Intelligent-Tiering, theres is a monthly monitoring and automation charge per object stored to monitor access patterns and move objects between access tiers.",
    '9': 'You pay for requests made against your S3 buckets and objects. S3 request costs are based on the request type, and are charged on the quantity of requests.  \n  Note: DELETE and CANCEL requests are free.  \n There are no retrieval charges in S3 Intelligent-Tiering. If an object in the infrequent access tier is accessed later, it is automatically moved back to the frequent access tier at no additional cost',
    '10': """These are considered WRITE actions against objects in Amazon S3.  
    \n **PUT Requests**  \n + Purpose: The PUT request is used to upload a new object to a specified bucket or to update an existing object.  \n + Usage: Commonly used for uploading files, such as images, documents, or any other data.  
    \n **COPY Requests**  \n  + Purpose: The COPY request is used to create a copy of an existing object within the same bucket or to a different bucket.  \n  + Usage: Typically used for duplicating files, creating backups, or moving files between different locations within Amazon S3.  
    \n **POST Request**  \n  + Purpose: The POST request is used to add an object to a bucket. It is similar to the PUT request but is often used in HTML forms where the form data is sent to the server.  \n + Usage: Commonly used for web applications where users upload files through a form.  
    \n **LIST Requests**  \n + Purpose: The LIST request is used to retrieve a list of objects within a bucket. This can include metadata about the objects.  \n + Usage: Typically used to display the contents of a bucket, such as listing all files in a directory.""",
    '11': """These are considered READ actions against objects in Amazon S3.  
    \n **GET Requests**  \n + Purpose: The GET request is used to retrieve an object from an S3 bucket. This includes downloading files or fetching object metadata.  \n + Usage: Commonly used for accessing files, such as images, documents, or any other data stored in S3.  
    \n **SELECT Requests**  \n + Purpose: The SELECT request is used to retrieve a subset of data from an object using SQL-like queries. This allows you to filter and retrieve only the necessary data, reducing the amount of data transferred.  \n + Usage: Typically used for querying large datasets stored in CSV, JSON, or Parquet formats to extract specific information without downloading the entire object.  
    \n **All other Requests**  \n + Purpose: The other requests are used to perform other actions that are not PUT, COPY, POST and LIST requests - such as HEAD, GetObjectTagging, GetObjectRetention requests.  \n + Usage: Commonly used for performing other actions not listed above.""",
    '12': 'Lifecycle Transition requests: Costs for lifecycle transition requests.',
    '13': 'Data Retrieval: General costs for retrieving data from S3.',
    '14': 'Data Retrieval requests: Costs for specific data retrieval requests.',
    '15': 'Data retrievals per GB: Costs for data retrievals measured per GB.',
    '16': 'Data transfer IN from Internet: Costs for transferring data into S3 from the internet.',
    '17': 'Data transfer OUT to Internet: Costs for transferring data out of S3 to the internet.',
    '18': 'Data transfer OUT to other Regions: Costs for transferring data out of S3 to other AWS regions.',
    '26': 'Storage management: Costs for managing storage in S3.',
    '27': 'Storage insights: Costs for gaining insights into storage usage in S3.',
    '28': 'S3 Inventory: Costs for using S3 Inventory to manage objects.',
    '29': 'S3 Object Tagging: Costs for tagging objects in S3.',
    '30': 'S3 Batch Operations: Costs for batch operations in S3.',
    '31': 'Batch Operations - Jobs: Costs for jobs in batch operations.',
    '32': 'Batch Operations - Objects: Costs for objects in batch operations.',
    '33': 'Batch Operations - Manifest: Costs for manifest in batch operations.',
    '34': 'S3 Storage Lens: Costs for using S3 Storage Lens for insights.',
    '35': 'Free metrics: Costs for free metrics in S3 Storage Lens.',
    '36': 'Advanced metrics: Costs for advanced metrics in S3 Storage Lens.',
    '37': 'S3 Storage Class Analysis: Costs for analyzing storage classes in S3.'
}

def storage_classes():
    cols = st.columns(7)
    with cols[0]:
        st.image('s3_cost_sim/images/standard.svg', 'S3 Standard')
    with cols[1]:
        st.image('s3_cost_sim/images/intelligent-tiering.svg', 'S3 Intelligent Tiering')
    with cols[2]:
        st.image('s3_cost_sim/images/standard-IA.svg', 'S3 Infrequent Access')
    with cols[3]:
        st.image('s3_cost_sim/images/onezone-IA.svg', 'S3 Infrequent Access - One Zone')
    with cols[4]:
        st.image('s3_cost_sim/images/gir.svg', 'S3 Glacier Instant Retrieval')
    with cols[5]:
        st.image('s3_cost_sim/images/gfr.svg', 'S3 Glacier Flexible Retrieval')
    with cols[6]:
        st.image('s3_cost_sim/images/gda.svg', 'S3 Glacier Deep Archive')



nodes = [StreamlitFlowNode(id='1', pos=(0, 0), data={'label': 'S3 Cost Components'}, node_type='input', source_position='bottom'),
        StreamlitFlowNode('2', (0, 0), {'label': 'Storage & requests'}, 'default', 'bottom', 'top'),
        StreamlitFlowNode('3', (0, 0), {'label': 'Data transfer'}, 'default', 'bottom', 'top'),
        StreamlitFlowNode('4', (0, 0), {'label': 'Security access & control'}, 'default', target_position='top', hidden=True),
        StreamlitFlowNode('5', (0, 0), {'label': 'Management & insights'}, 'default', target_position='top'),
        StreamlitFlowNode('6', (0, 0), {'label': 'Replication'}, 'default', target_position='top', hidden=True),
        StreamlitFlowNode('7', (0, 0), {'label': 'Transform & query'}, 'default', target_position='top', hidden=True),
        StreamlitFlowNode('8', (0, 0), {'label': 'Storage pricing'}, 'default', 'bottom', 'top'),
        StreamlitFlowNode('9', (0, 0), {'label': 'Request & data retrievals'}, 'default', 'bottom', 'top'),
        StreamlitFlowNode('10', (0, 0), {'label': 'PUT, COPY, POST, LIST requests'}, 'output', target_position='top'),
        StreamlitFlowNode('11', (0, 0), {'label': 'GET, SELECT, and all other requests'}, 'output', target_position='top'),
        StreamlitFlowNode('12', (0, 0), {'label': 'Lifecycle Transition requests'}, 'output', target_position='top'),
        StreamlitFlowNode('13', (0, 0), {'label': 'Data Retrieval'}, 'default', target_position='top'),
        StreamlitFlowNode('14', (0, 0), {'label': 'Data Retrieval requests'}, 'output', target_position='top'),
        StreamlitFlowNode('15', (0, 0), {'label': 'Data retrievals per GB'}, 'output', target_position='top'),
        StreamlitFlowNode('16', (0, 0), {'label': 'Data transfer IN from Internet'}, 'output', target_position='top'),
        StreamlitFlowNode('17', (0, 0), {'label': 'Data transfer OUT to Internet'}, 'output', target_position='top'),
        StreamlitFlowNode('18', (0, 0), {'label': 'Data transfer OUT to other Regions'}, 'output', target_position='top'),
        # StreamlitFlowNode('19', (0, 0), {'label': 'S3 Multi-Region Access Points'}, 'default', target_position='top', hidden=True),
        # StreamlitFlowNode('20', (0, 0), {'label': 'S3 MRAP data routing'}, 'output', target_position='top', hidden=True),
        # StreamlitFlowNode('21', (0, 0), {'label': 'S3 MRAP internet acceleration'}, 'output', target_position='top', hidden=True),
        # StreamlitFlowNode('22', (0, 0), {'label': 'S3 MRAP failover controls'}, 'output', target_position='top', hidden=True),
        # StreamlitFlowNode('23', (0, 0), {'label': 'S3 Transfer Acceleration'}, 'output', target_position='top', hidden=True),
        # StreamlitFlowNode('24', (0, 0), {'label': 'S3 Encryption'}, 'output', target_position='top', hidden=True),
        # StreamlitFlowNode('25', (0, 0), {'label': 'S3 Access Grants'}, 'output', target_position='top', hidden=True),
        StreamlitFlowNode('26', (0, 0), {'label': 'Storage management'}, 'default', target_position='top'),
        StreamlitFlowNode('27', (0, 0), {'label': 'Storage insights'}, 'default', target_position='top'),
        StreamlitFlowNode('28', (0, 0), {'label': 'S3 Inventory'}, 'default', target_position='top'),
        StreamlitFlowNode('29', (0, 0), {'label': 'S3 Object Tagging'}, 'default', target_position='top'),
        StreamlitFlowNode('30', (0, 0), {'label': 'S3 Batch Operations'}, 'default', target_position='top'),
        StreamlitFlowNode('31', (0, 0), {'label': 'Batch Operations - Jobs'}, 'output', target_position='top'),
        StreamlitFlowNode('32', (0, 0), {'label': 'Batch Operations - Objects'}, 'output', target_position='top'),
        StreamlitFlowNode('33', (0, 0), {'label': 'Batch Operations - Manifest'}, 'output', target_position='top'),
        StreamlitFlowNode('34', (0, 0), {'label': 'S3 Storage Lens'}, 'default', target_position='top'),
        StreamlitFlowNode('35', (0, 0), {'label': 'Free metrics'}, 'output', target_position='top'),
        StreamlitFlowNode('36', (0, 0), {'label': 'Advanced metrics'}, 'output', target_position='top'),
        StreamlitFlowNode('37', (0, 0), {'label': 'S3 Storage Class Analysis'}, 'output', target_position='top'),
        ]

edges = [StreamlitFlowEdge('1-2', '1', '2', animated=True),
        StreamlitFlowEdge('1-3', '1', '3', animated=True),
        StreamlitFlowEdge('1-4', '1', '4', animated=True),
        StreamlitFlowEdge('1-5', '1', '5', animated=True),
        StreamlitFlowEdge('1-6', '1', '6', animated=True),
        StreamlitFlowEdge('1-7', '1', '7', animated=True),
        StreamlitFlowEdge('2-8', '2', '8', animated=True),
        StreamlitFlowEdge('2-9', '2', '9', animated=True),
        StreamlitFlowEdge('9-10', '9', '10', animated=True),
        StreamlitFlowEdge('9-11', '9', '11', animated=True),
        StreamlitFlowEdge('9-12', '9', '12', animated=True),
        StreamlitFlowEdge('9-13', '9', '13', animated=True),
        StreamlitFlowEdge('13-14', '13', '14', animated=True),
        StreamlitFlowEdge('13-15', '13', '15', animated=True),
        StreamlitFlowEdge('3-16', '3', '16', animated=True),
        StreamlitFlowEdge('3-17', '3', '17', animated=True),
        StreamlitFlowEdge('3-18', '3', '18', animated=True),
        StreamlitFlowEdge('5-26', '5', '26', animated=True),
        StreamlitFlowEdge('5-27', '5', '27', animated=True),
        StreamlitFlowEdge('26-28', '26', '28', animated=True),
        StreamlitFlowEdge('26-29', '26', '29', animated=True),
        StreamlitFlowEdge('26-30', '26', '30', animated=True),
        StreamlitFlowEdge('30-31', '30', '31', animated=True),
        StreamlitFlowEdge('30-32', '30', '32', animated=True),
        StreamlitFlowEdge('30-33', '30', '33', animated=True),
        StreamlitFlowEdge('27-34', '27', '34', animated=True),
        StreamlitFlowEdge('34-35', '34', '35', animated=True),
        StreamlitFlowEdge('34-36', '34', '36', animated=True),
        StreamlitFlowEdge('27-37', '27', '37', animated=True),
        # StreamlitFlowEdge('19-18', '19', '18', animated=True, hidden=True),
        # StreamlitFlowEdge('19-20', '19', '20', animated=True, hidden=True),
        # StreamlitFlowEdge('19-21', '19', '21', animated=True, hidden=True),
        # StreamlitFlowEdge('19-22', '19', '22', animated=True, hidden=True),
        # StreamlitFlowEdge('3-23', '3', '23', animated=True, hidden=True),
        ]

selected_id = streamlit_flow('tree_layout', 
                             nodes, 
                             edges, 
                             layout=TreeLayout(direction='down'), 
                             fit_view=True, 
                             get_node_on_click=True,
                             show_minimap=True,
                             show_controls=True)

if selected_id:
    st.markdown(f"""#### {pricing_id[selected_id]}""")
    st.markdown(f""" {pricing_description[selected_id]}""")

    if selected_id == '2':
        storage_classes()

