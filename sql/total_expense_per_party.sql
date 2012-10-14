SELECT 
  SUM(public.political_expense.sum),
  COUNT(public.political_candidate.id),
  public.political_party.name 
FROM 
  public.political_party, 
  public.political_candidate, 
  public.political_expense
WHERE 
  political_candidate.party_id = political_party.id AND
  political_expense.candidate_id = political_candidate.id AND
  political_expense.expense_type_id = 7
GROUP BY
  public.political_party.id;
