SELECT political_person.first_name, political_person.last_name, 
       political_candidate.number, 
       political_candidate.municipality_id
FROM political_candidate, political_campaignbudget, political_person, political_campaignexpense
WHERE political_person.id = political_candidate.person_id
  AND political_candidate.id = political_campaignbudget.candidate_id;