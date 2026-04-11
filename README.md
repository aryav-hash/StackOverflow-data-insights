# StackOverflow-survey-insights

Every year StackOverflow takes a survey from it's users to gather data about the technical job market and the recent trends seen in that particular year. This project focuses on using the survey data of the year 2025 to generate charts on the following :-

### 1. Market Share of a Technology:
 Experts use various kinds of technologies to work in their domain. This metric discovers what are the most popular tools/languages being used by industry experts based on the number of respondents using that particular technology, divided by the total number of respondents of that domain.

 **Market Share = Respondents using that technology / Total number of respondents**

 The above metric is used to display a bar chart to show the popularity of that technology. Here the chart is only concerned with different programming languages.

### 2. Global Compensation Benchmarks
An exploration of average yearly compensation ($USD$) mapped against professional experience across different geographic regions. Experience is clustered into four distinct career stages:

| Experience (Years) | Career Level |
| :--- | :--- |
| **0 – 2** | Junior |
| **3 – 5** | Mid-Level |
| **6 – 10** | Senior |
| **10 – 12** | Lead / Principal |

The dataset for the project is available at [StackOverflow](https://survey.stackoverflow.co/).

---

## 🛠️ Tech Stack & Architecture

The project implements a robust data pipeline to handle the complexities of survey data:

* **Orchestration:** [Kestra](https://kestra.io/) (Pipeline management)
* **Processing:** [PySpark](https://spark.apache.org/docs/latest/api/python/index.html) (Data cleaning & flattening multi-value columns)
* **Data Warehouse:** [Google BigQuery](https://cloud.google.com/bigquery)
* **Transformation:** [dbt](https://www.getdbt.com/) (Modular SQL modeling and documentation)
* **Visualization:** [Looker Studio](https://lookerstudio.google.com/)
* **Infrastructure as Code:** [Terraform](https://www.terraform.io/)
* **Containerization:** [Docker](https://www.docker.com/)

 ![alt text](<screenshots/medallion.png>)

---

## 🔬 Key Features

* **Distributed Processing:** High-performance data cleaning and schema normalization (string-splitting and exploding) using **PySpark** on **Google Cloud Dataproc**.
* **Cloud Data Warehousing:** Structured, managed storage in **Google Cloud BigQuery** with optimized **Clustering** to minimize query latency and costs.
* **Analytics Engineering:** A robust, layered data modeling architecture (**Bronze ➔ Silver ➔ Gold**) implemented via **dbt Core**, ensuring data lineage and reliability.
* **Orchestration & Automation:** Full lifecycle management of ephemeral cloud infrastructure using **Kestra**, allowing for cost-effective, event-driven pipeline execution.
* **Strategic Insights UI:** Interactive **Looker Studio** command center featuring role-specific tech market share analysis and regional salary benchmarking.
* **Quality Assurance:** Integrated data hardening using **dbt Tests** and custom SQL logic to identify and neutralize outliers and non-standard 'NA' values.

---

## ✨ Details of the project
 The data pipeline is based on batch processing using **ELT (Extract-Load-Transform) workflow**.

 ### Phase-1: IaC
 The data lake (Google Cloud Storage) was setup for the project. The resources accessed through Terraform are the Google Cloud Storage Bucket named **"airport-dashboard-492216"** and two datasets were made inside this bucket on the BigQuery, named StackOverflow_stg and analytics. The StackOverflow_stg dataset, as the name suggests is for the staging tables that contain the raw data inside of them, and the analytics dataset contains the final tables which would be used in dbt to make the respective models for the charts.

 > The name airport-dashboard is not a suitable name for a bucket used in this project. The project was going to be about an  airport dashboard initially which is why it was named that way however, I dropped that idea and adopted this one.

 ### Phase-2: Workflow Orchestration
 Kestra was used to create a flow named **upload_to_gcs.yml** that can put the respective data files we need for the project onto the bucket. The flow consists of installing the data in the form of a .csv file from StackOverflow's website and then uploading it onto the Google Cloud Bucket. The flow is only concerned with the StackOverflow's 2025 survey data, but it can be tweaked to upload the data of the previous years as well.

 ![alt text](<screenshots/kestraflow.png>)

 ![alt text](<screenshots/kestradashboard.png>)

 ### Phase-3: Spark Transformations
 After the upload of data to the bucket, we connect spark directly to the data stored in the bucket so that we can access the data and perform the relevant transformations. We connect to the data kept in the bucket in the same way as shown in the zoomcamp course. Spark was used to write two notebooks, the first one is the testing.ipynb kept in the spark/notebooks directory. Here, the data was explored and a smaller dataframe (around 1000) was used to test the transformations we wanted to do to the data.

 For the first chart we extracted the ResponseId, DevType, LanguageHaveWorkedWith and DatabaseHaveWorkedWith columns. We exploded on the LanguagesHaveWorkedWithColumn since the data contained in that column had languages picked by the user separated from one another using semicolons. By **exploding**, that individual row got converted into multiple rows based on the number of languages selected by the surveyor. Each row now only has one language. We then calculate the column which contains the total number of distinct responses that we got from each DevType as TotalDevsInRole and the column named TechUsers which calculates for each DevType, and language, what is the total number of users for that language in that DevType. These tasks were done through the help of **grouping ( DevType ) and ( DevType, Language )** respectively.

 For the second chart we extracted the ResponseId, Country, YearsCode, YearsCodePro, WorkExp, and ConvertedCompYearly columns. The script made sure that all the records that contained NULL or Junk values were changed to 0. Typecasting was also done to the columns.

 After the testing, a production script was written with the logic explored in the testing script.

 ### Phase-4: Building the staging tables
 The production script was used to generate the staging tables using the **Dataproc Serverless Cluster** in Google Cloud. Kestra automated this by executing another flow contained in **script_execution.yml** file. The production_script was made into a python script and then uploaded to the cloud for execution. There are various benefits of using the Dataproc Serverless Cluster on GCP. The storage and compute are separated in the Google Cloud which is better than a local cluster where the data lives on the same compute nodes. The cluster is ephemeral, meaning that it doesn't run 24/7 instead it only runs for the time when we need to do computation and then it shuts down. In order to use this service, we need to setup a service account with the relevant permissions. These were configured using the **gcloud CLI**.

 ![alt text](<screenshots/accountpermissions.png>)

 ### Phase-5: Using DBT to build the models
 After the execution of the script, we got two staging tables in our BigQuery named **stg_market_share_2025** and **stg_salary_exp_2025**. DBT CLI was used to connect to the BigQuery instance and in our models (dbt/analytics/models/staging) we wrote two models named stg_market_share.sql and stg_salary_exp.sql which contains tables that we planned through our script in phase-3. Using these we made the fct_salary_benchmark.sql and fct_tech_market_share.sql marts. In fct_salary_benchmark.sql we selected the records that had salary greater than $500 and also classified different experience groups based on the number of years the person had worked in the industry. Here the data was clustered by experience level and country. In fct_tech_market_share.sql we clustered the data by developer role and selected all the columns.
 By running **dbt build** we were able to get the specific models in the analytics dataset of our GCP.
 
 ![alt text](<screenshots/dbtgraph.png>)

 ### Phase-6: Building the charts in Looker Studio
 Since the analytics data had been setup, we went ahead and connected it to the Looker Studio of Google Cloud. Here after importing the data for representation two charts were made. The first chart made our of fct_tech_market share.sql is a column based bar chart that explores the market share of different languages for different roles in the industry. The second chart is a heatmap that shows the median salary for different experience groups of developers in different countries.
 
 **Tile1**
 ![alt text](<screenshots/tile1.png>)
 
 **Tile2**
 ![alt text](<screenshots/tile2.png>)

## 🛠️ Setup & Deployment Guide

Follow these steps to replicate the environment and execute the pipeline from scratch.

## 🔐 Environment Management

This project utilizes `.env` and `.envrc` files to securely manage credentials and automate environment configuration.

### Environment Variables (`.env`)
Create a `.env` file in the root directory to store sensitive configuration. This file is used by Python scripts and the dbt wrapper to authenticate with GCP.

**Example `.env` template:**
```text
GCP_PROJECT_ID=your-project-id-here
GCP_REGION=us-central1
GCP_KEYFILE_PATH=/absolute/path/to/service-account-key.json
DBT_PROFILES_DIR=./  # Optional: point dbt to a local profile
```

There are several key-value pairs written for kestra as well. Look for the variables inside of the code and do the setup accordingly.
For environment variable use **direnv**:

### 1. Prerequisites
* **Python 3.12+** (Managed via `uv`)
* **Google Cloud CLI (gcloud)** authenticated to your account.
* **A Google Cloud Project** with billing enabled.

### 2. Infrastructure & Permissions Setup
Run the following commands in your terminal to configure the necessary GCP resources and Service Account permissions.

#### A. APIs, Service accounts/roles, and credentials
```bash
   gcloud services enable \
      storage-component.googleapis.com \
      bigquery.googleapis.com \
      dataproc.googleapis.com
      
   # Create the Service Account
   gcloud iam service-accounts create stackoverflow-loader --display-name="Stack Overflow Data Loader"

   # Assign BigQuery Admin (For dbt and table creation)
   gcloud projects add-iam-policy-binding [PROJECT_ID] \
      --member="serviceAccount:stackoverflow-loader@[PROJECT_ID].iam.gserviceaccount.com" \
      --role="roles/bigquery.admin"

   # Assign Storage Admin (For GCS access)
   gcloud projects add-iam-policy-binding [PROJECT_ID] \
      --member="serviceAccount:stackoverflow-loader@[PROJECT_ID].iam.gserviceaccount.com" \
      --role="roles/storage.admin"

   # Assign Dataproc Editor (For Spark job execution)
   gcloud projects add-iam-policy-binding [PROJECT_ID] \
      --member="serviceAccount:stackoverflow-loader@[PROJECT_ID].iam.gserviceaccount.com" \
      --role="roles/dataproc.editor"

   gcloud iam service-accounts keys create keys/service-account-key.json \
      --iam-account=stackoverflow-loader@[PROJECT_ID].iam.gserviceaccount.com
```
The project uses UV for fast, reproducible dependency management :-

```` bash
   # Install dependencies
      uv sync

   # Activate virtual environment
      source .venv/bin/activate
````


#### B. Setting dbt profile config
dbt requires a profiles.yml file to connect to BigQuery. For reproducibility, create this file at ~/.dbt/profiles.yml:
``` bash
   stackoverflow_analytics:
   outputs:
      dev:
         type: bigquery
         method: service-account
         project: [PROJECT_ID]
         dataset: analytics
         threads: 4
         keyfile: /path/to/your/keys/service-account-key.json
         location: us-central1 # Ensure this matches your BQ dataset location
         priority: interactive
   target: dev
```

#### C. Execution
**Raw Ingestion:** Upload the survey CSV to your GCS bucket. The kestra flows have been provided in the kestra directory.

**Spark Transformation:** Submit the PySpark job to Dataproc (or run via the Kestra orchestrator) to populate the stackoverflow_stg dataset.

**dbt Modeling:**
``` bash
   # Verify connection
   dbt debug

   # Run and test all models
   dbt build
```

#### D. Connecting Looker Studio

To visualize the data, follow these steps to connect your BigQuery Marts:

1. Open Looker Studio and create a New Report.

2. Select BigQuery as the Data Source.

3. Choose My Projects > [PROJECT_ID] > analytics > fct_tech_market_share.
Ensure the MarketSharePct field is set to a "Percent" type and use Median for salary metrics to avoid outlier skewing.