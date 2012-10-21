SELECT 
  SUM(political_expense.sum),
  COUNT(political_candidate.id),
  political_party.name 
FROM 
  political_party, 
  political_candidate, 
  political_expense
WHERE 
  political_candidate.party_id = political_party.id AND
  political_expense.candidate_id = political_candidate.id AND
  political_expense.id = 1
GROUP BY
  public.political_party.id;
