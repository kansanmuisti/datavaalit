SELECT * 
FROM political_candidate, political_person, geo_municipality
WHERE political_candidate.person_id = political_person.id
  AND geo_municipality.name = 'Hankasalmi'
  AND political_person.last_name = 'Makkonen';