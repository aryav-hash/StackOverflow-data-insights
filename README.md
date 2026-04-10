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

---

## ✨ Features & Details of the project
 The data pipeline is based on batch processing using **ELT (Extract-Load-Transform) workflow**.

 ### Phase-1: IaC
 The data lake (Google Cloud Storage) was setup for the project. The resources accessed through Terraform are the Google Cloud Storage Bucket named **"airport-dashboard-492216"** and two datasets were made inside this bucket on the BigQuery, named stackoverflow_stg and analytics. The stackoverflow_stg dataset, as the name suggests is for the staging tables that contain the raw data inside of them, and the analytics dataset contains the final tables which would be used in dbt to make the respective models for the charts.

 > The name airport-dashboard is not a suitable name for a bucket used in this project. The project was going to be about an  airport dashboard initially which is why it was named that way however, I dropped that idea and adopted this one.

 ### Phase-2: Workflow Orchestration
 Kestra was used to create a flow named **upload_to_gcs.yml** that can put the respective data files we need for the project onto the bucket. The flow consists of installing the data in the form of a .csv file from stackoverflow's website and then uploading it onto the Google Cloud Bucket. The flow is only concerned with the stackoverflow's 2025 survey data, but it can be tweaked to upload the data of the previous years as well.

 ### Phase-3: Spark Transformations
 After the upload of data to the bucket, we connect spark directly to the data stored in the bucket so that we can access the data and perform the relevant transformations. We connect to the data kept in the bucket in the same way as shown in the zoomcamp course. Spark was used to write two notebooks, the first one is the testing.ipynb kept in the spark/notebooks directory. Here, the data was explored and a smaller dataframe (around 1000) was used to test the transformations we wanted to do to the data.

 For the first chart we extracted the ResponseId, DevType, LanguageHaveWorkedWith and DatabaseHaveWorkedWith columns. We exploded on the LanguagesHaveWorkedWithColumn since the data contained in that column had languages picked by the user separated from one another using semicolons. By **exploding**, that individual row got converted into multiple rows based on the number of languages selected by the surveyor. Each row now only has one language. We then calculate the column which contains the total number of distinct responses that we got from each DevType as TotalDevsInRole and the column named TechUsers which calculates for each DevType, and language, what is the total number of users for that language in that DevType. These tasks were done through the help of **grouping ( DevType ) and ( DevType, Language )** respectively.

 For the second chart we extracted the ResponseId, Country, YearsCode, YearsCodePro, WorkExp, and ConvertedCompYearly columns. The script made sure that all the records that contained NULL or Junk values were changed to 0. Typecasting was also done to the columns.

 After the testing, a production script was written with the logic explored in the testing script.

 ### Phase-4: Building the staging tables
 The production script was used to generate the staging tables using the **Dataproc Serverless Cluster** in Google Cloud. Kestra automated this by executing another flow contained in **script_execution.yml** file. The production_script was made into a python script and then uploaded to the cloud for execution.
 
## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Docker

### Installation
1. Clone the repo:
   ```bash
   git clone [https://github.com/username/project.git](https://github.com/username/project.git)