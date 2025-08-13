# AWS Healthcare Data Pipeline Challenge

A complete serverless data pipeline for processing healthcare facility data and monitoring accreditation expirations using AWS services.

## 🏗️ Architecture Overview

This project implements a **4-stage automated data pipeline**:
- **Stage 1**: Data extraction with Athena (facility metrics)
- **Stage 2**: Data filtering with Athena (6-month expiring accreditations)  
- **Stage 3**: Event-driven processing with Lambda (notifications)
- **Stage 4**: Analytics with Athena (state-wise facility counts)

## 📁 Project Structure

```
AWS Challenge/
├── 📄 README.md                           # Project documentation
├── 📄 sample_healthcare_facility.json     # Test data (NDJSON format)
├── 📁 athena/
│   ├── 📁 queries/
│   │   ├── facility_summary.hql          # Stage 1: Extract facility metrics
│   │   ├── expiring_accreditations.hql   # Stage 2: Filter expiring accreditations
│   │   └── department_capacity.hql       # Stage 4: Count facilities by state
│   └── 📁 tables/
│       └── create_healthcare_facilities_table.hql
├── 📁 lambda/
│   ├── 📁 src/
│   │   └── healthcare_processor.py       # Main Lambda function
│   ├── requirements.txt                  # Python dependencies
│   ├── test-event.json                  # Test payload
│   └── trust-policy.json               # IAM trust policy
├── 📁 stepfunctions/
│   └── healthcare_pipeline.json         # Complete 4-stage workflow
├── 📁 iam/
│   ├── stepfunctions-execution-role-policy.json  # Step Functions permissions
│   └── stepfunctions-trust-policy.json           # Step Functions trust policy
└── 📁 infrastructure/
    └── healthcare-infrastructure.yaml    # CloudFormation template
```

## 🚀 Deployment Instructions

### Prerequisites
- AWS CLI configured with appropriate permissions
- AWS account with access to: S3, Athena, Lambda, Step Functions, SNS, IAM

### Step 1: S3 Setup
1. Create S3 bucket: `YOUR_BUCKET_NAME`
2. Upload `sample_healthcare_facility.json` to `s3://YOUR_BUCKET_NAME/healthcare-data/facilities/`

### Step 2: Athena Database Setup
1. Create database: `healthcare_db`
2. Run table creation script: `athena/tables/create_healthcare_facilities_table.hql`

### Step 3: Lambda Function
1. Create function: `healthcare-processor`
2. Upload code from: `lambda/src/healthcare_processor.py`
3. Set runtime: Python 3.9+
4. Configure IAM role with S3 and SNS permissions

### Step 4: SNS Topics
Create three topics:
- `healthcare-accreditation-critical`
- `healthcare-accreditation-high`  
- `healthcare-accreditation-medium`

### Step 5: Step Functions
1. Create IAM role using: `iam/stepfunctions-*-policy.json`
2. Create state machine using: `stepfunctions/healthcare_pipeline.json`
3. Update account ID (ACCOUNT_ID) with your AWS account ID

## 🧪 Testing

Execute the Step Functions state machine with empty input `{}` to run the complete pipeline.

**Expected Results:**
- ✅ Stage 1: Facility metrics extracted
- ✅ Stage 2: Expiring accreditations filtered (6-month window)
- ✅ Stage 3: Lambda processing and notifications (90-day window)
- ✅ Stage 4: State-wise facility counts generated
- ✅ Results copied to S3 production folder
- ✅ SNS success notification sent

## 📊 Monitoring

The pipeline includes comprehensive monitoring:
- **CloudWatch Logs**: Lambda function execution logs
- **Step Functions**: Visual workflow monitoring  
- **SNS Notifications**: Multi-tier alert system
- **Athena**: Query execution metrics

## 🛠️ AWS Services Used

- **S3**: Data storage (NDJSON format)
- **Athena**: SQL analytics and data extraction
- **Lambda**: Serverless data processing
- **Step Functions**: Workflow orchestration
- **SNS**: Notification system
- **IAM**: Security and permissions
- **CloudWatch**: Monitoring and logging

## 🎯 Key Features

- **Multi-stage pipeline**: 4 distinct processing stages
- **Event-driven architecture**: Automated triggers and notifications
- **Error handling**: Retry logic and failure notifications
- **Scalable design**: Serverless and fully managed services
- **Cost-effective**: Pay-per-use AWS services
- **Monitoring**: Comprehensive logging and alerting

## 📈 Business Value

- **Proactive monitoring**: 90-day advance notice of expiring accreditations
- **Risk management**: Critical/High/Medium priority classification
- **Analytics insights**: State-wide facility distribution analysis
- **Automation**: Reduced manual monitoring overhead
- **Compliance**: Ensures accreditation renewals are tracked

---

**Built for AWS Data Engineering Challenge - Complete serverless healthcare data pipeline** 🏥⚡
