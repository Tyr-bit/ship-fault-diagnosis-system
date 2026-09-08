MATCH (n) RETURN count(n) AS node_count;
MATCH ()-[r]->() RETURN count(r) AS rel_count;

MATCH p=(s:Symptom)-[:HAS_EQUIPMENT]->(e:Equipment)-[:BELONGS_TO]->(sys:System)
RETURN p LIMIT 30;

MATCH p=(s:Symptom)-[:HAS_CAUSE]->(c:Cause)-[:HAS_REPAIR]->(r:Repair)
RETURN p LIMIT 30;

MATCH p=(s:Symptom)-[:HAS_CAUSE]->(c:Cause)-[:HAS_DIAGNOSIS]->(d:Diagnosis)
RETURN p LIMIT 30;

MATCH (n:MaintenanceCase) RETURN n LIMIT 20;