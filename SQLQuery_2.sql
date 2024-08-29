SELECT p.Locatie AS Country, COUNT(v.ID) AS Total_Votes
FROM persons p
LEFT JOIN  votes v ON p.ID = v.chosen_person AND v.valid = 1
GROUP BY p.Locatie
ORDER BY p.Locatie;
