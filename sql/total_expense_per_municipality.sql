SELECT 
  SUM(political_expense.sum), 
  COUNT(political_expense.candidate_id) AS candidates,
  geo_municipality.name
FROM 
  public.political_expense, 
  public.political_candidate, 
  public.geo_municipality, 
  public.political_person
WHERE 
  political_expense.candidate_id = political_candidate.id AND
  political_candidate.municipality_id = geo_municipality.id AND
  political_candidate.person_id = political_person.id AND
  political_expense.expense_type_id = 7
GROUP BY  
  geo_municipality.id;