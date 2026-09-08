# src/graph_neo4j.py
import os
from neo4j import GraphDatabase

# =========================
# Neo4j 连接配置
# =========================
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = os.environ.get("NEO4J_PASSWORD", "")  # 通过环境变量注入，勿提交真实密码

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    return _driver

# =========================
# 允许的节点和关系类型
# =========================
ALLOWED_LABELS = {
    "Symptom", "Equipment", "System", "Cause", "Repair", "Diagnosis", "MaintenanceCase"
}
ALLOWED_RELATIONSHIPS = {
    "HAS_EQUIPMENT", "BELONGS_TO", "HAS_CAUSE", "HAS_REPAIR", "HAS_DIAGNOSIS",
    "INSTANCE_OF", "CONFIRMED_CAUSE", "USED_REPAIR"
}

# =========================
# 基础执行函数
# =========================
def run_cypher(tx, cypher, params=None):
    tx.run(cypher, params or {})

def validate_graph_update(update: dict):
    if update.get("action") != "MERGE":
        raise ValueError("Only MERGE action is allowed")
    start_node = update.get("start_node", {})
    end_node = update.get("end_node", {})
    relationship = update.get("relationship", "")
    start_label = start_node.get("label")
    end_label = end_node.get("label")
    start_name = start_node.get("name")
    end_name = end_node.get("name")
    if start_label not in ALLOWED_LABELS:
        raise ValueError(f"Invalid start label: {start_label}")
    if end_label not in ALLOWED_LABELS:
        raise ValueError(f"Invalid end label: {end_label}")
    if relationship not in ALLOWED_RELATIONSHIPS:
        raise ValueError(f"Invalid relationship: {relationship}")
    if not start_name or not end_name:
        raise ValueError("Node name cannot be empty")

def build_merge_relation_cypher(update: dict):
    validate_graph_update(update)
    start_label = update["start_node"]["label"]
    start_name = update["start_node"]["name"]
    end_label = update["end_node"]["label"]
    end_name = update["end_node"]["name"]
    rel_type = update["relationship"]
    props = update.get("properties", {})
    detail = props.get("detail", "")
    weight_increment = int(props.get("weight_increment", 0))

    cypher = f"""
    MERGE (a:{start_label} {{name: $start_name}})
    MERGE (b:{end_label} {{name: $end_name}})
    MERGE (a)-[r:{rel_type}]->(b)
    ON CREATE SET
        r.detail = $detail,
        r.weight = CASE WHEN $weight_increment > 0 THEN $weight_increment ELSE 1 END
    ON MATCH SET
        r.detail = CASE WHEN $detail <> '' THEN $detail ELSE r.detail END,
        r.weight = CASE
            WHEN $weight_increment > 0 THEN coalesce(r.weight, 1) + $weight_increment
            ELSE coalesce(r.weight, 1)
        END
    """
    params = {
        "start_name": start_name,
        "end_name": end_name,
        "detail": detail,
        "weight_increment": weight_increment
    }
    return cypher, params

def save_maintenance_case(tx, data: dict):
    meta = data["meta"]
    kc = data["knowledge_content"]
    cypher = """
    MERGE (mc:MaintenanceCase {session_id: $session_id})
    SET mc.timestamp = $timestamp,
        mc.source = $source,
        mc.symptom = $symptom,
        mc.equipment = $equipment,
        mc.system = $system,
        mc.root_cause = $root_cause,
        mc.repair = $repair,
        mc.diagnosis = $diagnosis,
        mc.confidence_score = $confidence_score
    """
    params = {
        "session_id": meta["session_id"],
        "timestamp": meta["timestamp"],
        "source": meta["source"],
        "symptom": kc["symptom"],
        "equipment": kc["equipment"],
        "system": kc["system"],
        "root_cause": kc["root_cause"],
        "repair": kc["repair"],
        "diagnosis": kc["diagnosis"],
        "confidence_score": kc["confidence_score"]
    }
    tx.run(cypher, params)

