# Databricks notebook: 02_fire_metrics
# version: NotebookV1  origId: 3366858372929093
# extracted: 2026-04-20  source: reg_reporting.dbc (2021-09-28)

# COMMAND ----------
%md
# Pipeline monitoring
In the previous notebook, we demonstrated how to ingest, clean and process raw data used in the transmission of regulatory reports. We stored high quality data to a silver table and invalid records to quarantine. Although data quality metrics are available from the job interface, we demonstrate how organizations can programmatically access those metrics into an operational datastore.

[![DLT](https://img.shields.io/badge/-DLT-grey)]()
[![DLT](https://img.shields.io/badge/-AUTO_LOADER-grey)]()
[![DLT](https://img.shields.io/badge/-DELTA_SHARING-grey)]()

# COMMAND ----------
fire_entity = getParam("fire_entity")
pipeline_dir = getParam("pipeline_dir")
data_sharing_path = getParam("data_sharing_path")
data_sharing_table = getParam("data_sharing_table")
metrics_table = getParam("metrics_table")

# COMMAND ----------
%md
## Extracting metrics
As reported in the previous notebook, delta live table runs against a specific pipeline path. In addition to the actual data being stored as delta files under the `./tables` directory (our external tables), delta live tables also stores operation metrics in `./system/events`. In the section below, we demonstrate how to extract relevant data quality metrics matching our business and technical expectations set earlier. 

# COMMAND ----------
events = spark.read.format("delta").load("{}/system/events".format(pipeline_dir))
display(events)

# COMMAND ----------
%md
This table contains nested elements as json records that we can easily extract through simple user defined functions. For convenience, we wrap that logic in plain python using the `applyInPandas` pattern that expects a pandas dataframe as an input and returns a pandas dataframe of a defined schema. 

# COMMAND ----------
from pyspark.sql import functions as F
from pyspark.sql.types import *
import pandas as pd
import json

event_schema = StructType([
  StructField('timestamp', TimestampType(), True),
  StructField('step', StringType(), True),
  StructField('expectation', StringType(), True),
  StructField('passed', IntegerType(), True),
  StructField('failed', IntegerType(), True),
])

def events_to_dataframe(df):
  d = []
  group_key = df['timestamp'].iloc[0]
  for i, r in df.iterrows():
    json_obj = json.loads(r['details'])
    try:
      expectations = json_obj['flow_progress']['data_quality']['expectations']
      for expectation in expectations:
        d.append([group_key, expectation['dataset'], expectation['name'], expectation['passed_records'], expectation['failed_records']])
    except:
      pass
  return pd.DataFrame(d, columns=['timestamp', 'step', 'expectation', 'passed', 'failed'])

def extract_metrics(df):
  return df \
    .filter(F.col("event_type") == "flow_progress") \
    .groupBy("timestamp").applyInPandas(events_to_dataframe, schema=event_schema) \
    .withColumn("entity", F.lit(fire_entity)) \
    .select("timestamp", "entity", "step", "expectation", "passed", "failed")

# COMMAND ----------
metrics = extract_metrics(events)
display(metrics)

# COMMAND ----------
%md
## Operation data store
Given that operational metrics are stored as a delta format, we can leverage the functionality of Delta to operate as both batch and streaming and only consume delta increment (i.e. new metrics). For each entity, we process the latest metrics since last checkpoint using the structured streaming API and [trigger Once](https://databricks.com/blog/2017/05/22/running-streaming-jobs-day-10x-cost-savings.html) functionality. Running e.g. daily, this job will only process last day worth of metrics, appending newly acquired metrics to our operation data store

# COMMAND ----------
input_stream = spark \
    .readStream \
    .format("delta") \
    .load("{}/system/events".format(pipeline_dir)) \

output_stream = extract_metrics(input_stream)
    
output_stream \
  .writeStream \
  .trigger(once=True) \
  .format("delta") \
  .option("checkpointLocation", "{}/ods_checkpoint".format(pipeline_dir)) \
  .table(metrics_table)

# COMMAND ----------
display(
  spark
    .read
    .table(metrics_table)
    .groupBy(F.to_date(F.col("timestamp")).alias("date"))
    .agg(F.sum("passed").alias("passed"), F.sum("failed").alias("failed"))
)

# COMMAND ----------
%md
With all metrics available centrally into an operation store, analysts can create simple dashboarding capabilities or more complex alerting mechanisms on real time data quality. With Delta Lake ensuring full transparency of operation metrics coupled with immutability of actual regulatory data, organizations can easily time travel to a specific version that matches both volume and quality required for full regulatory compliance. 

# COMMAND ----------
from delta.tables import *
deltaTable = DeltaTable.forPath(spark, "{}/tables/silver".format(pipeline_dir))
display(deltaTable.history())

# COMMAND ----------
%md
# Transmitting reports

With full confidence in both quality and volume, financial institutions can safely exchange information with regulators using [Delta Sharing](https://databricks.com/blog/2021/05/26/introducing-delta-sharing-an-open-protocol-for-secure-data-sharing.html). We select our high quality and immutable slice of collateral data and create a copy to an externally facing distributed file storage using Delta `cloneAtVersion` capability (time travel).

# COMMAND ----------
deltaTable.cloneAtVersion(0, data_sharing_path, isShallow=True, replace=True)
_ = sql("CREATE TABLE IF NOT EXISTS {} USING DELTA LOCATION '{}'".format(data_sharing_table, data_sharing_path))

# COMMAND ----------
%md
We report below an example workflow (the following are for demonstration only and will only work with delta sharing enabled) used to grant regulators access to our data. We create a `SHARE` and add collateral entity table of a given version whilst maintaining strict access controls and granular audit logs in unity catalogue.

# COMMAND ----------
%sql
CREATE SHARE regulatory_reports;
ALTER SHARE regulatory_reports ADD TABLE fire_pipeline.collateral;

# COMMAND ----------
%md
We can register a recipient we want to share data with. Using this activation link, regulatory bodies will be able to download a connection profile (`.share` file) that contains a unique token to our delta share server in order to access our underlying data in a safe and transparent manner.

<img src="https://databricks-web-files.s3.us-east-2.amazonaws.com/notebooks/reg_reporting/images/delta_share_activation.png" width=800>

# COMMAND ----------
%sql
CREATE RECIPIENT regulatory_body;

# COMMAND ----------
%md
Finally, we grant regulators access to our share `regulatory_reports`. At this point, any user with granted privileges will be able to access our underlying data using their tools of choice, from in memory pandas to distributed dataframe or even directly through BI/MI capabilities. For more information about delta sharing, please visit delta [product page](https://delta.io/sharing/) and reach out to a databricks representative.

# COMMAND ----------
%md
## Take away
Through that series of notebooks and delta live table jobs, we demonstrated the benefits of the lakehouse architecture for regulatory compliance workloads. Specifically, we addressed the need for organizations to ensure consistency, integrity and timeliness of regulatory pipelines that could be easily achieved using a common data model (FIRE) coupled with a flexible orchestration engine (Delta Live Tables). With Delta Sharing capabilities, we finally demonstrated how FSIs could bring full transparency by sharing immutable reports to regulators using open protocols.

# COMMAND ----------
%run ./config/fire_config

# COMMAND ----------


# COMMAND ----------


