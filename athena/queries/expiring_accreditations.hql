-- Stage 2: Filter Facilities with Accreditations Expiring Within 6 Months
-- Filter facilities with any accreditation expiring within 6 months

SELECT DISTINCT
  facility_id,
  facility_name,
  location,
  employee_count,
  services,
  labs,
  accreditations
FROM healthcare_facilities
CROSS JOIN UNNEST(accreditations) AS t(accred)
WHERE date(accred.valid_until) BETWEEN current_date AND date_add('month', 6, current_date)
ORDER BY facility_name;
