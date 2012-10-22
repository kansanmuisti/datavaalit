SELECT 
  parties.candidates AS total_candidates,
  COUNT(prebudgets.candidate_id) AS filed_prebudgets,
  political_party.name AS party,
  CAST(COUNT(prebudgets.candidate_id) AS FLOAT) / CAST(parties.candidates AS FLOAT) AS percent
FROM 
  (SELECT 
     DISTINCT(political_campaignbudget.candidate_id) AS candidate_id 
   FROM political_campaignbudget) AS prebudgets,
  (SELECT 
     COUNT(political_candidate.id) AS candidates, 
     political_candidate.party_id AS party_id
   FROM 
     political_candidate 
   GROUP BY 
     political_candidate.party_id) AS parties,
  political_candidate,
  political_party
WHERE
  prebudgets.candidate_id = political_candidate.id AND
  parties.party_id = political_candidate.party_id AND
  political_candidate.party_id = political_party.id
GROUP BY
  political_candidate.party_id,
  parties.candidates,
  political_party.name;
  