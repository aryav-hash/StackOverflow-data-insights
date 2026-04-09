import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

def main():
    spark = SparkSession.builder\
            .appName("StackOverflow_Production_Pipeline")\
            .getOrCreate()
    
    if len(sys.argv) < 3:
        sys.exit(1)

    bucket_name=sys.argv[1]
    year = sys.argv[2]

    input_path =f"gs://{bucket_name}/raw/survey/{year}/results.csv"
    temp_gcs_bucket = f"{bucket_name}/temp_spark"

    df = spark.read.csv(input_path, header=True, inferSchema=True)

    numeric_regex = "^[0-9]+$"
    float_regex = r"^[0-9]*\.?[0-9]+$"

    df_tile1 = df.filter(F.col("ResponseId").rlike(numeric_regex)).select(
        "ResponseId",
        "Country",

        F.when(F.col("YearsCode").rlike(numeric_regex), F.col("YearsCode").cast("int"))
        .otherwise(0).alias("YearsCode"),

        F.when(F.col("WorkExp").rlike(numeric_regex), F.col("WorkExp").cast("int"))
        .otherwise(0).alias("YearsCodePro"),

        F.when(F.col("ConvertedCompYearly").rlike(float_regex), F.col("ConvertedCompYearly").cast("float"))
        .otherwise(None).alias("Salary")
    )

    df_tech_raw = df.filter(F.col("ResponseId").rlike(numeric_regex)).select(
        "ResponseId",
        "DevType",
        "LanguageHaveWorkedWith",
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

    df_tile1.write\
            .format("bigquery")\
            .option("temporaryGcsBucket", temp_gcs_bucket)\
            .option("table", f"stackoverflow_stg.stg_salary_exp_{year}")\
            .mode("overwrite")\
            .save()

    df_market_share.write\
                .format("bigquery")\
                .option("temporaryGcsBucket", temp_gcs_bucket)\
                .option("table", f"stackoverflow_stg.stg_market_share_{year}")\
                .mode("overwrite")\
                .save()

if __name__ == "__main__":
    main()