# Databricks notebook: fire_config
# version: NotebookV1  origId: 2270797741141910
# extracted: 2026-04-20  source: reg_reporting.dbc (2021-09-28)

# COMMAND ----------
config = {
  "fire_entity"         : "collateral",
  "pipeline_dir"        : "/FileStore/antoine.amend@databricks.com/fire/collateral",
  "data_sharing_path"   : "/FileStore/antoine.amend@databricks.com/fire/share/collateral",
  "data_sharing_table"  : "fire_pipeline.collateral",
  "metrics_table"       : "fire_pipeline.ods"
}

# COMMAND ----------
import pandas as pd
 
# as-is, we simply retrieve dictionary key, but the reason we create a function
# is that user would be able to replace dictionary to application property file
# without impacting notebook code
def getParam(s):
  return config[s]

