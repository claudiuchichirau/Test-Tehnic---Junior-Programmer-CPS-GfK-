SELECT p.Locatie, CONCAT(p.First_Name, ' ', p.Last_Name) AS Full_Name, v.quality, COUNT(*) AS Total_Votes
FROM persons p
JOIN votes v ON p.ID = v.chosen_person
WHERE v.valid = 1  
GROUP BY p.Locatie, CONCAT(p.First_Name, ' ', p.Last_Name), v.quality  
ORDER BY p.Locatie, CONCAT(p.First_Name, ' ', p.Last_Name);  
