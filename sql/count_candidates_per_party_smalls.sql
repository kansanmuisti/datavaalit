SELECT
  sekalainen.party_code AS Lyhenne,
  COUNT(sekalainen.id) AS Ehdokkaiden_lkm 
FROM
  (SELECT * FROM political_candidate WHERE party_id IS NULL) AS sekalainen
GROUP BY
  sekalainen.party_code
ORDER BY
  sekalainen.party_code;