-- Create external table for healthcare facilities JSON data in S3
-- This table allows querying JSON data directly from S3 using Athena

CREATE EXTERNAL TABLE healthcare_facilities (
  facility_id string,
  facility_name string,
  location struct<
    address: string,
    city: string,
    state: string,
    zip: string
  >,
  employee_count int,
  services array<string>,
  labs array<struct<
    lab_name: string,
    certifications: array<string>
  >>,
  accreditations array<struct<
    accreditation_body: string,
    accreditation_id: string,
    valid_until: string
  >>
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
STORED AS INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 's3://YOUR_BUCKET_NAME/healthcare-data/facilities/';
