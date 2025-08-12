-- Stage 1: Extract Key Facility Metrics
-- Extract: facility_id, facility_name, employee_count, number_of_offered_services, and expiry_date_of_first_accreditation

SELECT 
  facility_id,
  facility_name,
  employee_count,
  cardinality(services) AS number_of_offered_services,
  -- Get the earliest (first) accreditation expiry date
  (
    SELECT MIN(date(accred.valid_until))
    FROM UNNEST(accreditations) AS t(accred)
  ) AS expiry_date_of_first_accreditation
FROM healthcare_facilities
ORDER BY facility_name;
