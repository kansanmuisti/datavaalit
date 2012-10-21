SELECT 
  public.political_party.name AS Puolue,
  public.political_party.code AS Lyhenne,
  COUNT(public.political_candidate.id) AS Ehdokkaiden_lkm 
FROM 
  public.political_party, 
  public.political_candidate
WHERE 
  political_candidate.party_id = political_party.id
GROUP BY
  public.political_party.id
ORDER BY
  public.political_party.name;