def link_maintenance_case(tx, data: dict):
    meta = data["meta"]
    kc = data["knowledge_content"]
    cypher = """
    MERGE (mc:MaintenanceCase {session_id: $session_id})
    MERGE (sym:Symptom {name: $symptom})
    MERGE (cau:Cause {name: $root_cause})
    MERGE (rep:Repair {name: $repair})
    MERGE (dia:Diagnosis {name: $diagnosis})
    MERGE (eq:Equipment {name: $equipment})
    MERGE (sys:System {name: $system})
    MERGE (mc)-[:INSTANCE_OF]->(sym)
    MERGE (mc)-[:CONFIRMED_CAUSE]->(cau)
    MERGE (mc)-[:USED_REPAIR]->(rep)
    MERGE (sym)-[:HAS_EQUIPMENT]->(eq)
    MERGE (eq)-[:BELONGS_TO]->(sys)
    MERGE (sym)-[:HAS_CAUSE]->(cau)
    MERGE (cau)-[:HAS_REPAIR]->(rep)
    MERGE (cau)-[:HAS_DIAGNOSIS]->(dia)
    """
    params = {
        "session_id": meta["session_id"],
        "symptom": kc["symptom"],
        "root_cause": kc["root_cause"],
        "repair": kc["repair"],
        "diagnosis": kc["diagnosis"],
        "equipment": kc["equipment"],
        "system": kc["system"]
    }
    tx.run(cypher, params)

def process_self_learning_data(data: dict) -> int:
    """处理自学习数据，写入图谱，返回更新的关系数量"""
    updates = data.get("graph_updates", [])
    with get_driver().session() as session:
        session.execute_write(save_maintenance_case, data)
        session.execute_write(link_maintenance_case, data)
        for update in updates:
            cypher, params = build_merge_relation_cypher(update)
            session.execute_write(run_cypher, cypher, params)
    return len(updates)

def query_graph(keywords: str) -> str:
    """
    根据关键词从Neo4j查询相关故障知识，返回格式化的文本。
    如果无结果，返回空字符串。
    """
    if not keywords.strip():
        return ""

    cypher = """
    MATCH (s:Symptom)
    WHERE s.name CONTAINS $kw
    OPTIONAL MATCH (s)-[:HAS_EQUIPMENT]->(e:Equipment)-[:BELONGS_TO]->(sys:System)
    OPTIONAL MATCH (s)-[:HAS_CAUSE]->(c:Cause)
    OPTIONAL MATCH (c)-[:HAS_DIAGNOSIS]->(d:Diagnosis)
    OPTIONAL MATCH (c)-[:HAS_REPAIR]->(r:Repair)
    RETURN s.name AS symptom,
           collect(DISTINCT e.name) AS equipment,
           collect(DISTINCT sys.name) AS system,
           collect(DISTINCT c.name) AS causes,
           collect(DISTINCT d.name) AS diagnoses,
           collect(DISTINCT r.name) AS repairs
    LIMIT 5
    """
    with get_driver().session() as session:
        result = session.run(cypher, {"kw": keywords})
        records = list(result)

    if not records:
        return ""

    lines = ["【知识图谱信息】"]
    for rec in records:
        lines.append(f"故障现象：{rec['symptom']}")
        if rec['equipment']:
            lines.append(f"相关设备：{', '.join(rec['equipment'])}")
        if rec['system']:
            lines.append(f"所属系统：{', '.join(rec['system'])}")
        if rec['causes']:
            lines.append(f"可能原因：{', '.join(rec['causes'])}")
        if rec['diagnoses']:
            lines.append(f"诊断方法：{', '.join(rec['diagnoses'])}")
        if rec['repairs']:
            lines.append(f"维修方案：{', '.join(rec['repairs'])}")
        lines.append("---")
    return "\n".join(lines)