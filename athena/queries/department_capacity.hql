-- Stage 3: Count Accredited Facilities Per State
-- Execute Athena query to count accredited facilities per state

SELECT 
  location.state,
  COUNT(*) AS accredited_facilities_count
FROM healthcare_facilities
WHERE cardinality(accreditations) > 0
GROUP BY location.state
ORDER BY accredited_facilities_count DESC;
