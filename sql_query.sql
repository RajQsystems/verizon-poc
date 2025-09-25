SELECT fuze_project_id,
       site_name,
       'Real Estate Released' AS milestone,
       real_estate_released_f AS forecast_date
FROM projects_encoded
WHERE real_estate_released_f IS NOT NULL
  AND real_estate_released_f BETWEEN '2025-10-01' AND '2025-12-31'
UNION ALL
SELECT fuze_project_id,
       site_name,
       'Construction Awarded' AS milestone,
       construction_awarded_f AS forecast_date
FROM projects_encoded
WHERE construction_awarded_f IS NOT NULL
  AND construction_awarded_f BETWEEN '2025-10-01' AND '2025-12-31'
UNION ALL
SELECT fuze_project_id,
       site_name,
       'Construction Started' AS milestone,
       construction_started_f AS forecast_date
FROM projects_encoded
WHERE construction_started_f IS NOT NULL
  AND construction_started_f BETWEEN '2025-10-01' AND '2025-12-31'
UNION ALL
SELECT fuze_project_id,
       site_name,
       'Physical Construction Completed' AS milestone,
       physical_construction_completed_f AS forecast_date
FROM projects_encoded
WHERE physical_construction_completed_f IS NOT NULL
  AND physical_construction_completed_f BETWEEN '2025-10-01' AND '2025-12-31'
UNION ALL
SELECT fuze_project_id,
       site_name,
       'Inservice Activation' AS milestone,
       inservice_activation_f AS forecast_date
FROM projects_encoded
WHERE inservice_activation_f IS NOT NULL
  AND inservice_activation_f BETWEEN '2025-10-01' AND '2025-12-31'
ORDER BY forecast_date ASC;