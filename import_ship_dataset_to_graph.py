import json
import requests
from pathlib import Path

A_GRAPH_UPDATE_URL = "http://127.0.0.1:5001/graph/update"
DATA_FILE = r"D:\serviceo\A\data\ship_fault_dataset_150.json"


def safe_text(v, default=""):
    if v is None:
        return default
    return str(v).strip()


def safe_list(v):
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    if isinstance(v, str) and v.strip():
        return [v.strip()]
    return []


def build_payload_from_record(record: dict):
    record_id = safe_text(record.get("record_id"))
    equipment = safe_text(record.get("equipment_type"))
    subsystem = safe_text(record.get("subsystem"))
    component = safe_text(record.get("fault_name"))  # 用 fault_name 作为 component
    symptom = safe_text(record.get("symptom"))
    root_cause = safe_text(record.get("possible_cause"))
    solution = safe_text(record.get("repair_solution"))

    diagnosis_method = safe_text(record.get("diagnosis_method"))
    symptom_detail = safe_text(record.get("symptom_detail"))
    cause_category = safe_text(record.get("cause_category"))
    trigger_condition = safe_text(record.get("trigger_condition"))
    expected_result = safe_text(record.get("expected_result"))
    data_source = safe_text(record.get("data_source"))

    tools = safe_list(record.get("required_tools"))
    parts = safe_list(record.get("required_parts"))
    keywords = safe_list(record.get("keywords"))

    risk_level = safe_text(record.get("severity_level"))
    warning = safe_text(record.get("safety_warning"))
    confidence = float(record.get("confidence", 0.9))

    # 组织图谱关系
    graph_updates = [
        {
            "start_node": {"label": "Equipment", "name": equipment},
            "relationship": "HAS_SUBSYSTEM",
            "end_node": {"label": "Subsystem", "name": subsystem},
            "properties": {
                "detail": f"record_id={record_id}",
                "weight_increment": 1
            }
        },
        {
            "start_node": {"label": "Subsystem", "name": subsystem},
            "relationship": "HAS_COMPONENT",
            "end_node": {"label": "Component", "name": component},
            "properties": {
                "detail": f"fault_name映射为component; record_id={record_id}",
                "weight_increment": 1
            }
        },
        {
            "start_node": {"label": "Component", "name": component},
            "relationship": "HAS_SYMPTOM",
            "end_node": {"label": "Symptom", "name": symptom},
            "properties": {
                "detail": symptom_detail,
                "weight_increment": 1
            }
        },
        {
            "start_node": {"label": "Symptom", "name": symptom},
            "relationship": "CAUSED_BY",
            "end_node": {"label": "Reason", "name": root_cause},
            "properties": {
                "detail": f"cause_category={cause_category}; diagnosis={diagnosis_method}",
                "weight_increment": 1
            }
        },
        {
            "start_node": {"label": "Reason", "name": root_cause},
            "relationship": "REPAIRED_BY",
            "end_node": {"label": "Solution", "name": solution},
            "properties": {
                "detail": f"expected_result={expected_result}",
                "weight_increment": 1
            }
        },

        # MaintenanceCase 与核心节点关联
        {
            "start_node": {"label": "MaintenanceCase", "name": record_id},
            "relationship": "INSTANCE_OF",
            "end_node": {"label": "Symptom", "name": symptom},
            "properties": {
                "detail": f"source={data_source}",
                "weight_increment": 1
            }
        },
        {
            "start_node": {"label": "MaintenanceCase", "name": record_id},
            "relationship": "CONFIRMED_REASON",
            "end_node": {"label": "Reason", "name": root_cause},
            "properties": {
                "detail": "",
                "weight_increment": 1
            }
        },
        {
            "start_node": {"label": "MaintenanceCase", "name": record_id},
            "relationship": "USED_SOLUTION",
            "end_node": {"label": "Solution", "name": solution},
            "properties": {
                "detail": "",
                "weight_increment": 1
            }
        },
        {
            "start_node": {"label": "MaintenanceCase", "name": record_id},
            "relationship": "RELATED_COMPONENT",
            "end_node": {"label": "Component", "name": component},
            "properties": {
                "detail": "",
                "weight_increment": 1
            }
        },
    ]

    # 工具
    for tool in tools:
        graph_updates.append({
            "start_node": {"label": "Solution", "name": solution},
            "relationship": "USE_TOOL",
            "end_node": {"label": "Tool", "name": tool},
            "properties": {
                "detail": f"record_id={record_id}",
                "weight_increment": 1
            }
        })

    # 零部件
    for part in parts:
        graph_updates.append({
            "start_node": {"label": "Solution", "name": solution},
            "relationship": "REPLACE_PART",
            "end_node": {"label": "Part", "name": part},
            "properties": {
                "detail": f"record_id={record_id}",
                "weight_increment": 1
            }
        })

    # 风险等级
    if risk_level:
        graph_updates.append({
            "start_node": {"label": "Symptom", "name": symptom},
            "relationship": "HAS_RISK_LEVEL",
            "end_node": {"label": "RiskLevel", "name": risk_level},
            "properties": {
                "detail": f"record_id={record_id}",
                "weight_increment": 1
            }
        })

    # 安全警示
    if warning:
        graph_updates.append({
            "start_node": {"label": "Solution", "name": solution},
            "relationship": "HAS_WARNING",
            "end_node": {"label": "Warning", "name": warning},
            "properties": {
                "detail": f"record_id={record_id}",
                "weight_increment": 1
            }
        })

    # 关键词
    for kw in keywords:
        graph_updates.append({
            "start_node": {"label": "Symptom", "name": symptom},
            "relationship": "HAS_KEYWORD",
            "end_node": {"label": "Keyword", "name": kw},
            "properties": {
                "detail": f"record_id={record_id}",
                "weight_increment": 1
            }
        })
        graph_updates.append({
            "start_node": {"label": "Reason", "name": root_cause},
            "relationship": "HAS_KEYWORD",
            "end_node": {"label": "Keyword", "name": kw},
            "properties": {
                "detail": f"record_id={record_id}",
                "weight_increment": 1
            }
        })
        graph_updates.append({
            "start_node": {"label": "Solution", "name": solution},
            "relationship": "HAS_KEYWORD",
            "end_node": {"label": "Keyword", "name": kw},
            "properties": {
                "detail": f"record_id={record_id}",
                "weight_increment": 1
            }
        })

    payload = {
        "meta": {
            "session_id": record_id,
            "timestamp": "2026-03-13 14:00:00",
            "source": data_source or "ship_fault_dataset_150"
        },
        "knowledge_content": {
            "symptom": symptom,
            "component": component,
            "root_cause": root_cause,
            "solution": solution,
            "confidence_score": confidence
        },
        "graph_updates": graph_updates
    }

    return payload


def main():
    data_path = Path(DATA_FILE)
    if not data_path.exists():
        print(f"数据文件不存在: {DATA_FILE}")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    success_count = 0
    fail_count = 0

    for idx, record in enumerate(records, start=1):
        try:
            payload = build_payload_from_record(record)
            resp = requests.post(A_GRAPH_UPDATE_URL, json=payload, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            print(f"[{idx}] 导入成功: {record.get('record_id')} -> {result}")
            success_count += 1
        except Exception as e:
            print(f"[{idx}] 导入失败: {record.get('record_id')} -> {e}")
            fail_count += 1

    print("=" * 60)
    print(f"总数: {len(records)}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")


if __name__ == "__main__":
    main()
