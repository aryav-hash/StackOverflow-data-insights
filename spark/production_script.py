#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pyspark
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import functions as F

credentials_location = '/home/aryav/Projects/Airport-Dashboard/terraform/keys/airport-creds.json'
path_to_gcs_connector = "./lib/gcs-connector.jar"

conf = SparkConf() \
    .setMaster('local[*]') \
    .setAppName('test') \
    .set("spark.jars", path_to_gcs_connector) \
    .set("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
    .set("spark.hadoop.google.cloud.auth.service.account.json.keyfile", credentials_location)

sc = SparkContext(conf=conf)

hadoop_conf = sc._jsc.hadoopConfiguration()
hadoop_conf.set("fs.AbstractFileSystem.gs.impl",  "com.google.cloud.hadoop.recommender.gcs.GCSFileSystem")
hadoop_conf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
hadoop_conf.set("fs.gs.auth.service.account.enable", "true")
hadoop_conf.set("fs.gs.auth.service.account.json.keyfile", credentials_location)

spark = SparkSession.builder \
    .config(conf=sc.getConf()) \
    .getOrCreate()


# In[ ]:


bucket_name="airport-dashboard-492216-bucket"


# In[ ]:


df = spark.read.csv(f"gs://{bucket_name}/raw/survey/2025/results.csv", header=True)


# In[ ]:


numeric_regex = "^[0-9]+$"
float_regex = r"^[0-9]*\.?[0-9]+$"

df_tile1 = df.filter(F.col("ResponseId").rlike(numeric_regex)).select(
    "ResponseId",
    "Country",

    # YearsCode: If numeric, cast to int. If NULL or Junk, make it 0.
    F.when(F.col("YearsCode").rlike(numeric_regex), F.col("YearsCode").cast("int"))
     .otherwise(0).alias("YearsCode"),

    # YearsCodePro: Same logic, Junk/NULL becomes 0.
    F.when(F.col("WorkExp").rlike(numeric_regex), F.col("WorkExp").cast("int"))
     .otherwise(0).alias("YearsCodePro"),

    # Salary: If it looks like a float, cast it. Otherwise, leave as NULL.
    F.when(F.col("ConvertedCompYearly").rlike(float_regex), F.col("ConvertedCompYearly").cast("float"))
     .otherwise(None).alias("Salary")
)


# In[ ]:


df_tech_raw = df.filter(F.col("ResponseId").rlike("^[0-9]+$")).select(
    "ResponseId",
    "DevType",
    "LanguageHaveWorkedWith",
    "DatabaseHaveWorkedWith"
)

df_tech_exploded = df_tech_raw.withColumn(
    "Language", F.explode(F.split(F.col("LanguageHaveWorkedWith"), ";"))
).filter(
    F.col("Language").isNotNull() & (F.col("Language") != "")
)

role_totals = df_tech_raw.filter(F.col("DevType").isNotNull()) \
    .groupBy("DevType") \
    .agg(F.countDistinct("ResponseId").alias("TotalDevsInRole"))

tech_counts = df_tech_exploded.filter(F.col("DevType").isNotNull()) \
    .groupBy("DevType", "Language") \
    .agg(F.countDistinct("ResponseId").alias("TechUsers"))

df_market_share = tech_counts.join(role_totals, "DevType") \
    .withColumn("MarketSharePct", (F.col("TechUsers") / F.col("TotalDevsInRole")) * 100) \
    .select(
        "DevType",
        "Language",
        F.round("MarketSharePct", 2).alias("MarketSharePct"),
        "TechUsers"
    ).orderBy("DevType", F.desc("MarketSharePct"))


# In[ ]:




