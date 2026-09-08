# =========================================================
# 抑制 transformers 库的弃用警告（必须在导入任何模块之前）
# =========================================================
import warnings
import logging
import os

# 禁用 transformers 的 logging 输出
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

# 设置 logging 级别
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

# 禁用 warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", message=".*Accessing `__path__`.*")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

import streamlit as st
import time
import pandas as pd
import os
from database import (
    init_db,
    log_operation,
    get_all_logs,
    save_fault_record,
    get_all_fault_records,
    save_chat_session,
    get_all_chat_sessions,
    get_chat_session_by_id,
    update_chat_session_report,
    convert_session_row,
    convert_session_rows, delete_chat_session
)
import markdown
import uuid
import re
import json
from PIL import Image
import io
import speech_recognition as sr
import streamlit.components.v1 as components
from graph_chat import chat_with_expert_multi_turn
from datetime import datetime, timezone, timedelta
from kg_client import push_to_knowledge_graph
import requests
import textwrap
import tempfile
import sys
import base64
import plotly.express as px
import plotly.graph_objects as go
from neo4j import GraphDatabase
from streamlit_agraph import agraph, Node, Edge, Config
# 动态路径：支持 D:\serviceo (源码) 和 D:\serviceo_e (打包) 两种部署方式
_SERVICEO_ROOT = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(_SERVICEO_ROOT) == "app":
    _SERVICEO_ROOT = os.path.dirname(_SERVICEO_ROOT)
B_PROJECT_ROOT = os.path.join(_SERVICEO_ROOT, "B", "HAI")
if B_PROJECT_ROOT not in sys.path:
    sys.path.insert(0, B_PROJECT_ROOT)

try:
    from src.main_rag import retrieve_info
except (ImportError, ModuleNotFoundError):
    # RAG 模块由团队其他成员维护，未包含在本仓库中；
    # 缺少时降级为空上下文，不影响前端主体功能。
    def retrieve_info(text="", audio_bytes=None, image_bytes=None, **kwargs):
        return "", []


# =========================
# Neo4j / A服务 配置
# =========================
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "CHANGE_ME")
import math
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go

from collections import Counter
from pyvis.network import Network

# =========================
# Neo4j / A服务 配置
# =========================
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "CHANGE_ME")

import math
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go

from collections import Counter
from pyvis.network import Network


# =========================================================
# 基础配置
# =========================================================
import socket

def get_local_ip():
    """获取本机局域网 IP 地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# 优先使用环境变量，否则自动获取本机 IP
GRAPH_API_HOST = os.environ.get("GRAPH_API_HOST", get_local_ip())
GRAPH_API_PORT = os.environ.get("GRAPH_API_PORT", "5001")
GRAPH_API_BASE = f"http://{GRAPH_API_HOST}:{GRAPH_API_PORT}"

TYPE_NAME_MAP = {
    "System": "系统",
    "Subsystem": "子系统",
    "Equipment": "设备",
    "Component": "部件",
    "Part": "零件",
    "Symptom": "故障现象",
    "Cause": "故障原因",
    "Reason": "故障原因",
    "Diagnosis": "诊断方法",
    "Repair": "维修方案",
    "Solution": "维修方案",
    "MaintenanceCase": "维修案例",
    "Tool": "工具",
    "Keyword": "关键词",
    "Warning": "预警信息",
    "RiskLevel": "风险等级",
    "Unknown": "未知类型"
}

COLOR_MAP = {
    "System": "#1565C0",
    "Subsystem": "#1E88E5",
    "Equipment": "#42A5F5",
    "Component": "#5C6BC0",
    "Part": "#7986CB",
    "Symptom": "#F4511E",
    "Cause": "#8E24AA",
    "Reason": "#8E24AA",
    "Diagnosis": "#00897B",
    "Repair": "#43A047",
    "Solution": "#43A047",
    "MaintenanceCase": "#F9A825",
    "Tool": "#546E7A",
    "Keyword": "#90CAF9",
    "Warning": "#EF6C00",
    "RiskLevel": "#C62828",
    "Unknown": "#90A4AE"
}

# 重点：补齐你当前图库真实关系
RELATION_NAME_MAP = {
    "HAS_EQUIPMENT": "关联设备",
    "HAS_COMPONENT": "关联部件",
    "RELATED_COMPONENT": "相关部件",
    "BELONGS_TO": "所属系统",
    "HAS_SUBSYSTEM": "所属子系统",
    "HAS_CAUSE": "可能原因",
    "CAUSED_BY": "可能由该原因引起",
    "HAS_DIAGNOSIS": "诊断方法",
    "REQUIRES_DIAGNOSIS": "建议采用该诊断方法确认",
    "HAS_REPAIR": "维修方案",
    "REPAIRED_BY": "维修处理",
    "FIXES": "可采用该维修方案处理",
    "EXHIBITS": "设备表现为该故障现象",
    "INSTANCE_OF": "类型归属",
    "CONFIRMED_CAUSE": "确认原因",
    "USED_REPAIR": "采用方案",
    "USE_TOOL": "所需工具",
    "REPLACE_PART": "更换部件"
}

VALID_LABELS = [
    "Symptom", "Equipment", "System", "Cause",
    "Repair", "Diagnosis", "MaintenanceCase"
]

# 重点：维护页也要支持真实关系
VALID_RELATIONSHIPS = [
    "HAS_EQUIPMENT",
    "BELONGS_TO",
    "HAS_CAUSE",
    "HAS_REPAIR",
    "HAS_DIAGNOSIS",
    "INSTANCE_OF",
    "CONFIRMED_CAUSE",
    "USED_REPAIR",
    "EXHIBITS",
    "CAUSED_BY",
    "REQUIRES_DIAGNOSIS",
    "FIXES"
]

def render_compact_empty_card(title, message="当前暂无数据"):
    st.markdown(f"""
    <div style="
        background:#F7FBFF;
        border:1px solid #DCE9F8;
        border-radius:16px;
        padding:18px 16px;
        min-height:110px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        font-family:Microsoft YaHei;
        margin-bottom:8px;
    ">
        <div style="font-size:16px;font-weight:700;color:#173B7A;margin-bottom:6px;">{title}</div>
        <div style="font-size:14px;color:#5C6C80;">{message}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# 通用请求
# =========================================================
def safe_get(url, params=None, timeout=20):
    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


import base64
import os

def svg_to_base64(svg_file):
    with open(svg_file, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

SIDEBAR_LOGO_SVG = svg_to_base64(os.path.join(os.path.dirname(__file__), "pic/1.svg"))


def safe_post(url, json_data=None, timeout=20):
    resp = requests.post(url, json=json_data, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def get_graph_service_health():
    try:
        result = safe_get(f"{GRAPH_API_BASE}/health", timeout=8)
        return result.get("success", False), result.get("message", "")
    except Exception as e:
        return False, str(e)


# =========================================================
# 建议文案辅助：给工人更明确的动作建议
# =========================================================
def normalize_text(x):
    return str(x).strip() if x is not None else ""


def unique_clean_list(values):
    out = []
    seen = set()
    for x in values or []:
        x = normalize_text(x)
        if x and x not in seen and x != "-":
            out.append(x)
            seen.add(x)
    return out


def build_worker_diag_advice(symptom_name, diagnoses, causes, equipments):
    diagnoses = unique_clean_list(diagnoses)
    causes = unique_clean_list(causes)
    equipments = unique_clean_list(equipments)

    if diagnoses:
        return "；".join(diagnoses[:3])

    parts = []
    if symptom_name:
        parts.append(f"先核查“{symptom_name}”对应报警信息和现场可见异常")
    if equipments:
        parts.append(f"重点检查设备：{'、'.join(equipments[:3])}")
    if causes:
        parts.append(f"优先围绕原因“{causes[0]}”做定点排查")
    parts.append("复核温度、压力、电流、振动、泄漏、异响等关键运行参数")
    return "；".join(parts)


def build_worker_repair_advice(repairs, causes):
    repairs = unique_clean_list(repairs)
    causes = unique_clean_list(causes)

    if repairs:
        return "；".join(repairs[:3])

    if causes:
        return f"可先围绕“{causes[0]}”对应部位做基础处理：检查、清洁、紧固、润滑、疏通；确认故障点后再拆修或更换"
    return "原因未明确前，先进行基础巡检：检查接线、紧固、润滑、堵塞、泄漏、冷却与供电状态，避免盲目更换部件"


def build_worker_risk_advice(symptom_name):
    if symptom_name:
        return f"若“{symptom_name}”伴随高温、带压、带电、泄漏、冒烟、异响等情况，须先停机隔离并确认安全后再处理"
    return "如存在高温、带压、带电、泄漏、异响等情况，须先停机隔离并确认安全后再处理"


def classify_action_tag(text):
    text = normalize_text(text)
    if not text:
        return "其他处理"

    rules = [
        ("检查检测", ["检查", "检测", "诊断", "测量", "复核", "确认", "排查"]),
        ("清洁疏通", ["清洗", "清洁", "疏通", "吹扫", "排污"]),
        ("紧固调整", ["紧固", "调整", "校准", "校正", "标定"]),
        ("润滑冷却", ["润滑", "加油", "冷却", "降温"]),
        ("更换修复", ["更换", "修复", "维修", "拆修", "更修"]),
        ("电气处理", ["接线", "断电", "供电", "电压", "电流", "绝缘"]),
    ]
    for tag, kws in rules:
        for kw in kws:
            if kw in text:
                return tag
    return "其他处理"


def node_type_guess(name):
    name = normalize_text(name)
    return "Unknown" if not name else "Unknown"


# =========================================================
# 接口数据获取
# =========================================================
def fetch_all_graph_from_a():
    result = safe_get(f"{GRAPH_API_BASE}/graph/all", timeout=30)
    if not result.get("success"):
        raise Exception(result.get("message", "获取全图失败"))

    data = result.get("data", {}) or {}
    nodes = data.get("nodes", []) or []
    edges = data.get("edges", []) or []

    normalized_nodes = []
    for n in nodes:
        node = dict(n)

        if "label" not in node:
            node["label"] = node.get("name", "")

        if "desc" not in node:
            node["desc"] = node.get("label", "")

        if "type" not in node:
            if "type_name" in node:
                node["type"] = node["type_name"]
            elif "raw_labels" in node and isinstance(node["raw_labels"], list) and node["raw_labels"]:
                node["type"] = node["raw_labels"][0]
            elif "labels" in node and isinstance(node["labels"], list) and node["labels"]:
                node["type"] = node["labels"][0]
            else:
                node["type"] = "Unknown"

        if "id" not in node:
            node["id"] = f"{node['type']}:{node['label']}"

        normalized_nodes.append(node)

    normalized_edges = []
    for e in edges:
        edge = dict(e)
        edge["label_cn"] = RELATION_NAME_MAP.get(edge.get("label", ""), edge.get("label", ""))
        normalized_edges.append(edge)

    return {
        "nodes": normalized_nodes,
        "edges": normalized_edges,
        "paths": [],
        "source": "all",
        "raw": result
    }


def fetch_fault_tree_from_a(symptom: str):
    symptom = (symptom or "").strip()
    if not symptom:
        return {
            "nodes": [],
            "edges": [],
            "paths": [],
            "source": "fault-tree",
            "raw": {},
            "summary": {},
            "worker_tips": []
        }

    result = safe_get(
        f"{GRAPH_API_BASE}/graph/fault-tree",
        params={"symptom": symptom},
        timeout=20
    )

    if not result.get("success"):
        raise Exception(result.get("message", "查询故障树失败"))

    data = result.get("data", {}) or {}
    candidates = data.get("candidates", []) or []
    backend_graph = data.get("graph", {}) or {}
    backend_nodes = backend_graph.get("nodes", []) or []
    backend_edges = backend_graph.get("edges", []) or []
    backend_paths = data.get("paths", []) or []

    # -----------------------------------------------------
    # 一、优先使用后端真实图结构
    # -----------------------------------------------------
    nodes = []
    edges = []

    node_seen = set()
    edge_seen = set()

    def add_node_obj(node):
        node = dict(node)
        label = normalize_text(node.get("label") or node.get("name"))
        node_type = normalize_text(node.get("type") or node.get("type_name"))
        if not label:
            return

        if not node_type:
            if "raw_labels" in node and isinstance(node["raw_labels"], list) and node["raw_labels"]:
                node_type = str(node["raw_labels"][0]).strip()
            elif "labels" in node and isinstance(node["labels"], list) and node["labels"]:
                node_type = str(node["labels"][0]).strip()
            else:
                node_type = "Unknown"

        node_id = normalize_text(node.get("id"))
        if not node_id:
            node_id = f"{node_type}:{label}"

        key = node_id
        if key in node_seen:
            return
        node_seen.add(key)

        nodes.append({
            "id": node_id,
            "label": label,
            "type": node_type,
            "desc": normalize_text(node.get("desc") or label),
            "raw_labels": node.get("raw_labels", [node_type])
        })

    def add_edge_obj(edge):
        edge = dict(edge)
        src = normalize_text(edge.get("from") or edge.get("source"))
        dst = normalize_text(edge.get("to") or edge.get("target"))
        rel = normalize_text(edge.get("label") or edge.get("type"))
        if not src or not dst or not rel:
            return
        key = (src, dst, rel)
        if key in edge_seen:
            return
        edge_seen.add(key)
        edges.append({
            "from": src,
            "to": dst,
            "label": rel,
            "label_cn": RELATION_NAME_MAP.get(rel, rel)
        })

    for n in backend_nodes:
        add_node_obj(n)

    for e in backend_edges:
        add_edge_obj(e)

    # -----------------------------------------------------
    # 二、如果后端 graph 为空，才允许前端兜底构图
    # 注意：兜底也按真实关系方向来拼
    # Equipment -EXHIBITS-> Symptom
    # Symptom -CAUSED_BY-> Cause
    # Cause -REQUIRES_DIAGNOSIS-> Diagnosis
    # Repair -FIXES-> Cause
    # -----------------------------------------------------
    if not nodes and not edges and candidates:
        def add_simple_node(node_type, name, desc=None):
            name = normalize_text(name)
            if not name or name == "-":
                return
            node_id = f"{node_type}:{name}"
            if node_id in node_seen:
                return
            node_seen.add(node_id)
            nodes.append({
                "id": node_id,
                "label": name,
                "type": node_type,
                "desc": desc or name,
                "raw_labels": [node_type]
            })

        def add_simple_edge(src_type, src_name, dst_type, dst_name, rel):
            src_name = normalize_text(src_name)
            dst_name = normalize_text(dst_name)
            if not src_name or not dst_name:
                return
            src = f"{src_type}:{src_name}"
            dst = f"{dst_type}:{dst_name}"
            key = (src, dst, rel)
            if key in edge_seen:
                return
            edge_seen.add(key)
            edges.append({
                "from": src,
                "to": dst,
                "label": rel,
                "label_cn": RELATION_NAME_MAP.get(rel, rel)
            })

        for item in candidates:
            symptom_name = normalize_text(item.get("symptom"))
            systems = unique_clean_list(item.get("system", []))
            equipments = unique_clean_list(item.get("equipment", []))
            causes = unique_clean_list(item.get("causes", []))
            diagnoses = unique_clean_list(item.get("diagnosis", []))
            repairs = unique_clean_list(item.get("repair", []))

            if symptom_name:
                add_simple_node("Symptom", symptom_name, "当前故障现象")

            for eq_name in equipments:
                add_simple_node("Equipment", eq_name, "关联设备")
                if symptom_name:
                    add_simple_edge("Equipment", eq_name, "Symptom", symptom_name, "EXHIBITS")

            for sys_name in systems:
                add_simple_node("System", sys_name, "所属系统")

            for eq_name in equipments:
                for sys_name in systems:
                    add_simple_edge("Equipment", eq_name, "System", sys_name, "BELONGS_TO")

            for cause_name in causes:
                add_simple_node("Cause", cause_name, "可能原因")
                if symptom_name:
                    add_simple_edge("Symptom", symptom_name, "Cause", cause_name, "CAUSED_BY")

                for dia_name in diagnoses:
                    add_simple_node("Diagnosis", dia_name, "推荐诊断方法")
                    add_simple_edge("Cause", cause_name, "Diagnosis", dia_name, "REQUIRES_DIAGNOSIS")

                for repair_name in repairs:
                    add_simple_node("Repair", repair_name, "推荐维修方案")
                    add_simple_edge("Repair", repair_name, "Cause", cause_name, "FIXES")

    # -----------------------------------------------------
    # 三、路径数据：优先用后端 paths，否则从 candidates 生成
    # -----------------------------------------------------
    paths = []
    worker_tips = []

    if backend_paths:
        for idx, p in enumerate(backend_paths, start=1):
            symptom_name = normalize_text(p.get("symptom") or symptom)
            equipment = normalize_text(p.get("equipment"))
            cause = normalize_text(p.get("cause"))
            diagnosis = normalize_text(p.get("diagnosis"))
            repair = normalize_text(p.get("repair"))

            diag_advice = diagnosis if diagnosis else build_worker_diag_advice(
                symptom_name=symptom_name,
                diagnoses=[],
                causes=[cause] if cause else [],
                equipments=[equipment] if equipment else []
            )
            repair_advice = repair if repair else build_worker_repair_advice(
                repairs=[],
                causes=[cause] if cause else []
            )

            path_row = {
                "路径编号": f"路径{idx}",
                "系统": "当前未建立系统级映射",
                "设备": equipment if equipment else "当前未识别具体设备",
                "故障现象": symptom_name if symptom_name else "未识别",
                "原因分支": cause if cause else "当前知识库未定位明确原因",
                "诊断建议": diag_advice,
                "维修建议": repair_advice,
                "优先级": "建议优先排查" if idx == 1 else "建议继续排查",
                "风险提示": build_worker_risk_advice(symptom_name)
            }
            paths.append(path_row)

    elif candidates:
        for item in candidates:
            symptom_name = normalize_text(item.get("symptom"))
            systems = unique_clean_list(item.get("system", []))
            equipments = unique_clean_list(item.get("equipment", []))
            causes = unique_clean_list(item.get("causes", []))
            diagnoses = unique_clean_list(item.get("diagnosis", []))
            repairs = unique_clean_list(item.get("repair", []))

            if causes:
                for idx, cause_name in enumerate(causes, start=1):
                    paths.append({
                        "路径编号": f"路径{len(paths) + 1}",
                        "系统": "、".join(systems) if systems else "当前未建立系统级映射",
                        "设备": "、".join(equipments) if equipments else "当前未识别具体设备",
                        "故障现象": symptom_name if symptom_name else symptom,
                        "原因分支": cause_name,
                        "诊断建议": build_worker_diag_advice(symptom_name, diagnoses, [cause_name], equipments),
                        "维修建议": build_worker_repair_advice(repairs, [cause_name]),
                        "优先级": "建议优先排查" if idx == 1 else "建议继续排查",
                        "风险提示": build_worker_risk_advice(symptom_name if symptom_name else symptom)
                    })
            else:
                paths.append({
                    "路径编号": f"路径{len(paths) + 1}",
                    "系统": "、".join(systems) if systems else "当前未建立系统级映射",
                    "设备": "、".join(equipments) if equipments else "当前未识别具体设备",
                    "故障现象": symptom_name if symptom_name else symptom,
                    "原因分支": "当前知识库未定位明确原因",
                    "诊断建议": build_worker_diag_advice(symptom_name if symptom_name else symptom, diagnoses, [], equipments),
                    "维修建议": build_worker_repair_advice(repairs, []),
                    "优先级": "待确认",
                    "风险提示": build_worker_risk_advice(symptom_name if symptom_name else symptom)
                })

    # -----------------------------------------------------
    # 四、工人提示：给出一句更明确的现场操作建议
    # -----------------------------------------------------
    if paths:
        first = paths[0]
        worker_tips = [
            f"优先排查：{first.get('原因分支', '当前未定位原因')}",
            f"建议先做：{first.get('诊断建议', '先核查运行参数和现场异常')}",
            f"处理方向：{first.get('维修建议', '先基础巡检，确认后再维修')}",
            f"安全提示：{first.get('风险提示', '处理前先确认安全状态')}"
        ]
    else:
        worker_tips = [
            "当前未从知识库检索到有效故障树路径",
            "建议先通过关键词联想确认更标准的故障现象名称",
            "建议补充报警代码、异常声音、温度/压力/电流变化、发生工况等信息"
        ]

    # -----------------------------------------------------
    # 五、统计摘要
    # -----------------------------------------------------
    summary_systems = set()
    summary_equipments = set()
    summary_causes = set()
    summary_diagnoses = set()
    summary_repairs = set()
    summary_symptoms = set()

    for item in candidates:
        symptom_name = normalize_text(item.get("symptom"))
        systems = unique_clean_list(item.get("system", []))
        equipments = unique_clean_list(item.get("equipment", []))
        causes = unique_clean_list(item.get("causes", []))
        diagnoses = unique_clean_list(item.get("diagnosis", []))
        repairs = unique_clean_list(item.get("repair", []))

        if symptom_name:
            summary_symptoms.add(symptom_name)
        summary_systems.update(systems)
        summary_equipments.update(equipments)
        summary_causes.update(causes)
        summary_diagnoses.update(diagnoses)
        summary_repairs.update(repairs)

    if backend_paths:
        for p in backend_paths:
            if normalize_text(p.get("symptom")):
                summary_symptoms.add(normalize_text(p.get("symptom")))
            if normalize_text(p.get("equipment")):
                summary_equipments.add(normalize_text(p.get("equipment")))
            if normalize_text(p.get("cause")):
                summary_causes.add(normalize_text(p.get("cause")))
            if normalize_text(p.get("diagnosis")):
                summary_diagnoses.add(normalize_text(p.get("diagnosis")))
            if normalize_text(p.get("repair")):
                summary_repairs.add(normalize_text(p.get("repair")))

    summary = {
        "关联系统数": len(summary_systems),
        "关联设备数": len(summary_equipments),
        "故障现象数": len(summary_symptoms),
        "可能原因数": len(summary_causes),
        "诊断建议数": len(summary_diagnoses),
        "维修方案数": len(summary_repairs),
        "分析路径数": len(paths)
    }

    return {
        "nodes": nodes,
        "edges": edges,
        "paths": paths,
        "source": "fault-tree",
        "raw": result,
        "summary": summary,
        "worker_tips": worker_tips
    }


def search_symptom_from_a(keyword: str, limit=10):
    keyword = (keyword or "").strip()
    if not keyword:
        return []
    result = safe_get(
        f"{GRAPH_API_BASE}/graph/symptom/search",
        params={"q": keyword, "limit": limit},
        timeout=15
    )
    if not result.get("success"):
        return []
    return result.get("data", []) or []


def add_node_to_a(label, name):
    return safe_post(f"{GRAPH_API_BASE}/graph/node/add", {"label": label, "name": name})


def update_node_to_a(label, old_name, new_name):
    return safe_post(f"{GRAPH_API_BASE}/graph/node/update", {
        "label": label,
        "old_name": old_name,
        "new_name": new_name
    })


def delete_node_to_a(label, name):
    return safe_post(f"{GRAPH_API_BASE}/graph/node/delete", {"label": label, "name": name})


def add_relation_to_a(start_label, start_name, relationship, end_label, end_name):
    return safe_post(f"{GRAPH_API_BASE}/graph/relation/add", {
        "start_label": start_label,
        "start_name": start_name,
        "relationship": relationship,
        "end_label": end_label,
        "end_name": end_name
    })


def delete_relation_to_a(start_label, start_name, relationship, end_label, end_name):
    return safe_post(f"{GRAPH_API_BASE}/graph/relation/delete", {
        "start_label": start_label,
        "start_name": start_name,
        "relationship": relationship,
        "end_label": end_label,
        "end_name": end_name
    })


# =========================================================
# 数据构建
# =========================================================
def build_node_df(graph_data):
    nodes = graph_data.get("nodes", []) or []
    if not nodes:
        return pd.DataFrame(columns=["id", "label", "type", "desc"])

    df = pd.DataFrame(nodes)

    if "label" not in df.columns:
        if "name" in df.columns:
            df["label"] = df["name"]
        else:
            df["label"] = ""

    if "desc" not in df.columns:
        df["desc"] = df["label"]

    if "type" not in df.columns:
        if "type_name" in df.columns:
            df["type"] = df["type_name"]
        elif "raw_labels" in df.columns:
            df["type"] = df["raw_labels"].apply(
                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else str(x)
            )
        elif "labels" in df.columns:
            df["type"] = df["labels"].apply(
                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else str(x)
            )
        else:
            df["type"] = "Unknown"

    df["type"] = df["type"].fillna("Unknown").astype(str).str.strip()
    df.loc[df["type"] == "", "type"] = "Unknown"

    if "id" not in df.columns:
        df["id"] = df.apply(
            lambda r: f"{r['type']}:{r['label']}" if r["label"] else f"{r['type']}:unknown",
            axis=1
        )

    return df[["id", "label", "type", "desc"]]


def build_edge_df(graph_data):
    edges = graph_data.get("edges", []) or []
    if not edges:
        return pd.DataFrame(columns=["from", "to", "label", "label_cn"])
    df = pd.DataFrame(edges)
    if "label_cn" not in df.columns:
        df["label_cn"] = df["label"].map(lambda x: RELATION_NAME_MAP.get(x, x))
    return df


def build_path_df(graph_data):
    paths = graph_data.get("paths", []) or []
    if not paths:
        return pd.DataFrame(columns=[
            "路径编号", "系统", "设备", "故障现象", "原因分支",
            "诊断建议", "维修建议", "优先级", "风险提示"
        ])
    return pd.DataFrame(paths)


def build_type_stats(node_df):
    if node_df is None or node_df.empty:
        return pd.DataFrame(columns=["type", "count"])

    df = node_df.copy()

    if "type" not in df.columns:
        return pd.DataFrame(columns=["type", "count"])

    df["type"] = df["type"].fillna("未知类型").astype(str).str.strip()
    df.loc[df["type"] == "", "type"] = "未知类型"

    result = df.groupby("type").size().reset_index(name="count")
    result = result.sort_values("count", ascending=False).reset_index(drop=True)
    return result


def build_relation_stats(edge_df):
    if edge_df.empty:
        return pd.DataFrame(columns=["label", "label_cn", "count"])
    result = edge_df.groupby(["label", "label_cn"]).size().reset_index(name="count")
    return result.sort_values("count", ascending=False)


def build_degree_stats(node_df, edge_df):
    if node_df is None or node_df.empty:
        return pd.DataFrame(columns=["id", "label", "type", "type_name", "degree"])

    df = node_df.copy()

    if "type" not in df.columns:
        df["type"] = "Unknown"

    if "label" not in df.columns:
        df["label"] = ""

    if "id" not in df.columns:
        df["id"] = df.apply(
            lambda r: f"{r['type']}:{r['label']}" if r["label"] else f"{r['type']}:unknown",
            axis=1
        )

    if edge_df is None or edge_df.empty:
        return pd.DataFrame(columns=["id", "label", "type", "type_name", "degree"])

    degree_counter = Counter()
    for _, row in edge_df.iterrows():
        if "from" in row and pd.notna(row["from"]):
            degree_counter[row["from"]] += 1
        if "to" in row and pd.notna(row["to"]):
            degree_counter[row["to"]] += 1

    node_map = {r["id"]: r for _, r in df.iterrows()}
    rows = []

    for node_id, degree in degree_counter.items():
        node = node_map.get(node_id)
        if node is not None:
            node_type = str(node.get("type", "Unknown"))
            rows.append({
                "id": node_id,
                "label": node.get("label", ""),
                "type": node_type,
                "type_name": TYPE_NAME_MAP.get(node_type, node_type),
                "degree": degree
            })

    if not rows:
        return pd.DataFrame(columns=["id", "label", "type", "type_name", "degree"])

    return pd.DataFrame(rows).sort_values("degree", ascending=False).reset_index(drop=True)


def build_business_overview_stats(node_df, edge_df=None):
    if node_df is None or node_df.empty:
        return {
            "系统覆盖数": 0,
            "设备覆盖数": 0,
            "故障现象数": 0,
            "故障原因数": 0,
            "维修方案数": 0
        }

    df = node_df.copy()

    if "type" not in df.columns:
        return {
            "系统覆盖数": 0,
            "设备覆盖数": 0,
            "故障现象数": 0,
            "故障原因数": 0,
            "维修方案数": 0
        }

    df["type"] = df["type"].fillna("Unknown").astype(str).str.strip()
    df.loc[df["type"] == "", "type"] = "Unknown"

    return {
        "系统覆盖数": int(df["type"].isin(["System", "Subsystem"]).sum()),
        "设备覆盖数": int(df["type"].isin(["Equipment", "Component", "Part"]).sum()),
        "故障现象数": int(df["type"].isin(["Symptom"]).sum()),
        "故障原因数": int(df["type"].isin(["Cause", "Reason"]).sum()),
        "维修方案数": int(df["type"].isin(["Repair", "Solution"]).sum())
    }


# =========================================================
# 图谱过滤 / 邻域
# =========================================================
def filter_graph_data(graph_data, selected_types=None, keyword="", max_nodes=300):
    selected_types = selected_types or []
    keyword = (keyword or "").strip().lower()

    nodes = graph_data.get("nodes", []) or []
    edges = graph_data.get("edges", []) or []

    filtered_nodes = []
    for n in nodes:
        type_ok = True if not selected_types else n.get("type") in selected_types
        text = f"{n.get('label', '')} {n.get('desc', '')} {n.get('type', '')}".lower()
        keyword_ok = True if not keyword else keyword in text
        if type_ok and keyword_ok:
            filtered_nodes.append(n)

    filtered_nodes = filtered_nodes[:max_nodes]
    node_ids = set(n["id"] for n in filtered_nodes)

    filtered_edges = []
    for e in edges:
        if e.get("from") in node_ids and e.get("to") in node_ids:
            edge = dict(e)
            edge["label_cn"] = RELATION_NAME_MAP.get(edge.get("label", ""), edge.get("label", ""))
            filtered_edges.append(edge)

    return {
        "nodes": filtered_nodes,
        "edges": filtered_edges,
        "paths": [],
        "source": graph_data.get("source", ""),
        "raw": graph_data.get("raw", {})
    }


def extract_neighbors_subgraph(graph_data, center_keyword, max_neighbors=80):
    center_keyword = (center_keyword or "").strip().lower()
    if not center_keyword:
        return {"nodes": [], "edges": [], "paths": [], "source": "neighbors", "raw": {}}

    nodes = graph_data.get("nodes", []) or []
    edges = graph_data.get("edges", []) or []

    matched = [n for n in nodes if center_keyword in str(n.get("label", "")).lower()]
    if not matched:
        return {"nodes": [], "edges": [], "paths": [], "source": "neighbors", "raw": {}}

    center = matched[0]
    center_id = center["id"]

    node_ids = {center_id}
    sub_edges = []

    for e in edges:
        if e["from"] == center_id or e["to"] == center_id:
            node_ids.add(e["from"])
            node_ids.add(e["to"])
            edge = dict(e)
            edge["label_cn"] = RELATION_NAME_MAP.get(edge.get("label", ""), edge.get("label", ""))
            sub_edges.append(edge)
        if len(node_ids) >= max_neighbors:
            break

    sub_nodes = [n for n in nodes if n["id"] in node_ids]

    return {
        "nodes": sub_nodes,
        "edges": sub_edges,
        "paths": [],
        "source": "neighbors",
        "raw": {}
    }


# =========================================================
# 业务辅助数据
# 重点：兼容 EXHIBITS，不再只依赖 HAS_EQUIPMENT
# =========================================================
def build_system_equipment_symptom_df(graph_data):
    nodes = graph_data.get("nodes", []) or []
    edges = graph_data.get("edges", []) or []
    node_map = {n["id"]: n for n in nodes}

    equipment_to_system = {}
    records = []

    for e in edges:
        src = node_map.get(e.get("from"))
        dst = node_map.get(e.get("to"))
        rel = e.get("label")
        if not src or not dst:
            continue

        if rel == "BELONGS_TO" and src.get("type") in ["Equipment", "Component", "Part"] and dst.get("type") in ["System", "Subsystem"]:
            equipment_to_system[src.get("label")] = dst.get("label")

    for e in edges:
        src = node_map.get(e.get("from"))
        dst = node_map.get(e.get("to"))
        rel = e.get("label")
        if not src or not dst:
            continue

        # 新兼容：Equipment -EXHIBITS-> Symptom
        if rel == "EXHIBITS" and src.get("type") in ["Equipment", "Component", "Part"] and dst.get("type") == "Symptom":
            records.append({
                "系统": equipment_to_system.get(src.get("label"), "当前未建立系统映射"),
                "设备": src.get("label"),
                "故障现象": dst.get("label"),
                "数量": 1
            })

        # 保留旧兼容
        if rel == "HAS_EQUIPMENT" and src.get("type") == "Symptom" and dst.get("type") in ["Equipment", "Component", "Part"]:
            records.append({
                "系统": equipment_to_system.get(dst.get("label"), "当前未建立系统映射"),
                "设备": dst.get("label"),
                "故障现象": src.get("label"),
                "数量": 1
            })

    if not records:
        return pd.DataFrame(columns=["系统", "设备", "故障现象", "数量"])

    df = pd.DataFrame(records)
    return df.groupby(["系统", "设备", "故障现象"], as_index=False)["数量"].sum()


# =========================================================
# UI：图例
# =========================================================
def render_legend():
    legend_items = [
        ("System", "系统"),
        ("Equipment", "设备"),
        ("Component", "部件"),
        ("Symptom", "故障现象"),
        ("Cause", "故障原因"),
        ("Diagnosis", "诊断方法"),
        ("Repair", "维修方案"),
        ("MaintenanceCase", "维修案例")
    ]

    html = """<div style="display:flex;flex-wrap:wrap;gap:12px 14px;margin-bottom:8px;">"""
    for k, label_cn in legend_items:
        color = COLOR_MAP.get(k, "#90A4AE")
        html += f"""
        <div style="
            display:inline-flex;align-items:center;gap:8px;
            background:#fff;border:1px solid #E8EEF7;border-radius:999px;
            padding:8px 14px;box-shadow:0 4px 10px rgba(20,60,120,0.06);
            font-family:Microsoft YaHei;font-size:14px;color:#234;font-weight:600;">
            <span style="width:14px;height:14px;border-radius:50%;display:inline-block;background:{color};"></span>
            <span>{label_cn}</span>
        </div>
        """
    html += "</div>"
    components.html(html, height=80, scrolling=False)


# =========================================================
# UI：Pyvis 图
# =========================================================
def render_pyvis_graph(graph_data, height=720, hierarchical=False, title_text=None, show_title=False):
    nodes = graph_data.get("nodes", []) or []
    edges = graph_data.get("edges", []) or []

    if not nodes:
        st.info("暂无可视化数据")
        return

    net = Network(
        height=f"{height}px",
        width="100%",
        directed=True,
        bgcolor="#F7FBFF",
        font_color="#1F2D3D"
    )

    level_map = {
        "Symptom": 1,
        "Cause": 2,
        "Reason": 2,
        "Equipment": 2,
        "Component": 2,
        "Part": 2,
        "Diagnosis": 3,
        "Repair": 3,
        "Solution": 3,
        "System": 3,
        "Subsystem": 3,
        "MaintenanceCase": 4
    }

    for n in nodes:
        node_id = n.get("id")
        node_type = n.get("type", "Unknown")
        label = n.get("label", "-")
        desc = n.get("desc", label)
        color = COLOR_MAP.get(node_type, "#90A4AE")

        title = f"""
        <div style="font-family:Microsoft YaHei;">
            <b>{label}</b><br/>
            类型：{TYPE_NAME_MAP.get(node_type, node_type)}<br/>
            说明：{desc}
        </div>
        """

        size = 34 if node_type == "Symptom" else 24 if node_type in ["Cause", "Reason"] else 18

        net.add_node(
            node_id,
            label=label,
            color=color,
            title=title,
            size=size,
            level=level_map.get(node_type, 5)
        )

    for e in edges:
        label_cn = e.get("label_cn") or RELATION_NAME_MAP.get(e.get("label", ""), e.get("label", ""))
        net.add_edge(
            e.get("from"),
            e.get("to"),
            label=label_cn,
            title=label_cn,
            color="#8AA4BF"
        )

    if hierarchical:
        net.set_options("""
        {
          "layout": {
            "hierarchical": {
              "enabled": true,
              "direction": "UD",
              "sortMethod": "directed",
              "levelSeparation": 150,
              "nodeSpacing": 170,
              "treeSpacing": 220
            }
          },
          "nodes": {
            "shape": "dot",
            "font": {"size": 16, "face": "Microsoft YaHei"},
            "borderWidth": 1
          },
          "edges": {
            "arrows": {"to": {"enabled": true}},
            "smooth": {"enabled": true, "type": "cubicBezier"},
            "font": {"size": 12, "face": "Microsoft YaHei", "align": "middle"}
          },
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true
          },
          "physics": {
            "enabled": false
          }
        }
        """)
    else:
        net.set_options("""
        {
          "nodes": {
            "shape": "dot",
            "font": {"size": 16, "face": "Microsoft YaHei"},
            "borderWidth": 1
          },
          "edges": {
            "arrows": {"to": {"enabled": true}},
            "smooth": {"enabled": true, "type": "dynamic"},
            "font": {"size": 12, "face": "Microsoft YaHei", "align": "middle"}
          },
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true,
            "multiselect": true
          },
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -3000,
              "springLength": 140,
              "springConstant": 0.03,
              "damping": 0.09
            },
            "stabilization": {
              "enabled": true,
              "iterations": 120
            }
          }
        }
        """)

    if show_title and title_text:
        st.markdown(f"### {title_text}")

    html = net.generate_html(notebook=False)
    components.html(html, height=height + 10, scrolling=True)


# =========================================================
# UI：故障分析摘要
# =========================================================
def render_fault_summary_cards(summary):
    if not summary:
        st.info("暂无故障分析摘要")
        return

    cols = st.columns(6)
    items = [
        ("关联系统", summary.get("关联系统数", 0)),
        ("关联设备", summary.get("关联设备数", 0)),
        ("可能原因", summary.get("可能原因数", 0)),
        ("诊断建议", summary.get("诊断建议数", 0)),
        ("维修方案", summary.get("维修方案数", 0)),
        ("分析路径", summary.get("分析路径数", 0)),
    ]

    for col, (name, value) in zip(cols, items):
        with col:
            st.metric(name, value)

    if summary.get("关联系统数", 0) == 0:
        st.caption("说明：当前知识库尚未建立完整系统级映射，不影响按“故障现象—原因—诊断—维修”链路进行分析。")


# =========================================================
# UI：工人操作建议面板
# =========================================================
def render_worker_action_panel(ft_data):
    tips = ft_data.get("worker_tips", []) or []
    path_df = build_path_df(ft_data)

    st.markdown("### 现场处置建议")

    if path_df.empty:
        st.markdown("""
        - 当前未从知识库检索到有效故障树路径  
        - 建议优先从“推荐故障现象”中选择更标准的症状名称  
        - 建议补充报警代码、异常声音、温度/压力/电流变化、发生工况、是否持续出现等现场信息  
        - 原因未明确前，先进行基础巡检：外观、连接、紧固、泄漏、堵塞、润滑、供电、冷却状态  
        - 若存在高温、带压、带电、泄漏、异响、冒烟等情况，须先停机隔离后再处理
        """)
        return

    if tips:
        for tip in tips:
            st.markdown(f"- {tip}")

    first = path_df.iloc[0]
    action_html = f"""
    <div style="
        background:#F8FBFF;
        border:1px solid #DCEBFA;
        border-radius:18px;
        padding:18px 20px;
        margin-top:12px;
        font-family:Microsoft YaHei;
        line-height:1.9;
        color:#24364B;
    ">
        <div style="font-size:18px;font-weight:800;color:#173B7A;margin-bottom:10px;">建议工人优先执行</div>
        <div><b>1. 优先排查原因：</b>{first.get("原因分支", "当前未定位原因")}</div>
        <div><b>2. 先做哪些检查：</b>{first.get("诊断建议", "先核查运行参数和现场异常")}</div>
        <div><b>3. 建议处理方向：</b>{first.get("维修建议", "先基础巡检，确认后再维修")}</div>
        <div><b>4. 安全注意事项：</b>{first.get("风险提示", "处理前先确认安全状态")}</div>
    </div>
    """
    components.html(action_html, height=230, scrolling=False)

# =========================================================
# UI：多路径卡片
# =========================================================
def render_fault_tree_cards(path_df):
    if path_df.empty:
        st.info("暂无故障路径分析结果")
        return

    cards_html = """
    <div style="display:flex;flex-direction:column;gap:16px;font-family:Microsoft YaHei;">
    """

    for idx, row in path_df.iterrows():
        priority = row.get("优先级", "建议排查")
        priority_color = "#F4511E" if "优先" in priority else "#546E7A"

        cards_html += f"""
        <div style="
            background:#FFFFFF;
            border:1px solid #E6EEF8;
            border-radius:22px;
            padding:22px 24px;
            box-shadow:0 10px 28px rgba(25,60,120,0.08);
        ">
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-bottom:16px;
            ">
                <div style="
                    font-size:18px;
                    font-weight:800;
                    color:#173B7A;
                ">
                    {row.get("路径编号", f"路径{idx + 1}")}
                </div>

                <div style="
                    padding:7px 14px;
                    border-radius:999px;
                    background:#F8FBFF;
                    border:1px solid #D9E8F8;
                    color:{priority_color};
                    font-size:13px;
                    font-weight:700;
                ">
                    {priority}
                </div>
            </div>

            <div style="
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:12px 24px;
                line-height:1.9;
                color:#24364B;
                font-size:15px;
            ">
                <div><b>所属系统：</b>{row.get("系统", "当前未建立系统映射")}</div>
                <div><b>关联设备：</b>{row.get("设备", "当前未识别具体设备")}</div>
                <div style="grid-column:1 / span 2;"><b>故障现象：</b>{row.get("故障现象", "未识别")}</div>
                <div style="grid-column:1 / span 2;"><b>原因分支：</b>{row.get("原因分支", "未识别")}</div>
                <div style="grid-column:1 / span 2;"><b>诊断建议：</b>{row.get("诊断建议", "-")}</div>
                <div style="grid-column:1 / span 2;"><b>维修建议：</b>{row.get("维修建议", "-")}</div>
                <div style="grid-column:1 / span 2;"><b>风险提示：</b>{row.get("风险提示", "-")}</div>
            </div>
        </div>
        """

    cards_html += "</div>"
    height = min(230 * len(path_df) + 40, 1600)
    components.html(cards_html, height=height, scrolling=True)


# =========================================================
# UI：故障树卡片视图
# =========================================================
def render_fault_tree_html(path_df, symptom_name="", topic_name=""):
    if path_df.empty:
        st.info("暂无故障树分析结果")
        return

    symptom_name = symptom_name or (
        path_df.iloc[0]["故障现象"]
        if "故障现象" in path_df.columns and not path_df.empty
        else "当前故障"
    )

    cause_tags = list(path_df["原因分支"].dropna().astype(str).unique())[:6] if "原因分支" in path_df.columns else []
    repair_tags = list(path_df["维修建议"].dropna().astype(str).unique())[:4] if "维修建议" in path_df.columns else []

    topic_block = ""
    if topic_name:
        topic_block = f"""
        <div style="font-size:13px;color:#5E748C;margin-bottom:8px;">当前专题：{topic_name}</div>
        """

    cause_html = "".join([
        f"""<span style="display:inline-block;margin:4px 8px 4px 0;padding:6px 12px;border-radius:999px;
        background:#F3E8FF;color:#6F42C1;font-size:13px;font-weight:600;">{c}</span>"""
        for c in cause_tags
    ]) or """<span style="color:#7B8A9A;">暂无明确原因分支</span>"""

    repair_html = "".join([
        f"""<span style="display:inline-block;margin:4px 8px 4px 0;padding:6px 12px;border-radius:999px;
        background:#EAF7EE;color:#2E7D32;font-size:13px;font-weight:600;">{r}</span>"""
        for r in repair_tags
    ]) or """<span style="color:#7B8A9A;">暂无明确维修方向</span>"""

    html = f"""
    <div style="background:#F8FBFF;border:1px solid #E3EDF8;border-radius:24px;padding:24px 22px 18px 22px;font-family:Microsoft YaHei;">
        {topic_block}
        <div style="font-size:22px;font-weight:800;color:#173B7A;margin-bottom:16px;">故障树结构总览</div>

        <div style="display:flex;justify-content:center;margin-bottom:20px;">
            <div style="
                background:linear-gradient(135deg,#FF7043 0%,#F4511E 100%);
                color:#fff;border-radius:18px;padding:16px 24px;
                box-shadow:0 8px 16px rgba(244,81,30,0.14);
                min-width:320px;text-align:center;">
                <div style="font-size:13px;opacity:0.92;">当前分析故障现象</div>
                <div style="font-size:20px;font-weight:800;margin-top:4px;">{symptom_name}</div>
            </div>
        </div>

        <div style="background:#fff;border:1px solid #E6EEF8;border-radius:18px;padding:18px 18px 14px 18px;margin-bottom:14px;">
            <div style="font-size:14px;font-weight:700;color:#173B7A;margin-bottom:10px;">主要原因分支</div>
            <div>{cause_html}</div>
        </div>

        <div style="background:#fff;border:1px solid #E6EEF8;border-radius:18px;padding:18px 18px 14px 18px;">
            <div style="font-size:14px;font-weight:700;color:#173B7A;margin-bottom:10px;">主要处理方向</div>
            <div>{repair_html}</div>
        </div>
    </div>
    """
    components.html(html, height=320, scrolling=False)
def render_temperature_topic_intro():
    st.markdown("""
    <div style="
        background:linear-gradient(135deg,#0D47A1 0%, #1976D2 100%);
        border-radius:22px;
        padding:20px 22px;
        color:white;
        box-shadow:0 8px 22px rgba(13,71,161,0.16);
        margin-bottom:14px;
    ">
        <div style="font-size:20px;font-weight:800;margin-bottom:8px;">主机温度异常专题分析</div>
        <div style="font-size:14px;line-height:1.8;opacity:0.96;">
            面向“船舶主机温度偏高”类故障，支持按缸位温度异常、局部过热、诊断与维修路径进行专题化深入分析。
        </div>
    </div>
    """, unsafe_allow_html=True)
def fetch_temperature_options_from_a(symptom="船舶主机温度偏高"):
    result = safe_get(
        f"{GRAPH_API_BASE}/graph/topic/temperature-options",
        params={"symptom": symptom},
        timeout=20
    )
    if not result.get("success"):
        raise Exception(result.get("message", "获取温度专题失败"))

    data = result.get("data", {}) or {}
    cards = data.get("cards", []) or []
    overview_fault_tree = data.get("overview_fault_tree", {}) or {}

    normalized_overview = normalize_fault_tree_frontend_result(
        overview_fault_tree,
        raw_result=result,
        source="temperature-topic-overview",
        query_text=symptom
    )

    return {
        "topic": data.get("topic", symptom),
        "cards": cards,
        "overview_fault_tree": normalized_overview,
        "raw": result
    }

def render_temperature_topic_buttons(cards, selected_name=""):
    if not cards:
        return None

    st.markdown("### 温度异常分支选择")
    st.caption("点击下列分支，查看对应的详细故障树分析。")

    cols = st.columns(4)
    clicked = None

    for idx, item in enumerate(cards):
        title = str(item.get("name", "")).strip() or f"分支{idx + 1}"
        is_selected = (title == selected_name)

        with cols[idx % 4]:
            if st.button(
                f"{'✓ ' if is_selected else ''}{title}",
                key=f"temperature_branch_btn_{idx}",
                use_container_width=True
            ):
                clicked = title

    return clicked


def render_temperature_topic_cards(cards, selected_name=""):
    if not cards:
        st.info("当前专题暂无可选分支")
        return None

    st.markdown("#### 温度异常分支选择")
    cols = st.columns(3)
    clicked = None

    for idx, item in enumerate(cards):
        title = str(item.get("name", "")).strip() or f"分支{idx+1}"
        desc = str(item.get("summary", "") or item.get("desc", "")).strip()
        is_selected = title == selected_name

        with cols[idx % 3]:
            st.markdown(f"""
            <div style="
                background:{'#EEF5FF' if is_selected else '#FFFFFF'};
                border:1px solid {'#9FC1F7' if is_selected else '#E6EEF8'};
                border-radius:18px;
                padding:16px 14px;
                min-height:120px;
                margin-bottom:10px;
                box-shadow:0 6px 16px rgba(25,60,120,0.05);
            ">
                <div style="font-size:16px;font-weight:800;color:#173B7A;margin-bottom:8px;">{title}</div>
                <div style="font-size:13px;color:#5C6C80;line-height:1.7;">{desc if desc else '点击查看该温度异常分支的详细故障树与维修建议。'}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"查看 {title}", key=f"temperature_topic_card_{idx}", use_container_width=True):
                clicked = title

    return clicked
def render_symptom_frequency_chart(all_graph_data, title="故障现象覆盖排行", top_n=12):
    node_df = build_node_df(all_graph_data)
    if node_df is None or node_df.empty:
        render_compact_empty_card(title, "暂无节点数据")
        return

    symptom_df = node_df[node_df["type"].isin(["Symptom"])].copy()
    if symptom_df.empty:
        render_compact_empty_card(title, "暂无故障现象节点")
        return

    df = symptom_df["label"].value_counts().reset_index()
    df.columns = ["故障现象", "数量"]
    df = df.head(top_n).sort_values("数量", ascending=True)

    fig = px.bar(
        df,
        x="数量",
        y="故障现象",
        orientation="h",
        text="数量",
        title=title,
        color="数量",
        color_continuous_scale="Oranges"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=420,
        margin=dict(l=20, r=50, t=60, b=20),
        xaxis_title="覆盖数量",
        yaxis_title="故障现象",
        font=dict(family="Microsoft YaHei"),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# UI：推荐面板
# =========================================================
def render_recommendation_panel(path_df):
    st.markdown("### 推荐优先排查项")

    if path_df.empty:
        st.info("暂无推荐内容")
        return

    top_causes = list(path_df["原因分支"].dropna().astype(str).unique())[:5]
    top_repairs = list(path_df["维修建议"].dropna().astype(str).unique())[:5]

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**优先检查原因**")
        if top_causes:
            for i, item in enumerate(top_causes, start=1):
                st.markdown(f"{i}. {item}")
        else:
            st.caption("暂无明确原因")

    with c2:
        st.markdown("**优先处理方向**")
        if top_repairs:
            for i, item in enumerate(top_repairs, start=1):
                st.markdown(f"{i}. {item}")
        else:
            st.caption("暂无明确处理建议")


# =========================================================
# Plotly 图：总览
# =========================================================
def render_type_donut_chart(type_stats_df, title="知识构成占比"):
    import pandas as pd
    import streamlit as st
    import plotly.express as px

    if type_stats_df is None or type_stats_df.empty:
        st.info("暂无数据")
        return

    df = type_stats_df.copy()

    if "type" not in df.columns:
        if "type_name" in df.columns:
            df["type"] = df["type_name"]
        elif "label" in df.columns:
            df["type"] = df["label"]
        else:
            st.warning(f"类型统计数据缺少类型列，当前列名：{df.columns.tolist()}")
            st.dataframe(df)
            return

    if "count" not in df.columns:
        st.warning(f"类型统计数据缺少 count 列，当前列名：{df.columns.tolist()}")
        st.dataframe(df)
        return

    df["type"] = df["type"].fillna("未知类型").astype(str).str.strip()
    df.loc[df["type"] == "", "type"] = "未知类型"
    df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0)

    if df["count"].sum() <= 0:
        st.info("暂无可展示的类型统计数据")
        return

    fig = px.pie(
        df,
        names="type",
        values="count",
        hole=0.55,
        title=title
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(family="Microsoft YaHei")
    )
    st.plotly_chart(fig, use_container_width=True)


def render_relation_bar_chart(relation_stats_df, title="关系覆盖情况", top_n=12):
    import pandas as pd

    if relation_stats_df is None or relation_stats_df.empty:
        st.info("暂无数据")
        return

    df = relation_stats_df.copy()

    # 兼容名称列
    if "label_cn" not in df.columns:
        if "label" in df.columns:
            df["label_cn"] = df["label"]
        elif "relation" in df.columns:
            df["label_cn"] = df["relation"]
        else:
            st.warning(f"关系统计数据缺少名称列，当前列名：{df.columns.tolist()}")
            st.dataframe(df)
            return

    if "count" not in df.columns:
        st.warning(f"关系统计数据缺少 count 列，当前列名：{df.columns.tolist()}")
        st.dataframe(df)
        return

    df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0)
    show_df = df.head(top_n).copy()
    show_df = show_df.sort_values("count", ascending=True)

    fig = px.bar(
        show_df,
        x="count",
        y="label_cn",
        orientation="h",
        color="count",
        text="count",
        title=title,
        color_continuous_scale="Blues"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=420,
        margin=dict(l=20, r=50, t=60, b=20),
        xaxis_title="关系数量",
        yaxis_title="关系类型",
        font=dict(family="Microsoft YaHei"),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)


def render_system_sunburst_chart(graph_data, title="系统-设备-故障现象层级分布"):
    df = build_system_equipment_symptom_df(graph_data)
    if df is None or df.empty or len(df) < 2:
        st.info("当前层级数据较少，暂不展示旭日图")
        return

    required_cols = ["系统", "设备", "故障现象", "数量"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.warning(f"旭日图数据缺少列：{missing}")
        st.dataframe(df)
        return

    fig = px.sunburst(
        df,
        path=["系统", "设备", "故障现象"],
        values="数量",
        title=title
    )
    fig.update_layout(
        height=560,
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(family="Microsoft YaHei")
    )
    st.plotly_chart(fig, use_container_width=True)


def render_type_treemap_chart(type_stats_df, title="知识类型树图"):
    import pandas as pd
    import streamlit as st
    import plotly.express as px

    if type_stats_df is None or type_stats_df.empty:
        st.info("暂无数据")
        return

    df = type_stats_df.copy()

    # 统一类型列
    if "type" not in df.columns:
        if "type_name" in df.columns:
            df["type"] = df["type_name"]
        elif "label" in df.columns:
            df["type"] = df["label"]
        else:
            st.warning(f"树图数据缺少类型列，当前列名：{df.columns.tolist()}")
            st.dataframe(df)
            return

    # 检查 count 列
    if "count" not in df.columns:
        st.warning(f"树图数据缺少 count 列，当前列名：{df.columns.tolist()}")
        st.dataframe(df)
        return

    # 清理数据
    df["type"] = df["type"].fillna("未知类型").astype(str).str.strip()
    df.loc[df["type"] == "", "type"] = "未知类型"
    df["count"] = pd.to_numeric(df["count"], errors="coerce").fillna(0)
    df = df[df["count"] > 0].copy()

    if df.empty:
        st.info("暂无可展示的树图数据")
        return

    fig = px.treemap(
        df,
        path=[px.Constant("知识图谱"), "type"],
        values="count",
        color="count",
        color_continuous_scale="Blues",
        title=title
    )
    fig.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(family="Microsoft YaHei"),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# Plotly 图：诊断分析
# =========================================================
def render_top_degree_bar_chart(degree_stats_df, title="高关联知识节点排行", top_n=15):
    import pandas as pd

    if degree_stats_df is None or degree_stats_df.empty:
        st.info("暂无数据")
        return

    df = degree_stats_df.copy()

    # 兼容名称列
    if "label" not in df.columns:
        if "name" in df.columns:
            df["label"] = df["name"]
        else:
            st.warning(f"节点排行数据缺少 label 列，当前列名：{df.columns.tolist()}")
            st.dataframe(df)
            return

    # 兼容度数字段
    if "degree" not in df.columns:
        st.warning(f"节点排行数据缺少 degree 列，当前列名：{df.columns.tolist()}")
        st.dataframe(df)
        return

    # 兼容类型列
    if "type_name" not in df.columns:
        if "type" in df.columns:
            df["type_name"] = df["type"]
        elif "label_type" in df.columns:
            df["type_name"] = df["label_type"]
        else:
            df["type_name"] = "未知类型"

    df["degree"] = pd.to_numeric(df["degree"], errors="coerce").fillna(0)

    show_df = df.head(top_n).copy()
    show_df = show_df.sort_values("degree", ascending=True)

    fig = px.bar(
        show_df,
        x="degree",
        y="label",
        orientation="h",
        color="type_name",
        text="degree",
        title=title
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=520,
        margin=dict(l=20, r=60, t=60, b=20),
        xaxis_title="关联度",
        yaxis_title="节点名称",
        font=dict(family="Microsoft YaHei"),
        legend_title="节点类型"
    )
    st.plotly_chart(fig, use_container_width=True)

def render_fault_sankey_chart(path_df, title="故障多路径流向图"):
    if path_df is None or path_df.empty:
        render_compact_empty_card(title, "暂无路径数据")
        return

    valid_rows = []
    for _, row in path_df.iterrows():
        symptom = str(row.get("故障现象", "")).strip()
        cause = str(row.get("原因分支", "")).strip()
        diagnosis = str(row.get("诊断建议", "")).strip()
        repair = str(row.get("维修建议", "")).strip()

        if symptom or cause or diagnosis or repair:
            valid_rows.append((symptom, cause, diagnosis, repair))

    if not valid_rows:
        render_compact_empty_card(title, "暂无可用于构建流向图的数据")
        return

    labels = []
    label_index = {}

    def get_idx(name):
        if name not in label_index:
            label_index[name] = len(labels)
            labels.append(name)
        return label_index[name]

    sources, targets, values, colors = [], [], [], []

    for symptom, cause, diagnosis, repair in valid_rows:
        symptom_label = f"故障：{symptom or '未识别故障'}"
        cause_label = f"原因：{cause or '未明确原因'}"
        diagnosis_label = f"诊断：{diagnosis[:18]}..." if diagnosis and len(diagnosis) > 18 else f"诊断：{diagnosis or '待补充'}"
        repair_label = f"维修：{repair[:18]}..." if repair and len(repair) > 18 else f"维修：{repair or '待补充'}"

        s_idx = get_idx(symptom_label)
        c_idx = get_idx(cause_label)
        d_idx = get_idx(diagnosis_label)
        r_idx = get_idx(repair_label)

        sources.extend([s_idx, c_idx, c_idx])
        targets.extend([c_idx, d_idx, r_idx])
        values.extend([1, 1, 1])
        colors.extend(["#FF8A65", "#9575CD", "#66BB6A"])

    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=18,
            thickness=18,
            line=dict(color="#D0D7E2", width=0.6),
            label=labels,
            color=[
                "#FF7043" if x.startswith("故障：") else
                "#7E57C2" if x.startswith("原因：") else
                "#26A69A" if x.startswith("诊断：") else
                "#43A047"
                for x in labels
            ]
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors
        )
    )])

    fig.update_layout(
        title_text=title,
        font=dict(size=13, family="Microsoft YaHei"),
        height=520,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)


def render_cause_frequency_chart(path_df, title="原因分支分布", top_n=10):
    if path_df is None or path_df.empty or "原因分支" not in path_df.columns:
        st.info("暂无原因分支数据")
        return

    cause_series = path_df["原因分支"].dropna().astype(str)
    if cause_series.empty:
        st.info("暂无原因分支数据")
        return

    df = cause_series.value_counts().reset_index()
    df.columns = ["原因分支", "次数"]
    df = df.head(top_n).sort_values("次数", ascending=True)

    fig = px.bar(
        df,
        x="次数",
        y="原因分支",
        orientation="h",
        color="次数",
        text="次数",
        title=title,
        color_continuous_scale="Purples"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=420,
        margin=dict(l=20, r=50, t=60, b=20),
        xaxis_title="出现次数",
        yaxis_title="原因分支",
        font=dict(family="Microsoft YaHei"),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)


def render_repair_frequency_chart(path_df, title="维修建议分布", top_n=10):
    if path_df is None or path_df.empty or "维修建议" not in path_df.columns:
        st.info("暂无维修建议数据")
        return

    repair_series = path_df["维修建议"].dropna().astype(str)
    if repair_series.empty:
        st.info("暂无维修建议数据")
        return

    df = repair_series.value_counts().reset_index()
    df.columns = ["维修建议", "次数"]
    df = df.head(top_n).sort_values("次数", ascending=True)

    fig = px.bar(
        df,
        x="次数",
        y="维修建议",
        orientation="h",
        color="次数",
        text="次数",
        title=title,
        color_continuous_scale="Greens"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=420,
        margin=dict(l=20, r=50, t=60, b=20),
        xaxis_title="出现次数",
        yaxis_title="维修建议",
        font=dict(family="Microsoft YaHei"),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)



import uuid
from datetime import datetime
import requests

def markdown_to_html(text: str) -> str:
    if not text:
        return ""
    return markdown.markdown(
        text,
        extensions=["extra", "tables", "fenced_code", "nl2br", "sane_lists"]
    )



A_GRAPH_UPDATE_URL = "http://127.0.0.1:5001/graph/update"


def build_graph_payload_from_llm_result(llm_result: dict):
    return build_graph_payload(
        symptom=llm_result["symptom"],
        equipment=llm_result["equipment"],
        system=llm_result["system"],
        root_cause=llm_result["root_cause"],
        repair=llm_result["repair"],
        diagnosis=llm_result["diagnosis"],
        confidence_score=llm_result.get("confidence_score", 0.95),
        source="Expert_LLM_Learning"
    )


def push_to_a_graph_update(payload: dict, timeout: int = 15):
    """
    调用 A 的知识图谱自学习接口
    """
    resp = requests.post(
        A_GRAPH_UPDATE_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=timeout
    )

    try:
        result = resp.json()
    except Exception:
        raise Exception(f"A 服务返回非 JSON：HTTP {resp.status_code}，内容：{resp.text}")

    if resp.status_code != 200 or not result.get("success", False):
        raise Exception(result.get("message", f"写入失败，HTTP {resp.status_code}"))

    return result


def build_graph_payload(
        symptom: str,
        equipment: str,
        system: str,
        root_cause: str,
        repair: str,
        diagnosis: str,
        confidence_score: float = 0.95,
        source: str = "Streamlit_Graph_Writeback"
):
    """
    按 A 最新 /graph/update 协议构造 payload
    """

    symptom = symptom.strip()
    equipment = equipment.strip()
    system = system.strip()
    root_cause = root_cause.strip()
    repair = repair.strip()
    diagnosis = diagnosis.strip()

    payload = {
        "meta": {
            "session_id": f"SHIPFAULT-{uuid.uuid4()}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": source
        },
        "knowledge_content": {
            "symptom": symptom,
            "equipment": equipment,
            "system": system,
            "root_cause": root_cause,
            "repair": repair,
            "diagnosis": diagnosis,
            "confidence_score": float(confidence_score)
        },
        "graph_updates": [
            {
                "action": "MERGE",
                "start_node": {
                    "label": "Symptom",
                    "name": symptom
                },
                "relationship": "HAS_EQUIPMENT",
                "end_node": {
                    "label": "Equipment",
                    "name": equipment
                }
            },
            {
                "action": "MERGE",
                "start_node": {
                    "label": "Equipment",
                    "name": equipment
                },
                "relationship": "BELONGS_TO",
                "end_node": {
                    "label": "System",
                    "name": system
                }
            },
            {
                "action": "MERGE",
                "start_node": {
                    "label": "Symptom",
                    "name": symptom
                },
                "relationship": "HAS_CAUSE",
                "end_node": {
                    "label": "Cause",
                    "name": root_cause
                }
            },
            {
                "action": "MERGE",
                "start_node": {
                    "label": "Cause",
                    "name": root_cause
                },
                "relationship": "HAS_REPAIR",
                "end_node": {
                    "label": "Repair",
                    "name": repair
                }
            },
            {
                "action": "MERGE",
                "start_node": {
                    "label": "Cause",
                    "name": root_cause
                },
                "relationship": "HAS_DIAGNOSIS",
                "end_node": {
                    "label": "Diagnosis",
                    "name": diagnosis
                }
            }
        ]
    }

    return payload


def svg_file_to_data_uri(file_path: str) -> str:
    with open(file_path, "rb") as f:
        svg_data = f.read()
    b64 = base64.b64encode(svg_data).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"

def safe_svg_file_to_data_uri(file_path: str) -> str:
    try:
        with open(file_path, "rb") as f:
            svg_data = f.read()
        b64 = base64.b64encode(svg_data).decode("utf-8")
        return f"data:image/svg+xml;base64,{b64}"
    except Exception:
        return ""

def safe_image_file_to_data_uri(file_path: str, mime_type: str = "image/png") -> str:
    try:
        with open(file_path, "rb") as f:
            image_data = f.read()
        b64 = base64.b64encode(image_data).decode("utf-8")
        return f"data:{mime_type};base64,{b64}"
    except Exception:
        return ""

USER_AVATAR_SVG = safe_svg_file_to_data_uri(os.path.join(_SERVICEO_ROOT, "pic", "12.svg"))
ASSISTANT_AVATAR_SVG = safe_svg_file_to_data_uri(os.path.join(_SERVICEO_ROOT, "pic", "13.svg"))
SIDEBAR_LOGO_SVG = svg_file_to_data_uri(os.path.join(_SERVICEO_ROOT, "pic", "1.svg"))

def image_file_to_data_uri(file_path: str, mime_type: str = "image/png") -> str:
    with open(file_path, "rb") as f:
        image_data = f.read()
    b64 = base64.b64encode(image_data).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"

def normalize_fault_tree_frontend_result(data_block, raw_result=None, source="fault-tree", query_text=""):
    data_block = data_block or {}

    backend_graph = data_block.get("graph", {}) or {}
    backend_nodes = backend_graph.get("nodes", []) or []
    backend_edges = backend_graph.get("edges", []) or []
    backend_paths = data_block.get("paths", []) or []
    candidates = data_block.get("candidates", []) or []
    summary_from_backend = data_block.get("summary", {}) or {}

    nodes = []
    edges = []
    node_seen = set()
    edge_seen = set()

    def add_node_obj(node):
        node = dict(node)
        label = normalize_text(node.get("label") or node.get("name"))
        node_type = normalize_text(node.get("type") or node.get("type_name"))
        if not label:
            return

        if not node_type:
            if isinstance(node.get("raw_labels"), list) and node["raw_labels"]:
                node_type = str(node["raw_labels"][0]).strip()
            elif isinstance(node.get("labels"), list) and node["labels"]:
                node_type = str(node["labels"][0]).strip()
            else:
                node_type = "Unknown"

        node_id = normalize_text(node.get("id")) or f"{node_type}:{label}"
        if node_id in node_seen:
            return
        node_seen.add(node_id)

        nodes.append({
            "id": node_id,
            "label": label,
            "type": node_type,
            "desc": normalize_text(node.get("desc") or label),
            "raw_labels": node.get("raw_labels", [node_type])
        })

    def add_edge_obj(edge):
        edge = dict(edge)
        src = normalize_text(edge.get("from") or edge.get("source"))
        dst = normalize_text(edge.get("to") or edge.get("target"))
        rel = normalize_text(edge.get("label") or edge.get("type"))
        if not src or not dst or not rel:
            return
        key = (src, dst, rel)
        if key in edge_seen:
            return
        edge_seen.add(key)
        edges.append({
            "from": src,
            "to": dst,
            "label": rel,
            "label_cn": RELATION_NAME_MAP.get(rel, rel)
        })

    for n in backend_nodes:
        add_node_obj(n)
    for e in backend_edges:
        add_edge_obj(e)

    if not nodes and not edges and candidates:
        def add_simple_node(node_type, name, desc=None):
            name = normalize_text(name)
            if not name or name == "-":
                return
            node_id = f"{node_type}:{name}"
            if node_id in node_seen:
                return
            node_seen.add(node_id)
            nodes.append({
                "id": node_id,
                "label": name,
                "type": node_type,
                "desc": desc or name,
                "raw_labels": [node_type]
            })

        def add_simple_edge(src_type, src_name, dst_type, dst_name, rel):
            src_name = normalize_text(src_name)
            dst_name = normalize_text(dst_name)
            if not src_name or not dst_name:
                return
            src = f"{src_type}:{src_name}"
            dst = f"{dst_type}:{dst_name}"
            key = (src, dst, rel)
            if key in edge_seen:
                return
            edge_seen.add(key)
            edges.append({
                "from": src,
                "to": dst,
                "label": rel,
                "label_cn": RELATION_NAME_MAP.get(rel, rel)
            })

        for item in candidates:
            symptom_name = normalize_text(item.get("symptom") or query_text)
            systems = unique_clean_list(item.get("system", []))
            equipments = unique_clean_list(item.get("equipment", []))
            causes = unique_clean_list(item.get("causes", []))
            diagnoses = unique_clean_list(item.get("diagnosis", []))
            repairs = unique_clean_list(item.get("repair", []))

            if symptom_name:
                add_simple_node("Symptom", symptom_name, "当前故障现象")

            for eq_name in equipments:
                add_simple_node("Equipment", eq_name, "关联设备")
                if symptom_name:
                    add_simple_edge("Equipment", eq_name, "Symptom", symptom_name, "EXHIBITS")

            for sys_name in systems:
                add_simple_node("System", sys_name, "所属系统")

            for eq_name in equipments:
                for sys_name in systems:
                    add_simple_edge("Equipment", eq_name, "System", sys_name, "BELONGS_TO")

            for cause_name in causes:
                add_simple_node("Cause", cause_name, "可能原因")
                if symptom_name:
                    add_simple_edge("Symptom", symptom_name, "Cause", cause_name, "CAUSED_BY")

                for dia_name in diagnoses:
                    add_simple_node("Diagnosis", dia_name, "推荐诊断方法")
                    add_simple_edge("Cause", cause_name, "Diagnosis", dia_name, "REQUIRES_DIAGNOSIS")

                for repair_name in repairs:
                    add_simple_node("Repair", repair_name, "推荐维修方案")
                    add_simple_edge("Repair", repair_name, "Cause", cause_name, "FIXES")

    paths = []
    if backend_paths:
        for idx, p in enumerate(backend_paths, start=1):
            symptom_name = normalize_text(p.get("symptom") or query_text)
            equipment = normalize_text(p.get("equipment"))
            cause = normalize_text(p.get("cause"))
            diagnosis = normalize_text(p.get("diagnosis"))
            repair = normalize_text(p.get("repair"))

            paths.append({
                "路径编号": f"路径{idx}",
                "系统": "当前未建立系统级映射",
                "设备": equipment if equipment else "当前未识别具体设备",
                "故障现象": symptom_name if symptom_name else "未识别",
                "原因分支": cause if cause else "当前知识库未定位明确原因",
                "诊断建议": diagnosis if diagnosis else build_worker_diag_advice(symptom_name, [], [cause], [equipment]),
                "维修建议": repair if repair else build_worker_repair_advice([], [cause]),
                "优先级": "建议优先排查" if idx == 1 else "建议继续排查",
                "风险提示": build_worker_risk_advice(symptom_name)
            })
    elif candidates:
        for item in candidates:
            symptom_name = normalize_text(item.get("symptom") or query_text)
            systems = unique_clean_list(item.get("system", []))
            equipments = unique_clean_list(item.get("equipment", []))
            causes = unique_clean_list(item.get("causes", []))
            diagnoses = unique_clean_list(item.get("diagnosis", []))
            repairs = unique_clean_list(item.get("repair", []))

            if causes:
                for idx, cause_name in enumerate(causes, start=1):
                    paths.append({
                        "路径编号": f"路径{len(paths) + 1}",
                        "系统": "、".join(systems) if systems else "当前未建立系统级映射",
                        "设备": "、".join(equipments) if equipments else "当前未识别具体设备",
                        "故障现象": symptom_name,
                        "原因分支": cause_name,
                        "诊断建议": build_worker_diag_advice(symptom_name, diagnoses, [cause_name], equipments),
                        "维修建议": build_worker_repair_advice(repairs, [cause_name]),
                        "优先级": "建议优先排查" if idx == 1 else "建议继续排查",
                        "风险提示": build_worker_risk_advice(symptom_name)
                    })
            else:
                paths.append({
                    "路径编号": f"路径{len(paths) + 1}",
                    "系统": "、".join(systems) if systems else "当前未建立系统级映射",
                    "设备": "、".join(equipments) if equipments else "当前未识别具体设备",
                    "故障现象": symptom_name,
                    "原因分支": "当前知识库未定位明确原因",
                    "诊断建议": build_worker_diag_advice(symptom_name, diagnoses, [], equipments),
                    "维修建议": build_worker_repair_advice(repairs, []),
                    "优先级": "待确认",
                    "风险提示": build_worker_risk_advice(symptom_name)
                })

    summary = {
        "关联系统数": summary_from_backend.get("关联系统数", 0),
        "关联设备数": summary_from_backend.get("关联设备数", 0),
        "故障现象数": summary_from_backend.get("故障现象数", 1 if query_text else 0),
        "可能原因数": summary_from_backend.get("可能原因数", len(set([p["原因分支"] for p in paths if p["原因分支"]]))),
        "诊断建议数": summary_from_backend.get("诊断建议数", len(set([p["诊断建议"] for p in paths if p["诊断建议"]]))),
        "维修方案数": summary_from_backend.get("维修方案数", len(set([p["维修建议"] for p in paths if p["维修建议"]]))),
        "分析路径数": summary_from_backend.get("分析路径数", len(paths))
    }

    worker_tips = []
    if paths:
        first = paths[0]
        worker_tips = [
            f"优先排查：{first.get('原因分支', '当前未定位原因')}",
            f"建议先做：{first.get('诊断建议', '先核查运行参数和现场异常')}",
            f"处理方向：{first.get('维修建议', '先基础巡检，确认后再维修')}",
            f"安全提示：{first.get('风险提示', '处理前先确认安全状态')}"
        ]
    else:
        worker_tips = [
            "当前未从知识库检索到有效故障树路径",
            "建议先通过关键词联想确认更标准的故障现象名称",
            "建议补充报警代码、异常声音、温度/压力/电流变化、发生工况等信息"
        ]

    return {
        "nodes": nodes,
        "edges": edges,
        "paths": paths,
        "source": source,
        "raw": raw_result or {},
        "summary": summary,
        "worker_tips": worker_tips
    }


def fetch_temperature_options_from_a(symptom="船舶主机温度偏高"):
    result = safe_get(
        f"{GRAPH_API_BASE}/graph/topic/temperature-options",
        params={"symptom": symptom},
        timeout=20
    )
    if not result.get("success"):
        raise Exception(result.get("message", "获取温度专题失败"))

    data = result.get("data", {}) or {}
    cards = data.get("cards", []) or []
    overview_fault_tree = data.get("overview_fault_tree", {}) or {}

    normalized_overview = normalize_fault_tree_frontend_result(
        overview_fault_tree,
        raw_result=result,
        source="temperature-topic-overview",
        query_text=symptom
    )

    return {
        "topic": data.get("topic", symptom),
        "cards": cards,
        "overview_fault_tree": normalized_overview,
        "raw": result
    }


def fetch_temperature_detail_from_a(name):
    result = safe_get(
        f"{GRAPH_API_BASE}/graph/topic/temperature-detail",
        params={"name": name},
        timeout=20
    )
    if not result.get("success"):
        raise Exception(result.get("message", "获取温度专题详情失败"))

    data = result.get("data", {}) or {}
    detail_block = data.get("detail", {}) or data

    normalized = normalize_fault_tree_frontend_result(
        detail_block,
        raw_result=result,
        source="temperature-topic-detail",
        query_text=name
    )
    normalized["detail_name"] = name
    return normalized

def load_svg(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

LOGO_SVG = load_svg(os.path.join(_SERVICEO_ROOT, "pic", "1.svg"))

import html


def plain_text_to_html(text: str) -> str:
    text = html.escape(str(text))
    text = text.replace("\n", "<br>")
    return text


def looks_like_markdown_table(text: str):
    table_df = None
    content_text = str(text).strip()

    try:
        lines = [line.strip() for line in content_text.splitlines() if line.strip()]
        block = []

        for line in lines:
            if line.startswith("|") and line.endswith("|"):
                block.append(line)
            else:
                if len(block) >= 2:
                    break
                else:
                    block = []

        if len(block) >= 2:
            separator_line = block[1]

            if re.match(r'^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$', separator_line):

                def split_row(row):
                    row = row.strip()
                    if row.startswith("|"):
                        row = row[1:]
                    if row.endswith("|"):
                        row = row[:-1]
                    return [cell.strip() for cell in row.split("|")]

                columns = split_row(block[0])
                rows = []

                for row_line in block[2:]:
                    row = split_row(row_line)

                    if len(row) < len(columns):
                        row += [""] * (len(columns) - len(row))
                    elif len(row) > len(columns):
                        row = row[:len(columns)]

                    rows.append(row)

                if columns and rows:
                    table_df = pd.DataFrame(rows, columns=columns)

    except Exception:
        table_df = None

    return table_df


@st.cache_resource
def get_neo4j_driver():
    return GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )


# =========================
# 旧标签 -> 新标准标签 映射
# =========================
LABEL_ALIAS_MAP = {
    "Equipment": "Equipment",
    "EquipmentType": "Equipment",

    "Subsystem": "Subsystem",

    "Component": "Component",

    "Symptom": "Symptom",

    "Reason": "Reason",
    "Cause": "Reason",

    "Solution": "Solution",

    "Tool": "Tool",

    "Part": "Part",

    "RiskLevel": "RiskLevel",

    "Warning": "Warning",

    "Keyword": "Keyword",

    "MaintenanceCase": "MaintenanceCase",
}

# =========================
# 旧关系 -> 标准关系 映射（可继续补）
# =========================
REL_ALIAS_MAP = {
    "HAS_SUBSYSTEM": "HAS_SUBSYSTEM",
    "HAS_COMPONENT": "HAS_COMPONENT",
    "HAS_SYMPTOM": "HAS_SYMPTOM",
    "CAUSED_BY": "CAUSED_BY",
    "REPAIRED_BY": "REPAIRED_BY",
    "USE_TOOL": "USE_TOOL",
    "REPLACE_PART": "REPLACE_PART",
    "HAS_RISK_LEVEL": "HAS_RISK_LEVEL",
    "HAS_WARNING": "HAS_WARNING",
    "HAS_KEYWORD": "HAS_KEYWORD",
    "INSTANCE_OF": "INSTANCE_OF",
    "CONFIRMED_REASON": "CONFIRMED_REASON",
    "USED_SOLUTION": "USED_SOLUTION",
    "RELATED_COMPONENT": "RELATED_COMPONENT",

    # 如果旧数据里以后有别名，可以继续补：
    "HAS_CAUSE": "CAUSED_BY",
    "CAUSES": "CAUSED_BY",
    "SOLVED_BY": "REPAIRED_BY",
}
if "TYPE_NAME_MAP" not in globals() or not isinstance(TYPE_NAME_MAP, dict):
    TYPE_NAME_MAP = {}
if "COLOR_MAP" not in globals() or not isinstance(COLOR_MAP, dict):
    COLOR_MAP = {}

TYPE_NAME_MAP.setdefault("System", "系统")
TYPE_NAME_MAP.setdefault("Equipment", "设备")
TYPE_NAME_MAP.setdefault("Symptom", "故障现象")
TYPE_NAME_MAP.setdefault("Cause", "故障原因")
TYPE_NAME_MAP.setdefault("Diagnosis", "诊断方法")
TYPE_NAME_MAP.setdefault("Repair", "维修方案")
TYPE_NAME_MAP.setdefault("MaintenanceCase", "维修案例")

COLOR_MAP.setdefault("System", "#0B4EA2")
COLOR_MAP.setdefault("Equipment", "#42A5F5")
COLOR_MAP.setdefault("Symptom", "#FF7043")
COLOR_MAP.setdefault("Cause", "#7E57C2")
COLOR_MAP.setdefault("Diagnosis", "#26A69A")
COLOR_MAP.setdefault("Repair", "#43A047")
COLOR_MAP.setdefault("MaintenanceCase", "#F9A825")



def normalize_label(label: str):
    return LABEL_ALIAS_MAP.get(label, label if label else "Unknown")


def normalize_relation(rel_type: str):
    return REL_ALIAS_MAP.get(rel_type, rel_type if rel_type else "UNKNOWN_REL")


def get_node_primary_type(node):
    labels = list(node.labels)
    if not labels:
        return "Unknown"

    # 取第一个标签，并映射成标准标签
    raw_label = labels[0]
    return normalize_label(raw_label)


def get_node_raw_labels(node):
    labels = list(node.labels)
    return labels if labels else ["Unknown"]


def get_node_display_name(node):
    props = dict(node)

    # MaintenanceCase 可能没有 name，只有 session_id
    return (
            props.get("name")
            or props.get("session_id")
            or props.get("title")
            or props.get("id")
            or str(node.element_id)
    )


def infer_node_size(node_type):
    size_map = {
        "Equipment": 34,
        "Subsystem": 30,
        "Component": 26,
        "Symptom": 26,
        "Reason": 26,
        "Solution": 26,
        "Tool": 22,
        "Part": 22,
        "RiskLevel": 20,
        "Warning": 20,
        "Keyword": 18,
        "MaintenanceCase": 32,
        "Unknown": 20,
    }
    return size_map.get(node_type, 22)


def element_id_of(node):
    try:
        return node.element_id
    except Exception:
        try:
            return str(node.id)
        except Exception:
            return str(id(node))


def normalize_label(labels):
    labels = list(labels)

    if "Equipment" in labels or "EquipmentType" in labels:
        return "Equipment"
    elif "Subsystem" in labels:
        return "Subsystem"
    elif "Component" in labels:
        return "Component"
    elif "Symptom" in labels:
        return "Symptom"
    elif "Reason" in labels or "Cause" in labels:
        return "Reason"
    elif "Solution" in labels:
        return "Solution"
    elif "Tool" in labels:
        return "Tool"
    elif "Part" in labels:
        return "Part"
    elif "RiskLevel" in labels:
        return "RiskLevel"
    elif "Warning" in labels:
        return "Warning"
    elif "Keyword" in labels:
        return "Keyword"
    elif "MaintenanceCase" in labels:
        return "MaintenanceCase"
    else:
        return "Unknown"


def fetch_new_import_graph_data(limit=500):
    driver = get_neo4j_driver()

    query = """
    MATCH (mc:MaintenanceCase)
    WHERE mc.name STARTS WITH 'SHIPFAULT-'
    OPTIONAL MATCH (mc)-[:INSTANCE_OF]->(sy:Symptom)
    OPTIONAL MATCH (mc)-[:CONFIRMED_REASON]->(r:Reason)
    OPTIONAL MATCH (mc)-[:USED_SOLUTION]->(so:Solution)
    OPTIONAL MATCH (mc)-[:RELATED_COMPONENT]->(c:Component)
    OPTIONAL MATCH (sub:Subsystem)-[:HAS_COMPONENT]->(c)
    OPTIONAL MATCH (eq:Equipment)-[:HAS_SUBSYSTEM]->(sub)
    OPTIONAL MATCH (sy)-[:HAS_RISK_LEVEL]->(rl:RiskLevel)
    OPTIONAL MATCH (sy)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (so)-[:USE_TOOL]->(t:Tool)
    OPTIONAL MATCH (so)-[:REPLACE_PART]->(p:Part)
    OPTIONAL MATCH (so)-[:HAS_WARNING]->(w:Warning)
    RETURN mc, sy, r, so, c, sub, eq, rl, k, t, p, w
    LIMIT $limit
    """

    nodes = []
    edges = []

    def add_node(node):
        if node is None:
            return

        labels = list(node.labels)
        props = dict(node)
        std_type = normalize_label(labels)
        label_text = props.get("name") or props.get("id") or "未命名节点"
        desc_parts = [f"{k}: {v}" for k, v in props.items() if k != "name"]

        nodes.append({
            "id": element_id_of(node),
            "label": label_text,
            "type": std_type,
            "raw_labels": labels,
            "desc": " | ".join(desc_parts) if desc_parts else "-",
            "size": 22
        })

    def add_edge(a, b, rel_type):
        if a is None or b is None:
            return
        edges.append({
            "from": element_id_of(a),
            "to": element_id_of(b),
            "label": rel_type
        })

    with driver.session() as session:
        result = session.run(query, limit=limit)
        for record in result:
            mc = record["mc"]
            sy = record["sy"]
            r = record["r"]
            so = record["so"]
            c = record["c"]
            sub = record["sub"]
            eq = record["eq"]
            rl = record["rl"]
            k = record["k"]
            t = record["t"]
            p = record["p"]
            w = record["w"]

            for node in [mc, sy, r, so, c, sub, eq, rl, k, t, p, w]:
                add_node(node)

            add_edge(mc, sy, "INSTANCE_OF")
            add_edge(mc, r, "CONFIRMED_REASON")
            add_edge(mc, so, "USED_SOLUTION")
            add_edge(mc, c, "RELATED_COMPONENT")
            add_edge(sub, c, "HAS_COMPONENT")
            add_edge(eq, sub, "HAS_SUBSYSTEM")
            add_edge(sy, rl, "HAS_RISK_LEVEL")
            add_edge(sy, k, "HAS_KEYWORD")
            add_edge(so, t, "USE_TOOL")
            add_edge(so, p, "REPLACE_PART")
            add_edge(so, w, "HAS_WARNING")

    seen_nodes = set()
    dedup_nodes = []
    for n in nodes:
        if n["id"] not in seen_nodes:
            dedup_nodes.append(n)
            seen_nodes.add(n["id"])

    seen_edges = set()
    dedup_edges = []
    for e in edges:
        key = (e["from"], e["to"], e["label"])
        if key not in seen_edges:
            dedup_edges.append(e)
            seen_edges.add(key)

    return dedup_nodes, dedup_edges


def try_parse_markdown_table(text):
    """
    从 AI 回复中提取 Markdown 表格，返回 DataFrame
    只处理标准格式：
    |列1|列2|
    |---|---|
    |a|b|
    """
    if not text:
        return None

    lines = [line.strip() for line in str(text).splitlines() if line.strip()]
    if len(lines) < 3:
        return None

    table_blocks = []
    current_block = []

    for line in lines:
        if line.startswith("|") and line.endswith("|"):
            current_block.append(line)
        else:
            if len(current_block) >= 2:
                table_blocks.append(current_block)
            current_block = []

    if len(current_block) >= 2:
        table_blocks.append(current_block)

    if not table_blocks:
        return None

    block = table_blocks[0]
    if len(block) < 3:
        return None

    header_line = block[0]
    separator_line = block[1]

    # 判断第二行是不是 Markdown 表格分隔线
    if not re.match(r'^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$', separator_line):
        return None

    def split_row(row):
        row = row.strip()
        if row.startswith("|"):
            row = row[1:]
        if row.endswith("|"):
            row = row[:-1]
        return [cell.strip() for cell in row.split("|")]

    columns = split_row(header_line)
    rows = []

    for row_line in block[2:]:
        row = split_row(row_line)
        if len(row) < len(columns):
            row += [""] * (len(columns) - len(row))
        elif len(row) > len(columns):
            row = row[:len(columns)]
        rows.append(row)

    if not columns or not rows:
        return None

    try:
        df = pd.DataFrame(rows, columns=columns)
        return df
    except Exception:
        return None


def fetch_new_import_case_rows(limit=200):
    driver = get_neo4j_driver()

    query = """
    MATCH (mc:MaintenanceCase)
    WHERE mc.name STARTS WITH 'SHIPFAULT-'
    OPTIONAL MATCH (mc)-[:INSTANCE_OF]->(sy:Symptom)
    OPTIONAL MATCH (mc)-[:CONFIRMED_REASON]->(r:Reason)
    OPTIONAL MATCH (mc)-[:USED_SOLUTION]->(so:Solution)
    OPTIONAL MATCH (mc)-[:RELATED_COMPONENT]->(c:Component)
    OPTIONAL MATCH (sub:Subsystem)-[:HAS_COMPONENT]->(c)
    OPTIONAL MATCH (eq:Equipment)-[:HAS_SUBSYSTEM]->(sub)
    RETURN
        mc.name AS case_id,
        eq.name AS equipment,
        sub.name AS subsystem,
        c.name AS component,
        sy.name AS symptom,
        r.name AS reason,
        so.name AS solution
    ORDER BY case_id
    LIMIT $limit
    """

    with driver.session() as session:
        result = session.run(query, limit=limit)
        return [dict(record) for record in result]


def fetch_graph_data_from_neo4j(limit=500):
    driver = get_neo4j_driver()

    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, r, m, type(r) AS rel_type
    LIMIT $limit
    """

    nodes = []
    edges = []

    def add_node(node):
        if node is None:
            return

        labels = list(node.labels)
        props = dict(node)
        std_type = normalize_label(labels)
        label_text = props.get("name") or props.get("id") or "未命名节点"
        desc_parts = [f"{k}: {v}" for k, v in props.items() if k != "name"]

        nodes.append({
            "id": element_id_of(node),
            "label": label_text,
            "type": std_type,
            "raw_labels": labels,
            "desc": " | ".join(desc_parts) if desc_parts else "-",
            "size": 24
        })

    with driver.session() as session:
        result = session.run(query, limit=limit)

        for record in result:
            n = record["n"]
            r = record["r"]
            m = record["m"]
            rel_type = record["rel_type"]

            add_node(n)
            add_node(m)

            if r is not None and n is not None and m is not None and rel_type is not None:
                edges.append({
                    "from": element_id_of(n),
                    "to": element_id_of(m),
                    "label": str(rel_type)
                })

    # 节点去重
    seen_nodes = set()
    dedup_nodes = []
    for n in nodes:
        if n["id"] not in seen_nodes:
            dedup_nodes.append(n)
            seen_nodes.add(n["id"])

    # 关系去重
    seen_edges = set()
    dedup_edges = []
    for e in edges:
        key = (e["from"], e["to"], e["label"])
        if key not in seen_edges:
            dedup_edges.append(e)
            seen_edges.add(key)

    return dedup_nodes, dedup_edges


def detect_table_intent(text: str) -> bool:
    if not text:
        return False
    t = text.lower()
    keywords = [
        "表格", "表形式", "表格输出", "整理成表格", "用表格", "对比表", "汇总表",
        "table", "tabular", "markdown table", "in a table"
    ]
    return any(k in t for k in keywords)


def build_c_prompt(user_input, retrieved_context, language="中文"):
    wants_table = detect_table_intent(user_input)

    if language == "中文":
        format_rule = """
6. 如果用户要求表格，必须使用标准 Markdown 表格输出
7. 表格列建议为：故障现象 | 可能原因 | 排查步骤 | 注意事项
8. 若资料未明确提及，请写“未明确提及”或“需进一步检查”
9. 不要在回答中提“B检索结果”“模块B”“知识库模块”等系统内部术语
""" if wants_table else """
6. 请使用结构化方式回答，优先使用小标题和项目符号
7. 不要在回答中提“B检索结果”“模块B”“知识库模块”等系统内部术语
"""

        return f"""
你是一名船舶设备故障诊断助手，请结合用户问题与系统检索到的维修资料进行回答。

【用户问题】
{user_input if user_input else "请结合上传内容进行故障诊断分析。"}

【参考资料】
{retrieved_context if retrieved_context else "当前未检索到足够的参考资料。"}

【回答要求】
1. 优先依据参考资料进行回答
2. 如果参考资料不足，请明确说明“根据当前资料，暂无法完全确定”
3. 不要编造未在资料中出现的具体事实
4. 尽量包含：故障现象、可能原因、排查步骤、注意事项
5. 使用中文回答
{format_rule}
"""
    else:
        format_rule = """
6. If the user requests a table, use standard Markdown table output
7. Suggested columns: Symptoms | Possible Causes | Troubleshooting Steps | Precautions
8. If the material is insufficient, write "Not clearly specified" or "Needs further inspection"
9. Do not mention internal system terms such as retrieval module, knowledge module, or B
""" if wants_table else """
6. Use a structured answer with headings and bullet points
7. Do not mention internal system terms such as retrieval module, knowledge module, or B
"""

        return f"""
You are a marine equipment fault diagnosis assistant. Answer by combining the user question and the retrieved maintenance materials.

[User Question]
{user_input if user_input else "Please analyze the uploaded content for fault diagnosis."}

[Reference Materials]
{retrieved_context if retrieved_context else "No sufficient reference materials were retrieved."}

[Requirements]
1. Prioritize the reference materials
2. If the materials are insufficient, clearly say it cannot be fully determined from the current materials
3. Do not fabricate unsupported facts
4. Try to include symptoms, possible causes, troubleshooting steps, and precautions
5. Answer in English
{format_rule}
"""


# =========================
# 1. 基础路径配置
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ffmpeg 路径
FFMPEG_BIN = os.path.join(BASE_DIR, "tools", "ffmpeg-8.0.1-full_build", "bin")
os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")

# B 模块路径
B_HAI_DIR = os.path.join(BASE_DIR, "B", "HAI")
B_SRC_DIR = os.path.join(B_HAI_DIR, "src")

if B_HAI_DIR not in sys.path:
    sys.path.insert(0, B_HAI_DIR)

if B_SRC_DIR not in sys.path:
    sys.path.insert(0, B_SRC_DIR)


def format_message_html(text):
    if not text:
        return ""
    return text.replace("\n", "<br>")


def clear_input_next_run():
    st.session_state.clear_chat_input_next_run = True

def call_b_local(text="", audio_file=None, image_file=None):
    audio_bytes = None
    image_bytes = None

    try:
        # 读取音频字节
        if audio_file is not None:
            if hasattr(audio_file, "seek"):
                audio_file.seek(0)
            audio_bytes = audio_file.read()
            if hasattr(audio_file, "seek"):
                audio_file.seek(0)

        # 读取图片字节
        if image_file is not None:
            if hasattr(image_file, "seek"):
                image_file.seek(0)
            image_bytes = image_file.read()
            if hasattr(image_file, "seek"):
                image_file.seek(0)

        # 调用 B
        context, references = retrieve_info(
            text=text or "",
            audio_bytes=audio_bytes,
            image_bytes=image_bytes
        )

        return context or "", references or []

    except Exception as e:
        st.error(f"调用 B 本地模块失败: {e}")
        st.exception(e)
        return "", []


def translate_text_with_model(text, target_lang):
    """
    使用现有 C 模块做翻译
    target_lang: '中文' 或 'English'
    """
    try:
        if target_lang == "中文":
            prompt = f"""
请把下面内容准确翻译成中文。
要求：
1. 保留原意
2. 尽量使用船舶故障诊断/维修语境
3. 不要补充原文没有的信息
4. 只输出翻译结果，不要解释

原文：
{text}
"""
        else:
            prompt = f"""
Please translate the following content into English accurately.
Requirements:
1. Preserve the original meaning
2. Use marine fault diagnosis / maintenance terminology when appropriate
3. Do not add unsupported information
4. Output translation only, no explanation

Text:
{text}
"""

        translated = chat_with_expert_multi_turn(
            session_id=f"{st.session_state.session_id}-translate",
            user_input=prompt
        )
        return translated.strip()

    except Exception as e:
        st.error(f"翻译失败: {str(e)}")
        return ""


def create_button_with_callback(button_id, icon, tooltip, callback_key):
    """创建可交互的按钮"""
    if st.button(
            icon,
            key=callback_key,
            help=tooltip,
            use_container_width=False
    ):
        return True
    return False


def handle_user_submission(user_input):
    current_lang = LANGUAGES[st.session_state.language]
    input_text = user_input.strip() if user_input else ""

    # 默认值，防止变量未定义
    context = ""
    references = []
    response = ""
    elapsed = 0

    # 危险词检测
    danger_keywords = ["爆炸", "危险", "违法", "攻击"]
    is_dangerous = any(keyword in input_text for keyword in danger_keywords)
    st.session_state.show_warning = is_dangerous

    # 用户消息展示文本
    image_source = st.session_state.get("pending_image_source")
    is_zh = st.session_state.language == "中文"

    if input_text:
        display_content = input_text
    elif st.session_state.pending_audio is not None and st.session_state.pending_image is not None:
        if image_source == "camera":
            display_content = "🎤📷 语音 + 拍照" if is_zh else "🎤📷 Audio + Camera"
        else:
            display_content = "🎤📎 语音 + 图片" if is_zh else "🎤📎 Audio + Image"
    elif st.session_state.pending_audio is not None:
        display_content = "🎤 语音输入" if is_zh else "🎤 Audio input"
    elif st.session_state.pending_image is not None:
        if image_source == "camera":
            display_content = "📷 拍照输入" if is_zh else "📷 Camera input"
        else:
            display_content = "📎 图片输入" if is_zh else "📎 Image input"
    else:
        display_content = "（空输入）" if is_zh else "(Empty input)"

    # 构造用户消息
    user_message = {
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": display_content
    }

    # 如果有图片，复制一份用于历史记录显示
    if st.session_state.pending_image is not None:
        try:
            from PIL import Image, ImageFile
            ImageFile.LOAD_TRUNCATED_IMAGES = True

            st.session_state.pending_image.seek(0)
            image = Image.open(st.session_state.pending_image)
            image_copy = image.copy()
            user_message["image"] = image_copy
        except Exception as e:
            st.error(f"图片读取失败: {str(e)}")

    # 先显示用户消息
    st.session_state.messages.append(user_message)

    # ========== 调用 B ==========
    with st.spinner("🔍 正在检索维修手册并分析输入内容..."):
        try:
            if st.session_state.pending_audio is not None and hasattr(st.session_state.pending_audio, "seek"):
                st.session_state.pending_audio.seek(0)

            if st.session_state.pending_image is not None and hasattr(st.session_state.pending_image, "seek"):
                st.session_state.pending_image.seek(0)

            context, references = call_b_local(
                text=input_text,
                audio_file=st.session_state.pending_audio,
                image_file=st.session_state.pending_image
            )

            context = context or ""
            references = references or []

        except Exception as e:
            st.error(f"调用 B 本地模块失败: {str(e)}")
            st.exception(e)
            context, references = "", []

    # ========== 调用 C ==========
    try:
        with st.spinner(current_lang["chat_analyzing"]):
            start_time = time.time()

            effective_user_input = input_text
            if not effective_user_input:
                if st.session_state.pending_audio is not None and st.session_state.pending_image is not None:
                    effective_user_input = "请结合上传的语音和图片分析故障并给出维修建议"
                elif st.session_state.pending_audio is not None:
                    effective_user_input = "请结合上传的语音内容分析故障并给出维修建议"
                elif st.session_state.pending_image is not None:
                    effective_user_input = "请结合上传的图片内容分析故障并给出维修建议"
                else:
                    effective_user_input = "请分析当前故障"

            prompt_with_lang = build_c_prompt(
                user_input=effective_user_input,
                retrieved_context=context,
                language=st.session_state.language
            )

            response = chat_with_expert_multi_turn(
                session_id=st.session_state.session_id,
                user_input=prompt_with_lang
            )

            elapsed = time.time() - start_time


    except Exception as e:
        st.error(f"调用 C 模块失败: {str(e)}")
        st.exception(e)
        response = "抱歉，当前诊断模块调用失败，请稍后重试。"
        elapsed = 0

    # 保存助手消息
    st.session_state.messages.append({
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": response,
        "original_lang": st.session_state.language,
        "translation": "",
        "translation_lang": "",
        "translation_visible": False
    })
    if not st.session_state.current_topic:
        st.session_state.current_topic = build_topic_from_messages(st.session_state.messages)

    save_current_chat_session()

    # 显示引用来源
    if references:
        st.markdown("### 📚 引用来源")
        for ref in references:
            st.markdown(
                f"**[{ref.get('n', '-')}]** "
                f"`{ref.get('source', '未知来源')}` "
                f"(页 {ref.get('page', '-')})"
            )
            preview = ref.get("content_preview", "")
            if preview:
                st.caption(preview)

        with st.sidebar:
            st.markdown("---")
            st.subheader("📚 引用来源")
            for ref in references:
                st.caption(
                    f"[{ref.get('n', '-')}] {ref.get('source', '未知来源')} (页 {ref.get('page', '-')})"
                )

    # 写日志
    if input_text and st.session_state.pending_audio is not None and st.session_state.pending_image is not None:
        log_user_input = f"[文字+语音+图片] {input_text}"
    elif input_text and st.session_state.pending_audio is not None:
        log_user_input = f"[文字+语音] {input_text}"
    elif input_text and st.session_state.pending_image is not None:
        log_user_input = f"[文字+图片] {input_text}"
    elif st.session_state.pending_audio is not None and st.session_state.pending_image is not None:
        log_user_input = "[语音+图片]"
    elif st.session_state.pending_audio is not None:
        log_user_input = "[语音]"
    elif st.session_state.pending_image is not None:
        log_user_input = "[图片]"
    else:
        log_user_input = input_text

    log_operation(
        user_input=log_user_input,
        response=response,
        response_time=elapsed
    )

    # 清空待处理输入
    st.session_state.pending_image = None
    st.session_state.pending_image_source = None
    st.session_state.pending_audio = None
    st.session_state.upload_mode = None
    st.session_state.show_uploader = False

    st.session_state.show_uploader = False
    st.session_state.show_audio_input = False
    # 下一轮清空输入框
    clear_input_next_run()

    st.rerun()


def fetch_new_import_graph_data(limit=300):
    driver = get_neo4j_driver()

    query = """
    MATCH (mc:MaintenanceCase)
    WHERE mc.name STARTS WITH 'SHIPFAULT-'
    OPTIONAL MATCH p=(mc)-[*1..3]-(n)
    WITH collect(DISTINCT mc) + collect(DISTINCT n) AS all_nodes
    UNWIND all_nodes AS node
    WITH collect(DISTINCT node) AS nodes
    UNWIND nodes AS n1
    OPTIONAL MATCH (n1)-[r]->(n2)
    WHERE n2 IN nodes
    RETURN nodes, collect(DISTINCT {
        source: elementId(n1),
        target: elementId(n2),
        type: type(r)
    }) AS rels
    LIMIT 1
    """

    with driver.session() as session:
        record = session.run(query).single()

        if not record:
            return [], []

        nodes = []
        raw_nodes = record["nodes"]
        for node in raw_nodes:
            if node is None:
                continue

            labels = list(node.labels)
            props = dict(node)

            std_type = normalize_label(labels)
            label_text = props.get("name") or props.get("id") or "未命名节点"

            desc_parts = []
            for k, v in props.items():
                if k != "name":
                    desc_parts.append(f"{k}: {v}")

            nodes.append({
                "id": element_id_of(node),
                "label": label_text,
                "type": std_type,
                "raw_labels": labels,
                "desc": " | ".join(desc_parts) if desc_parts else "-",
                "size": 22
            })

        edges = []
        raw_rels = record["rels"]
        for rel in raw_rels:
            if not rel or rel["type"] is None:
                continue
            edges.append({
                "from": rel["source"],
                "to": rel["target"],
                "label": rel["type"]
            })

        # 去重
        seen_nodes = set()
        dedup_nodes = []
        for n in nodes:
            if n["id"] not in seen_nodes:
                dedup_nodes.append(n)
                seen_nodes.add(n["id"])

        seen_edges = set()
        dedup_edges = []
        for e in edges:
            key = (e["from"], e["to"], e["label"])
            if key not in seen_edges:
                dedup_edges.append(e)
                seen_edges.add(key)

        return dedup_nodes[:limit], dedup_edges[:limit]


def fetch_new_import_case_rows(limit=100):
    driver = get_neo4j_driver()

    query = """
    MATCH (mc:MaintenanceCase)
    WHERE mc.name STARTS WITH 'SHIPFAULT-'
    OPTIONAL MATCH (mc)-[:INSTANCE_OF]->(sy:Symptom)
    OPTIONAL MATCH (mc)-[:CONFIRMED_REASON]->(r:Reason)
    OPTIONAL MATCH (mc)-[:USED_SOLUTION]->(so:Solution)
    OPTIONAL MATCH (mc)-[:RELATED_COMPONENT]->(c:Component)
    RETURN
        mc.name AS case_id,
        c.name AS component,
        sy.name AS symptom,
        r.name AS reason,
        so.name AS solution
    ORDER BY case_id
    LIMIT $limit
    """

    with driver.session() as session:
        result = session.run(query, limit=limit)
        return [dict(record) for record in result]


import os
import re
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors


def generate_ai_report_for_session(session_obj):
    try:
        messages = session_obj.get("messages", []) or []
        topic = session_obj.get("topic", "未命名主题")
        language = session_obj.get("language", "中文")
        ship_imo = session_obj.get("ship_imo", "")

        if not messages:
            return "当前会话没有可用于生成报告的对话内容。"

        dialogue_lines = []
        for msg in messages:
            role = msg.get("role", "")
            content = str(msg.get("content", "")).strip()
            if not content:
                continue

            if role == "user":
                dialogue_lines.append(f"用户：{content}")
            elif role == "assistant":
                dialogue_lines.append(f"助手：{content}")
            else:
                dialogue_lines.append(f"{role}：{content}")

        dialogue_text = "\n".join(dialogue_lines).strip()
        if not dialogue_text:
            return "当前会话没有有效对话内容，无法生成报告。"

        prompt = f"""
        请根据以下完整对话内容，生成一份结构化的故障分析报告。

        输出要求：
        1. 使用{language}输出
        2. 必须输出纯文本
        3. 不要使用 Markdown 标记
        4. 不要出现 ###、##、#、**、``` 这些格式符号
        5. 即使需要分类展示，也必须用分条说明，不要使用 | 或 --- 组成表格
        6. 用专业、简洁、清晰的语言
        7. 不要遗漏关键故障信息
        8. 报告适合打印归档

        请严格按照以下结构输出：
        1. 故障主题
        2. 问题概述
        3. 用户描述的现象
        4. AI分析的可能原因
        5. 排查过程总结
        6. 建议处理方案
        7. 风险提示与注意事项
        8. 最终结论

        主题：{topic}
        船舶IMO：{ship_imo if ship_imo else "未提供"}

        完整对话：
        {dialogue_text}
        """

        report = chat_with_expert_multi_turn(
            session_id=f"report-{session_obj.get('session_id', '')}",
            user_input=prompt
        )

        if isinstance(report, str):
            return report.strip()

        return str(report).strip()

    except Exception as e:
        print(f"generate_ai_report_for_session 出错: {e}")
        return ""


def clean_markdown_text(text: str) -> str:
    if not text:
        return ""

    # 去掉 markdown 标题符号
    text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)

    # 去掉加粗符号
    text = text.replace("**", "")

    # 去掉代码块标记
    text = text.replace("```", "")

    # 列表标记替换
    text = re.sub(r'^\s*-\s*', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\*\s*', '• ', text, flags=re.MULTILINE)

    return text.strip()


def get_chinese_font_name():
    font_candidates = [
        ("SimSun", "C:/Windows/Fonts/simsun.ttc"),
        ("MicrosoftYaHei", "C:/Windows/Fonts/msyh.ttc"),
        ("SimHei", "C:/Windows/Fonts/simhei.ttf"),
        ("KaiTi", "C:/Windows/Fonts/simkai.ttf"),
    ]

    for font_name, font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
            except:
                pass

    raise Exception("未找到可用中文字体，请检查 C:/Windows/Fonts 下的中文字体。")


def generate_pdf_bytes(title, content):
    font_name = get_chinese_font_name()
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="CN_Title",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=16,
        leading=22,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceAfter=16
    )

    body_style = ParagraphStyle(
        name="CN_Body",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=10.5,
        leading=18,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceAfter=6
    )

    clean_title = clean_markdown_text(str(title))
    clean_content = clean_markdown_text(str(content))

    story = []

    safe_title = (
        clean_title.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
    story.append(Paragraph(safe_title, title_style))
    story.append(Spacer(1, 10))

    for raw_line in clean_content.split("\n"):
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue

        safe_line = (
            line.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        story.append(Paragraph(safe_line, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def build_topic_from_messages(messages):
    for msg in messages:
        if msg.get("role") == "user":
            text = str(msg.get("content", "")).strip()
            if text:
                return text[:28] + ("..." if len(text) > 28 else "")
    return "未命名主题"


def save_current_chat_session():
    messages = st.session_state.get("messages", [])
    if not messages:
        return

    has_user_msg = any(
        m.get("role") == "user" and str(m.get("content", "")).strip()
        for m in messages
    )
    if not has_user_msg:
        return

    session_id = st.session_state.get("session_id", "")
    if not session_id:
        return

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not st.session_state.current_topic:
        st.session_state.current_topic = build_topic_from_messages(messages)

    if not st.session_state.current_session_created_at:
        st.session_state.current_session_created_at = now_str

    save_chat_session(
        session_id=session_id,
        topic=st.session_state.current_topic,
        created_at=st.session_state.current_session_created_at,
        updated_at=now_str,
        ship_imo=st.session_state.get("ship_imo", ""),
        language=st.session_state.get("language", "中文"),
        messages=messages
    )


def reset_current_chat():
    st.session_state.messages = []
    st.session_state.session_id = generate_maritime_session_id(
        st.session_state.ship_imo or SHIP_IMO
    )
    st.session_state.show_warning = False
    st.session_state.pending_image = None
    st.session_state.pending_audio = None
    st.session_state.pending_image_source = None
    st.session_state.show_uploader = False
    st.session_state.show_audio_input = False
    st.session_state.chat_input_main_custom = ""
    st.session_state.current_topic = ""
    st.session_state.current_session_created_at = ""
    st.session_state.active_history_session_id = None


def load_chat_session_to_current(session_id):
    row = get_chat_session_by_id(session_id)
    session_obj = convert_session_row(row)
    if not session_obj:
        return False

    st.session_state.messages = session_obj["messages"]
    st.session_state.session_id = session_obj["session_id"]
    st.session_state.current_topic = session_obj["topic"]
    st.session_state.current_session_created_at = session_obj["created_at"]
    st.session_state.active_history_session_id = session_obj["session_id"]
    st.session_state.language = session_obj["language"] or st.session_state.language
    return True


# ─────────────────────────────────────────
# 页面基础配置（必须是第一行st命令）
# ─────────────────────────────────────────
st.set_page_config(
    page_title="船舶故障系统",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ========== 语言配置 ==========
LANGUAGES = {
    "中文": {
        "title": "船舶装备故障诊断智能问答系统",
        "sidebar_slogan": "深海之智，数据成图；海工领航，维保无忧。",
        "sidebar_subtitle": "船舶故障智能诊疗系统",
        "new_chat": "📝 新建对话",
        "export_chat": "📥 导出对话",
        "nav_chat": "💬 智能问答",
        "nav_graph": "🕸️ 知识图谱",
        "nav_records": "📋 故障记录",
        "status_title": "系统状态",
        "status_normal": "🟢 系统运行正常",
        "model_info": "🤖 模型：Qwen2.5-7B",
        "chat_title": "💬 智能问答",
        "chat_subtitle": "描述故障现象，系统将为您提供诊断建议",
        "chat_welcome": "您好！我是船舶装备故障诊断助手。请描述您遇到的故障现象，我将为您提供诊断建议。\n\n支持询问：发动机、液压系统、电气设备等常见故障。",
        "chat_placeholder": "请描述故障现象，例如：发动机冒黑烟、液压系统压力不足...",
        "chat_analyzing": "正在诊断...",
        "btn_download": "点击下载",
        "graph_title": "🕸️ 知识图谱",
        "graph_subtitle": "展示故障现象 → 故障原因 → 维修方案 的关联关系",
        "graph_search": "🔍 搜索节点",
        "graph_search_placeholder": "输入关键词，例如：发动机",
        "graph_legend": "图例：",
        "graph_legend_fault": "🔴 故障现象",
        "graph_legend_cause": "🟠 故障原因",
        "graph_legend_solution": "🟢 维修方案",
        "graph_legend_part": "🔵 零部件",
        "graph_node_count": "当前显示：{nodes} 个节点，{edges} 条关系",
        "graph_raw_data": "📄 查看原始数据",
        "graph_tab_nodes": "节点列表",
        "graph_tab_edges": "关系列表",
        "records_title": "📋 故障记录",
        "records_tab_new": "📝 新增故障记录",
        "records_tab_history": "📊 历史记录查询",
        "records_new_title": "新增故障记录",
        "records_equipment": "装备类型",
        "records_description": "故障现象描述",
        "records_description_placeholder": "例如：发动机启动困难，伴有异响",
        "records_cause": "故障原因",
        "records_cause_placeholder": "例如：燃油系统进气",
        "records_solution": "解决方案",
        "records_solution_placeholder": "例如：排气后重新启动，检查燃油管路密封",
        "btn_submit": "✅ 提交保存",
        "records_success": "✅ 故障记录保存成功！",
        "records_error": "❌ 请填写完整信息（故障现象、原因、解决方案均必填）",
        "records_history_title": "历史故障记录",
        "btn_refresh": "🔄 刷新",
        "records_empty": "暂无故障记录，请在左侧Tab新增。",
        "logs_title": "问答操作日志",
        "logs_empty": "暂无操作日志。",
        "user_label": "您",
        "assistant_label": "助手",
        "warning_text": "检测到敏感内容！请注意您的输入安全性。",
        "new_diagnosis_success": "✅ 已开启新诊断会话",
        "audio_ready": "🎤 已录制语音，可直接发送问题，或留空发送让系统仅根据语音分析",
        "image_ready": "📎 已上传图片，请输入您的问题，或留空发送让系统仅根据图片分析",
        "remove_audio": "❌ 移除语音",
        "remove_image": "❌ 移除",
        "record_audio": "点击开始录音",
        "record_success": "✅ 录音已获取，可直接发送",
        "upload_label": "选择图片文件",
        "upload_help": "支持 PNG, JPG, JPEG 格式，最大 200MB",
        "send_icon": "↑",
        "voice_icon": "🎤",
        "upload_icon": "📎",
        "translate_btn": "翻译",
        "translating": "正在翻译...",
        "translation_cn": "中文翻译",
        "translation_en": "English",
        "ship_input_title": "🚢 请输入船舶信息",
        "ship_name_label": "船名",
        "ship_imo_label": "IMO",
        "ship_info_title": "🔧 当前受诊船舶",
        "ship_order_label": "工单号",
        "ship_confirm_btn": "确认并进入系统",
        "ship_input_warning": "请完整填写船名和 IMO",
        "reset_ship_info": "🚢 重新填写船舶信息"
    },
    "English": {
        "title": "Ship Equipment Fault Diagnosis Q&A System",
        "sidebar_slogan": "Deep-Sea Intelligence, Data-Driven Insight;\nEmpowering Marine Engineering, Ensuring Reliable Maintenance.",
        "sidebar_subtitle": "Professional Ship Diagnostics AI",
        "new_chat": "📝 新建对话",
        "export_chat": "📥 Export Chat",
        "nav_chat": "💬 Smart Q&A",
        "nav_graph": "🕸️ Knowledge Graph",
        "nav_records": "📋 Fault Records",
        "status_title": "System Status",
        "status_normal": "🟢 System Running",
        "model_info": "🤖 Model: Qwen2.5-7B",
        "chat_title": "💬 Smart Q&A",
        "chat_subtitle": "Describe the fault, and the system will provide diagnostic suggestions",
        "chat_welcome": "Hello! I'm the ship equipment fault diagnosis assistant. Please describe the fault you encountered, and I will provide diagnostic suggestions.\n\nSupported queries: engine, hydraulic system, electrical equipment, etc.",
        "chat_placeholder": "Describe the fault, e.g.: engine emits black smoke, hydraulic system pressure insufficient...",
        "chat_analyzing": "Analyzing...",
        "btn_download": "Click to Download",
        "graph_title": "🕸️ Knowledge Graph",
        "graph_subtitle": "Show relationships: Fault → Cause → Solution",
        "graph_search": "🔍 Search Node",
        "graph_search_placeholder": "Enter keyword, e.g.: engine",
        "graph_legend": "Legend:",
        "graph_legend_fault": "🔴 Fault",
        "graph_legend_cause": "🟠 Cause",
        "graph_legend_solution": "🟢 Solution",
        "graph_legend_part": "🔵 Part",
        "graph_node_count": "Showing: {nodes} nodes, {edges} edges",
        "graph_raw_data": "📄 View Raw Data",
        "graph_tab_nodes": "Node List",
        "graph_tab_edges": "Edge List",
        "records_title": "📋 Fault Records",
        "records_tab_new": "📝 New Record",
        "records_tab_history": "📊 History Query",
        "records_new_title": "New Fault Record",
        "records_equipment": "Equipment Type",
        "records_description": "Fault Description",
        "records_description_placeholder": "e.g.: Engine hard to start with abnormal noise",
        "records_cause": "Fault Cause",
        "records_cause_placeholder": "e.g.: Air in fuel system",
        "records_solution": "Solution",
        "records_solution_placeholder": "e.g.: Bleed air and restart, check fuel line seal",
        "btn_submit": "✅ Submit",
        "records_success": "✅ Record saved successfully!",
        "records_error": "❌ Please fill in all required fields",
        "records_history_title": "Historical Fault Records",
        "btn_refresh": "🔄 Refresh",
        "records_empty": "No records yet. Please add from the left tab.",
        "logs_title": "Q&A Operation Logs",
        "logs_empty": "No logs yet.",
        "user_label": "You",
        "assistant_label": "Assistant",
        "warning_text": "Sensitive content detected. Please pay attention to input safety.",
        "new_diagnosis_success": "✅ New diagnosis session started",
        "audio_ready": "🎤 Voice recorded. You can send directly, or leave text empty for audio-only analysis.",
        "image_ready": "📎 Image uploaded. You can type a question, or leave text empty for image-only analysis.",
        "remove_audio": "❌ Remove Audio",
        "remove_image": "❌ Remove",
        "record_audio": "Click to start recording",
        "record_success": "✅ Recording captured. Ready to send.",
        "upload_label": "Choose an image file",
        "upload_help": "Supports PNG, JPG, JPEG, max 200MB",
        "send_icon": "↑",
        "voice_icon": "🎤",
        "upload_icon": "📎",
        "translate_btn": "Translate",
        "translating": "Translating...",
        "translation_cn": "Chinese Translation",
        "translation_en": "English",
        "ship_input_title": "🚢 Please Enter Ship Information",
        "ship_name_label": "Ship Name",
        "ship_imo_label": "IMO",
        "ship_info_title": "🔧 Current Vessel",
        "ship_order_label": "Work Order",
        "ship_confirm_btn": "Confirm and Enter",
        "ship_input_warning": "Please enter both ship name and IMO",
        "reset_ship_info": "🚢 Edit Ship Information"

    }
}

DEFAULT_SHIP_NAME = "远洋一号"
DEFAULT_SHIP_IMO = "IMO9876543"

# ─────────────────────────────────────────
# 船舶信息与时区配置
# ─────────────────────────────────────────
bj_tz = timezone(timedelta(hours=8))
SHIP_IMO = DEFAULT_SHIP_IMO


def generate_maritime_session_id(ship_imo):
    """生成船舶专用的会话ID"""
    now_str = datetime.now(bj_tz).strftime("%Y%m%d-%H%M%S")
    return f"{ship_imo}-{now_str}-{str(uuid.uuid4())[:4]}"


# ─────────────────────────────────────────
# 启动时初始化数据库
# ─────────────────────────────────────────
init_db()

# ========== 初始化Session State（完整版）==========
if "ship_name" not in st.session_state:
    st.session_state.ship_name = ""

if "ship_imo" not in st.session_state:
    st.session_state.ship_imo = ""

if "ship_info_confirmed" not in st.session_state:
    st.session_state.ship_info_confirmed = False

if "session_id" not in st.session_state:
    base_imo = st.session_state.ship_imo if st.session_state.ship_imo else SHIP_IMO
    st.session_state.session_id = generate_maritime_session_id(base_imo)

if "language" not in st.session_state:
    st.session_state.language = "中文"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_warning" not in st.session_state:
    st.session_state.show_warning = False

if "pending_image" not in st.session_state:
    st.session_state.pending_image = None

if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = False

if "show_audio_input" not in st.session_state:
    st.session_state.show_audio_input = False

if "pending_audio" not in st.session_state:
    st.session_state.pending_audio = None
if "pending_image_source" not in st.session_state:
    st.session_state.pending_image_source = None

if "chat_input_main_custom" not in st.session_state:
    st.session_state.chat_input_main_custom = ""

if "clear_chat_input_next_run" not in st.session_state:
    st.session_state.clear_chat_input_next_run = False
if "upload_mode" not in st.session_state:
    st.session_state.upload_mode = None
if "current_topic" not in st.session_state:
    st.session_state.current_topic = ""

if "current_session_created_at" not in st.session_state:
    st.session_state.current_session_created_at = ""

if "active_history_session_id" not in st.session_state:
    st.session_state.active_history_session_id = None

if "selected_chat_session_id" not in st.session_state:
    st.session_state.selected_chat_session_id = None

if "generated_report_for_view" not in st.session_state:
    st.session_state.generated_report_for_view = ""

# ========== 处理语言切换参数 ==========
query_params = st.query_params
if "switch_lang" in query_params:
    new_lang = query_params["switch_lang"]

    if isinstance(new_lang, list):
        new_lang = new_lang[0]

    if new_lang in LANGUAGES and new_lang != st.session_state.language:
        st.session_state.language = new_lang
        st.session_state.show_warning = False

        if len(st.session_state.messages) > 0 and st.session_state.messages[0].get("type") == "welcome":
            st.session_state.messages[0]["content"] = LANGUAGES[new_lang]["chat_welcome"]

    st.query_params.clear()
    st.rerun()

# 获取当前语言文本
lang = LANGUAGES[st.session_state.language]
# ========== 首次进入先填写船舶信息 ==========
if not st.session_state.ship_info_confirmed:

    st.markdown("""
    <style>
    /* 隐藏默认菜单和页脚 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 主体背景 */
    .stApp {
        background: linear-gradient(180deg, #0b2c66 0%, #123f8a 28%, #eaf2fb 28%, #f4f8fd 100%);
    }

    /* 主内容区域 */
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1200px;
    }

    /* 顶部横幅 */
    .portal-hero {
        position: relative;
        height: 280px;
        border-radius: 0 0 28px 28px;
        background:
            linear-gradient(rgba(10, 35, 85, 0.72), rgba(10, 35, 85, 0.72)),
            linear-gradient(135deg, #174ea6 0%, #0b2c66 100%);
        overflow: hidden;
        box-shadow: 0 10px 28px rgba(0,0,0,0.18);
        margin-bottom: 28px;
    }

    .portal-hero::before {
        content: "";
        position: absolute;
        inset: 0;
        background:
            radial-gradient(circle at 20% 30%, rgba(255,255,255,0.16), transparent 28%),
            radial-gradient(circle at 80% 20%, rgba(255,255,255,0.10), transparent 24%),
            radial-gradient(circle at 60% 75%, rgba(255,255,255,0.08), transparent 22%);
        pointer-events: none;
    }
    .portal-hero-inner {
        position: relative;
        z-index: 2;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 36px 42px;
    }


    .portal-title {
        font-size: 48px;
        font-weight: 900;
        margin-bottom: 14px;
        letter-spacing: 3px;
        line-height: 1.2;
        text-align: center;
        font-family: "STZhongsong", "STSong", "KaiTi", "Microsoft YaHei", serif;

        background: linear-gradient(
            135deg,
            rgba(255,255,255,0.95) 0%,
            rgba(220,236,255,0.92) 18%,
            rgba(154,205,255,0.95) 40%,
            rgba(255,255,255,0.98) 62%,
            rgba(129,190,255,0.92) 82%,
            rgba(255,255,255,0.95) 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;

        text-shadow:
            0 2px 8px rgba(255,255,255,0.18),
            0 6px 18px rgba(11,44,102,0.28);

        position: relative;
    }

    .portal-subtitle {
        color: rgba(255,255,255,0.92);
        font-size: 17px;
        line-height: 1.8;
        max-width: 760px;
    }

    .portal-tag {
        display: inline-block;
        width: fit-content;
        margin-bottom: 18px;
        padding: 8px 16px;
        border-radius: 999px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.18);
        color: #dcecff;
        font-size: 13px;
        font-weight: 600;
        backdrop-filter: blur(6px);
    }

    /* 内容卡片 */
    .entry-card {
        background: rgba(255,255,255,0.86);
        border: 1px solid rgba(34, 92, 180, 0.12);
        border-radius: 22px;
        padding: 26px 26px 22px 26px;
        box-shadow: 0 10px 28px rgba(15, 40, 90, 0.10);
        backdrop-filter: blur(6px);
        margin-top: -50px;
        position: relative;
        z-index: 5;
    }

    .entry-title {
        font-size: 28px;
        font-weight: 800;
        color: #163a70;
        margin-bottom: 10px;
    }

    .entry-desc {
        color: #50627e;
        font-size: 15px;
        line-height: 1.8;
        margin-bottom: 20px;
    }

    .entry-highlight {
        color: #1b4ea1;
        font-weight: 700;
    }

    /* 分区标题 */
    .form-section-title {
        font-size: 18px;
        font-weight: 700;
        color: #163a70;
        margin: 4px 0 14px 0;
        padding-left: 12px;
        border-left: 4px solid #2f67c7;
    }

    /* Streamlit 输入框美化 */
    div[data-baseweb="input"] > div {
        background: #ffffff !important;
        border: 1px solid rgba(47, 103, 199, 0.18) !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }

    div[data-baseweb="input"] input {
        color: #163a70 !important;
        font-size: 15px !important;
    }

    /* 表单提交按钮 */
    div.stFormSubmitButton > button {
        width: 100%;
        height: 48px;
        border: none !important;
        border-radius: 12px !important;
        background: linear-gradient(90deg, #1d5fd1 0%, #0b78d1 100%) !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 18px rgba(29,95,209,0.25) !important;
        transition: all 0.2s ease !important;
    }

    div.stFormSubmitButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(29,95,209,0.32) !important;
    }

    /* 底部提示卡 */
    .portal-note {
        margin-top: 18px;
        padding: 14px 16px;
        border-radius: 14px;
        background: linear-gradient(90deg, rgba(47,103,199,0.08), rgba(11,120,209,0.08));
        border: 1px solid rgba(47,103,199,0.12);
        color: #4b5f7d;
        font-size: 14px;
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="portal-hero">
        <div class="portal-hero-inner">
            <div class="portal-tag">⚓ 船舶智能诊断入口</div>
            <div class="portal-title">船舶智能诊断系统</div>
            <div class="portal-subtitle">
                面向船舶设备故障分析、远程诊断与维修支持场景，
                提供基于船舶身份信息的会话初始化与智能诊断入口。
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="entry-card">
        <div class="entry-title">点击进入智能诊断入口</div>
        <div class="entry-desc">
            请先填写 <span class="entry-highlight">船名</span> 与
            <span class="entry-highlight">IMO 编号</span>，
            系统将据此创建本次诊断工单与独立会话。
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="form-section-title">船舶基础信息录入</div>', unsafe_allow_html=True)

    with st.form("ship_info_form"):
        col1, col2 = st.columns(2)

        with col1:
            ship_name_input = st.text_input(
                "船名",
                value=st.session_state.ship_name,
                placeholder="例如：远洋一号"
            )

        with col2:
            ship_imo_input = st.text_input(
                "IMO",
                value=st.session_state.ship_imo,
                placeholder="例如：IMO9876543"
            )

        confirm_ship_info = st.form_submit_button("确认并进入系统")

    st.markdown("""
        <div class="portal-note">
            提示：首次进入仅需完成一次船舶信息登记。
        </div>
    </div>
    """, unsafe_allow_html=True)

    if confirm_ship_info:
        ship_name_input = ship_name_input.strip()
        ship_imo_input = ship_imo_input.strip().upper()

        if not ship_name_input or not ship_imo_input:
            st.warning("请完整填写船名和 IMO")
        else:
            st.session_state.ship_name = ship_name_input
            st.session_state.ship_imo = ship_imo_input
            st.session_state.ship_info_confirmed = True
            st.session_state.session_id = generate_maritime_session_id(ship_imo_input)
            st.rerun()

    st.stop()

# ─────────────────────────────────────────
# 页面1：智能问答（整合十轮记忆 + 船舶单子传递）
# ─────────────────────────────────────────
import textwrap
import base64

st.markdown("""
<style>
.welcome-panel {
    min-height: 58vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 40px 20px 120px 20px;
}

.welcome-logo {
    width: 88px;
    height: 88px;
    object-fit: contain;
    margin-bottom: 20px;
    filter: drop-shadow(0 8px 24px rgba(40,120,220,0.16));
}

.welcome-title {
    font-size: 32px;
    font-weight: 800;
    color: #1F2D3D;
    margin-bottom: 12px;
}

.welcome-subtitle {
    font-size: 15px;
    color: #6B7A90;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)


def get_base64_svg(svg_path):
    with open(svg_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


svg_base64 = get_base64_svg(os.path.join(_SERVICEO_ROOT, "pic", "11.svg"))
import html
import streamlit as st

st.markdown(f"""
<style>
/* =========================================================
   SIDEBAR · LIGHTER REFINED VERSION
   ========================================================= */

/* ===== 主背景：整体调浅 ===== */
section[data-testid="stSidebar"] {{
    background:
        radial-gradient(circle at 14% 8%, rgba(170, 228, 255, 0.18) 0%, rgba(170, 228, 255, 0.00) 26%),
        radial-gradient(circle at 88% 14%, rgba(156, 182, 255, 0.15) 0%, rgba(156, 182, 255, 0.00) 28%),
        linear-gradient(180deg, #123A78 0%, #2B5FA8 42%, #4C88D1 100%);
    position: relative;
    overflow: hidden;
    animation: sidebarSlideIn 0.72s ease-out;
    border-right: 1px solid rgba(210, 235, 255, 0.12);
}}

/* ===== 底部船舶背景纹理 ===== */
section[data-testid="stSidebar"]::after {{
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 14px;
    height: 250px;
    background-image: url("data:image/svg+xml;base64,{svg_base64}");
    background-repeat: no-repeat;
    background-position: center bottom;
    background-size: 72%;
    opacity: 0.11;
    pointer-events: none;
    z-index: 1;
}}

/* ===== 柔和流光 ===== */
section[data-testid="stSidebar"]::before {{
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(
            120deg,
            rgba(255,255,255,0.00) 0%,
            rgba(255,255,255,0.06) 16%,
            rgba(255,255,255,0.015) 34%,
            rgba(255,255,255,0.00) 52%,
            rgba(255,255,255,0.04) 72%,
            rgba(255,255,255,0.00) 100%
        );
    background-size: 220% 220%;
    animation: sidebarGlowFlow 10s ease-in-out infinite;
    pointer-events: none;
    z-index: 1;
}}

section[data-testid="stSidebar"] > div {{
    position: relative;
    z-index: 2;
}}

/* ===== 内容边距 ===== */
section[data-testid="stSidebar"] .block-container {{
    padding-top: 0.55rem !important;
    padding-bottom: 1.35rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}}

/* ===== 字体基础色 ===== */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] * {{
    color: #F2F8FF;
}}

/* ===== 滚动条 ===== */
section[data-testid="stSidebar"] ::-webkit-scrollbar {{
    width: 8px;
}}
section[data-testid="stSidebar"] ::-webkit-scrollbar-track {{
    background: transparent;
}}
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{
    background: linear-gradient(180deg, rgba(180,224,255,0.38) 0%, rgba(113,174,241,0.34) 100%);
    border-radius: 999px;
}}

/* ===== 动画 ===== */
@keyframes sidebarSlideIn {{
    from {{
        transform: translateX(-52px);
        opacity: 0;
    }}
    to {{
        transform: translateX(0);
        opacity: 1;
    }}
}}

@keyframes sidebarGlowFlow {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

@keyframes floatSoft {{
    0% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-3px); }}
    100% {{ transform: translateY(0px); }}
}}

/* =========================================================
   品牌区
   ========================================================= */
.sidebar-brand-shell {{
    position: relative;
    margin-bottom: 14px;
    padding: 2px 4px 0 4px;
}}

.sidebar-brand-block {{
    position: relative;
    margin: 0 0 10px 0;
    padding: 4px 6px 0 6px;
}}

.sidebar-brand-logo-wrap {{
    display: flex;
    align-items: center;
    justify-content: flex-start;
    margin-bottom: 10px;
}}

.sidebar-brand-logo {{
    width: 56px;
    height: 56px;
    object-fit: contain;
    display: block;
    filter: drop-shadow(0 8px 16px rgba(255,255,255,0.16));
    animation: floatSoft 4.5s ease-in-out infinite;
}}

.sidebar-brand-title {{
    color: #FFFFFF;
    font-size: 38px;
    font-weight: 900;
    line-height: 1.02;
    letter-spacing: 1.2px;
    margin: 0 0 8px 0;
    text-shadow:
        0 3px 12px rgba(0,0,0,0.12),
        0 0 8px rgba(255,255,255,0.06);
}}

.sidebar-brand-slogan {{
    margin: 0 0 10px 0;
    font-size: 15px;
    font-weight: 900;
    line-height: 1.5;
    letter-spacing: 0.2px;
    white-space: normal;
    background: linear-gradient(90deg, #FFFFFF 0%, #D9F0FF 35%, #A8DEFF 65%, #FFFFFF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    color: transparent;
    text-shadow:
        0 0 16px rgba(140, 210, 255, 0.12),
        0 2px 8px rgba(0,0,0,0.08);
}}

.sidebar-brand-line {{
    height: 1px;
    border: none;
    background: linear-gradient(
        90deg,
        rgba(255,255,255,0.00) 0%,
        rgba(190,226,255,0.28) 50%,
        rgba(255,255,255,0.00) 100%
    );
    margin: 10px 0 10px 0;
}}

.sidebar-brand-subtitle {{
    color: rgba(243, 249, 255, 0.95);
    font-size: 15px;
    font-weight: 800;
    line-height: 1.25;
    margin: 0 0 16px 0;
    letter-spacing: 0.35px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-shadow: 0 2px 8px rgba(0,0,0,0.10);
}}

/* =========================================================
   按钮系统
   ========================================================= */
section[data-testid="stSidebar"] .stButton,
section[data-testid="stSidebar"] .stDownloadButton {{
    width: 100%;
    margin-bottom: 12px;
}}

section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] .stDownloadButton > button {{
    position: relative;
    overflow: hidden;
    width: 100%;
    min-height: 50px;
    border-radius: 20px;
    border: 1px solid rgba(210, 235, 255, 0.20) !important;
    background: linear-gradient(90deg, #3A7BE6 0%, #48A0ED 100%) !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 16px !important;
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.12),
        0 12px 24px rgba(10, 42, 100, 0.16) !important;
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease !important;
}}

section[data-testid="stSidebar"] .stButton > button::before,
section[data-testid="stSidebar"] .stDownloadButton > button::before {{
    content: "";
    position: absolute;
    top: 0;
    left: -130%;
    width: 88%;
    height: 100%;
    transform: skewX(-20deg);
    background: linear-gradient(
        90deg,
        rgba(255,255,255,0.00) 0%,
        rgba(255,255,255,0.18) 50%,
        rgba(255,255,255,0.00) 100%
    );
    transition: left 0.58s ease;
}}

section[data-testid="stSidebar"] .stButton > button:hover,
section[data-testid="stSidebar"] .stDownloadButton > button:hover {{
    transform: translateY(-2px);
    background: linear-gradient(90deg, #4A89EE 0%, #58ACEF 100%) !important;
    border-color: rgba(225, 242, 255, 0.32) !important;
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.12),
        0 16px 30px rgba(10, 42, 100, 0.20) !important;
}}

section[data-testid="stSidebar"] .stButton > button:hover::before,
section[data-testid="stSidebar"] .stDownloadButton > button:hover::before {{
    left: 118%;
}}

section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button span,
section[data-testid="stSidebar"] .stButton > button div,
section[data-testid="stSidebar"] .stDownloadButton > button p,
section[data-testid="stSidebar"] .stDownloadButton > button span,
section[data-testid="stSidebar"] .stDownloadButton > button div {{
    color: #FFFFFF !important;
    font-weight: 800 !important;
}}

/* =========================================================
   船舶信息卡：透明方框包住
   ========================================================= */
.ship-native-wrap {{
    margin-top: 16px;
    margin-bottom: 16px;
    padding: 14px;
    border-radius: 22px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(220, 238, 255, 0.18);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.08),
        0 8px 22px rgba(8, 28, 78, 0.12);
    backdrop-filter: blur(10px);
}}

.ship-native-card {{
    position: relative;
    overflow: hidden;
    padding: 18px 16px 14px 16px;
    border-radius: 18px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
}}

.ship-native-card::before {{
    content: "";
    position: absolute;
    top: -42px;
    right: -28px;
    width: 160px;
    height: 160px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(190,235,255,0.16) 0%, rgba(190,235,255,0.00) 72%);
    pointer-events: none;
}}

.ship-native-title {{
    color: #FFFFFF;
    font-size: 19px;
    font-weight: 900;
    margin-bottom: 20px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.10);
}}

.ship-native-row {{
    margin-bottom: 16px;
}}

.ship-native-row:last-of-type {{
    margin-bottom: 10px;
}}

.ship-native-label {{
    display: block;
    color: #F7FBFF;
    font-size: 17px;
    font-weight: 900;
    margin-bottom: 4px;
}}

.ship-native-inline {{
    display: flex;
    align-items: baseline;
    gap: 8px;
    flex-wrap: wrap;
}}

.ship-native-inline .ship-native-label-inline {{
    color: #F7FBFF;
    font-size: 17px;
    font-weight: 900;
}}

.ship-native-inline .ship-native-value-inline {{
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 900;
}}

.ship-native-value-block {{
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 900;
}}

.ship-native-order {{
    color: #BFE6FF;
    font-family: "Courier New", monospace;
    font-size: 14px;
    font-weight: 800;
    word-break: break-all;
    line-height: 1.6;
    margin-top: 4px;
}}

/* ===== 分割线 ===== */
.sidebar-bottom-line {{
    height: 1px;
    background: linear-gradient(
        90deg,
        rgba(255,255,255,0.02) 0%,
        rgba(190,226,255,0.34) 50%,
        rgba(255,255,255,0.02) 100%
    );
    margin-top: 18px;
    margin-bottom: 10px;
}}

section[data-testid="stSidebar"] hr {{
    border: none !important;
    height: 1px !important;
    background: linear-gradient(
        90deg,
        rgba(255,255,255,0.02) 0%,
        rgba(190,226,255,0.34) 50%,
        rgba(255,255,255,0.02) 100%
    ) !important;
    margin: 18px 0 !important;
}}

/* =========================================================
   导航区
   ========================================================= */
.sidebar-nav-title {{
    margin: 4px 0 10px 0;
    color: #EEF7FF;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}

section[data-testid="stSidebar"] [role="radiogroup"] {{
    background: linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.025) 100%);
    border: 1px solid rgba(200, 230, 255, 0.10);
    border-radius: 18px;
    padding: 8px 10px;
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.04),
        0 8px 20px rgba(7,34,88,0.08);
}}

section[data-testid="stSidebar"] [role="radiogroup"] label {{
    border-radius: 14px;
    padding: 7px 9px;
    transition: background 0.18s ease, transform 0.18s ease;
}}

section[data-testid="stSidebar"] [role="radiogroup"] label:hover {{
    background: rgba(255,255,255,0.07);
    transform: translateX(2px);
}}

section[data-testid="stSidebar"] [role="radiogroup"] p,
section[data-testid="stSidebar"] [role="radiogroup"] span {{
    color: #F2F8FF !important;
    font-weight: 700 !important;
}}

section[data-testid="stSidebar"] input[type="radio"] {{
    accent-color: #8BD0FF;
}}

/* =========================================================
   状态区
   ========================================================= */
.sidebar-status-title {{
    margin: 0 0 10px 0;
    color: #E7F4FF;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}

section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] .stCaption p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] small {{
    color: #E1F0FF !important;
}}

section[data-testid="stSidebar"] [data-testid="stAlert"] {{
    border-radius: 16px !important;
    border: 1px solid rgba(190, 226, 255, 0.16) !important;
    box-shadow: 0 10px 18px rgba(6, 23, 66, 0.10);
    overflow: hidden;
}}

section[data-testid="stSidebar"] [data-testid="stAlert"] * {{
    color: #F8FBFF !important;
}}

section[data-testid="stSidebar"] [data-testid="stAlert"][kind="success"] {{
    background: linear-gradient(135deg, rgba(46, 148, 123, 0.88) 0%, rgba(34, 110, 101, 0.92) 100%) !important;
}}

section[data-testid="stSidebar"] [data-testid="stAlert"][kind="info"] {{
    background: linear-gradient(135deg, rgba(57, 121, 201, 0.88) 0%, rgba(39, 88, 155, 0.92) 100%) !important;
}}
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    ship_name = st.session_state.ship_name if st.session_state.ship_name else DEFAULT_SHIP_NAME
    ship_imo = st.session_state.ship_imo if st.session_state.ship_imo else DEFAULT_SHIP_IMO
    order_number = st.session_state.session_id

    ship_name = html.escape(str(ship_name))
    ship_imo = html.escape(str(ship_imo))
    order_number = html.escape(str(order_number))

    # =========================================================
    # 品牌区
    # =========================================================

    def render_welcome_panel():
        welcome_title = "你好，今天有什么能帮到您" if st.session_state.language == "中文" else "Hello, how can I help you today?"
        welcome_subtitle = "请输入故障现象，或上传图片/语音进行诊断" if st.session_state.language == "中文" else "Describe the fault, or upload an image/audio for diagnosis"

        st.markdown(f"""
            <div class="welcome-panel">
                <img src="{SIDEBAR_LOGO_SVG}" style="width:280px;height:auto;display:block;margin:0 auto 24px auto;" />
                <div class="welcome-title">{welcome_title}</div>
                <div class="welcome-subtitle">{welcome_subtitle}</div>
            </div>
        """, unsafe_allow_html=True)


    st.markdown(
        f"""
        <div class="sidebar-brand-shell">
            <div class="sidebar-brand-block">
                <div class="sidebar-brand-logo-wrap">
                    <img src="{SIDEBAR_LOGO_SVG}" class="sidebar-brand-logo" style="width:220px;height:auto;display:block;margin:0 auto;" />
                </div>
                <div class="sidebar-brand-slogan">{lang.get("sidebar_slogan", "深海之智，数据成图；海工领航，维保无忧。")}</div>
                <div class="sidebar-brand-line"></div>
                <div class="sidebar-brand-subtitle">{lang.get("sidebar_subtitle", "船舶故障智能诊疗系统")}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =========================================================
    # 新建对话（保留唯一入口）
    # =========================================================
    if st.button(lang.get("new_chat", "📝 新建对话"), key="new_chat_btn", use_container_width=True):
        save_current_chat_session()
        reset_current_chat()
        st.rerun()

    # =========================================================
    # 导出对话
    # =========================================================
    export_text = ""
    for msg in st.session_state.get("messages", []):
        role = msg.get("role", "")
        content = str(msg.get("content", "")).strip()
        if role == "user":
            export_text += f"User: {content}\n\n"
        elif role == "assistant":
            export_text += f"Assistant: {content}\n\n"

    st.download_button(
        label=lang.get("export_chat", "📥 导出对话"),
        data=export_text if export_text.strip() else "No conversation yet.",
        file_name=f"chat_{st.session_state.session_id}.txt",
        mime="text/plain",
        key="export_chat_btn",
        use_container_width=True
    )

    # =========================================================
    # 当前受诊船舶信息卡
    # =========================================================
    st.markdown('<div class="ship-native-wrap"><div class="ship-native-card">', unsafe_allow_html=True)

    st.markdown(
        f'<div class="ship-native-title">{lang.get("ship_info_title", "🔧 当前受诊船舶")}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'''
        <div class="ship-native-row">
            <div class="ship-native-inline">
                <span class="ship-native-label-inline">{lang.get("ship_name_label", "船名")}:</span>
                <span class="ship-native-value-inline">{ship_name}</span>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        f'''
        <div class="ship-native-row">
            <div class="ship-native-inline">
                <span class="ship-native-label-inline">{lang.get("ship_imo_label", "IMO")}:</span>
                <span class="ship-native-value-inline">{ship_imo}</span>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        f'''
        <div class="ship-native-row">
            <div class="ship-native-label">{lang.get("ship_order_label", "工单号")}:</div>
            <div class="ship-native-order">{order_number}</div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-bottom-line"></div>', unsafe_allow_html=True)

    # =========================================================
    # 功能导航
    # =========================================================
    st.markdown('<div class="sidebar-nav-title">功能导航</div>', unsafe_allow_html=True)

    nav_options = [lang["nav_chat"], lang["nav_graph"], lang["nav_records"]]

    if "sidebar_nav_radio" not in st.session_state:
        st.session_state.sidebar_nav_radio = nav_options[0]

    # 支持从别的页面强制跳转
    if st.session_state.get("force_nav_page") in nav_options:
        st.session_state.sidebar_nav_radio = st.session_state.force_nav_page
        st.session_state.force_nav_page = None

    page = st.radio(
        "功能导航",
        nav_options,
        key="sidebar_nav_radio",
        label_visibility="collapsed"
    )

    st.markdown("---", unsafe_allow_html=True)

    # =========================================================
    # 状态区
    # =========================================================
    st.markdown(f'<div class="sidebar-status-title">{lang["status_title"]}</div>', unsafe_allow_html=True)
    st.success(lang["status_normal"])
    st.info(lang["model_info"])

# ─────────────────────────────────────────
# 5. 页面内容：根据导航选择显示不同页面
# ─────────────────────────────────────────
if page == lang["nav_chat"]:

    # ========== 自定义 CSS 样式 ==========
    st.markdown("""
    <style>
    /* =========================
       隐藏 Streamlit 默认元素
       ========================= */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* =========================
       页面整体背景
       ========================= */
    .stApp {
        background: linear-gradient(180deg, #F8FBFF 0%, #F3F8FD 100%);
    }

    /* 页面主区域 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 8rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }

    /* =========================
       聊天主容器
       ========================= */
    .chat-container {
        max-width: 980px;
        margin: 0 auto;
        padding: 10px 0 24px 0;
    }

    .chat-lane {
        max-width: 860px;
        margin: 0 auto;
    }

    /* =========================
       头像与按钮列
       ========================= */
    .avatar-tool-col {
        width: 64px;
        min-width: 64px;
    }

    .chat-avatar-wrap {
        width: 42px;
        min-width: 42px;
        display: flex;
        justify-content: center;
        align-items: flex-start;
        margin: 0 auto;
        padding-top: 22px;
    }

    .chat-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        object-fit: cover;
        background: #fff;
        border: 1px solid rgba(30, 91, 184, 0.10);
        box-shadow: 0 6px 16px rgba(15, 52, 120, 0.10);
    }

    /* 头像下方按钮容器 */
    .avatar-tool-wrap {
        margin-top: 10px;
        display: flex;
        justify-content: center;
    }

    /* =========================
       内容块
       ========================= */
    .msg-main {
        display: flex;
        flex-direction: column;
        min-width: 0;
        max-width: 680px;
    }

    .msg-main-left {
        align-items: flex-start;
    }

    .msg-main-right {
        align-items: flex-end;
    }

    /* 名称 */
    .chat-name {
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 8px;
        line-height: 1.2;
        letter-spacing: 0.2px;
    }

    .chat-name-left {
        color: #1E4E9E;
        text-align: left;
        width: 100%;
    }

    .chat-name-right {
        color: #3E6EA8;
        text-align: right;
        width: 100%;
        padding-right: 2px;
    }

    /* =========================
       通用气泡
       ========================= */
    .chat-bubble {
        position: relative;
        display: inline-block;
        width: fit-content;
        max-width: 100%;
        min-width: 110px;
        padding: 16px 20px;
        border-radius: 18px;
        background: linear-gradient(180deg, #FFFFFF 0%, #FCFDFF 100%);
        border: 1px solid rgba(30, 91, 184, 0.10);
        font-size: 15px;
        line-height: 1.82;
        color: #24364B;
        word-break: break-word;
        white-space: normal;
        box-shadow:
            0 10px 28px rgba(11, 61, 145, 0.06),
            0 2px 8px rgba(11, 61, 145, 0.03);
    }

    /* 助手气泡 */
    .assistant-message {
        border-left: 4px solid #FFB14A;
        box-shadow:
            0 10px 26px rgba(255, 177, 74, 0.08),
            0 3px 10px rgba(11, 61, 145, 0.04);
    }

    /* 用户气泡 */
    .user-message {
        border-right: 4px solid #7BB6FF;
        text-align: left;
        box-shadow:
            0 10px 26px rgba(123, 182, 255, 0.10),
            0 3px 10px rgba(11, 61, 145, 0.04);
    }

    /* 助手左尾巴 */
    .assistant-message::before {
        content: "";
        position: absolute;
        left: -10px;
        top: 16px;
        width: 0;
        height: 0;
        border-top: 10px solid transparent;
        border-bottom: 10px solid transparent;
        border-right: 10px solid #FFFFFF;
        filter: drop-shadow(-1px 1px 0 rgba(30, 91, 184, 0.08));
    }

    /* 用户右尾巴 */
    .user-message::before {
        content: "";
        position: absolute;
        right: -10px;
        top: 16px;
        width: 0;
        height: 0;
        border-top: 10px solid transparent;
        border-bottom: 10px solid transparent;
        border-left: 10px solid #FFFFFF;
        filter: drop-shadow(1px 1px 0 rgba(30, 91, 184, 0.08));
    }

    /* 翻译按钮样式 */
    .stButton button {
        background: linear-gradient(180deg, #FDFEFF 0%, #F2F8FF 100%) !important;
        border: 1px solid #C5DCF8 !important;
        border-radius: 14px !important;
        color: #1E5BB8 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 8px 14px !important;
        min-height: 40px !important;
        transition: all 0.22s ease !important;
        box-shadow: 0 6px 14px rgba(30, 91, 184, 0.06) !important;
    }

    .stButton button:hover {
        background: linear-gradient(180deg, #F3F9FF 0%, #EAF3FF 100%) !important;
        border-color: #91BFF3 !important;
        color: #0B3D91 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 18px rgba(30, 91, 184, 0.10) !important;
    }

    /* 助手翻译区 */
    .assistant-translation-box {
        margin-top: 12px;
        padding: 12px 14px;
        border-top: 1px dashed rgba(30, 91, 184, 0.16);
        background: linear-gradient(180deg, #F8FBFF 0%, #F2F8FF 100%);
        border-radius: 12px;
        color: #355E98;
    }

    /* 中文翻译提示块 */
    .translation-cn-box {
        background: linear-gradient(180deg, #F6FBF7 0%, #EEF8F1 100%);
        border: 1px solid rgba(76, 175, 80, 0.16);
        border-left: 4px solid #67B97A;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0 16px 0;
        color: #244B32;
        font-size: 14px;
        line-height: 1.75;
        box-shadow: 0 6px 18px rgba(76, 175, 80, 0.05);
        max-width: 680px;
    }

    /* 表格头卡片 */
    .assistant-table-header {
        display: inline-block;
        width: fit-content;
        max-width: 100%;
        background: linear-gradient(180deg, #FFFFFF 0%, #FCFDFF 100%);
        border: 1px solid rgba(30, 91, 184, 0.10);
        border-left: 4px solid #FFB14A;
        padding: 14px 18px;
        border-radius: 18px;
        margin: 0 0 10px 0;
        color: #24364B;
        font-size: 15px;
        line-height: 1.6;
        box-shadow:
            0 10px 26px rgba(255, 177, 74, 0.08),
            0 3px 10px rgba(11, 61, 145, 0.04);
    }

    .chat-ref-title {
        margin-top: 10px;
        margin-bottom: 4px;
        font-size: 14px;
        font-weight: 700;
        color: #42526E;
    }

    /* 列表显示 */
    .assistant-message ul,
    .assistant-message ol,
    .user-message ul,
    .user-message ol,
    .translation-cn-box ul,
    .translation-cn-box ol {
        padding-left: 1.35rem;
        margin-top: 0.45rem;
        margin-bottom: 0.6rem;
    }

    .assistant-message li,
    .user-message li,
    .translation-cn-box li {
        margin-bottom: 0.35rem;
    }

    /* 表格微调 */
    [data-testid="stTable"] {
        background: rgba(255,255,255,0.92);
        border-radius: 14px;
        padding: 8px;
    }

    /* expander 微调 */
    details {
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(30, 91, 184, 0.10);
        border-radius: 12px;
        padding: 4px 8px;
    }

    pre, code {
        border-radius: 10px !important;
    }

    /* 录音区域 */
    .audio-input-center-wrap {
        max-width: 460px;
        margin: 8px auto 18px auto;
        text-align: center;
    }

    .audio-input-title {
        font-size: 14px;
        color: #4B5F7A;
        margin-bottom: 8px;
    }

    div[data-testid="stAudioInput"] {
        max-width: 460px !important;
        margin: 0 auto !important;
    }

    div[data-testid="stAudioInput"] > div {
        border-radius: 14px !important;
        background: rgba(248, 251, 255, 0.96) !important;
        border: 1px solid rgba(30, 91, 184, 0.10) !important;
        box-shadow: 0 8px 20px rgba(15, 52, 120, 0.05) !important;
    }

    /* Markdown 表格显示优化 */
    .assistant-message table,
    .user-message table {
        width: auto !important;
        border-collapse: collapse !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
        background: #fff !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    .assistant-message th,
    .assistant-message td,
    .user-message th,
    .user-message td {
        border: 1px solid rgba(30, 91, 184, 0.12) !important;
        padding: 8px 12px !important;
        text-align: left !important;
        vertical-align: top !important;
    }

    .assistant-message th,
    .user-message th {
        background: #F4F8FF !important;
        font-weight: 700 !important;
    }

    /* camera_input 样式修复 */
    div[data-testid="stCameraInput"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    div[data-testid="stCameraInput"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    div[data-testid="stCameraInput"] > div > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    div[data-testid="stCameraInput"] video,
    div[data-testid="stCameraInput"] img,
    div[data-testid="stCameraInput"] canvas {
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    div[data-testid="stCameraInput"] button {
        background: linear-gradient(180deg, #F7FBFF 0%, #EDF5FF 100%) !important;
        border: 1px solid #B9D7F7 !important;
        border-radius: 12px !important;
        color: #1E5BB8 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(30, 91, 184, 0.06) !important;
    }
        /* Markdown 渲染区域 */
    .markdown-body {
        font-size: 15px;
        line-height: 1.82;
        color: #24364B;
        word-break: break-word;
    }

    .markdown-body p {
        margin: 0 0 0.85rem 0;
    }

    .markdown-body h1,
    .markdown-body h2,
    .markdown-body h3,
    .markdown-body h4,
    .markdown-body h5,
    .markdown-body h6 {
        margin-top: 1rem;
        margin-bottom: 0.65rem;
        line-height: 1.45;
        font-weight: 800;
        color: #173B66;
    }

    .markdown-body h1 { font-size: 24px; }
    .markdown-body h2 { font-size: 21px; }
    .markdown-body h3 { font-size: 18px; }
    .markdown-body h4 { font-size: 16px; }

    .markdown-body strong {
        font-weight: 800;
        color: #173B66;
    }

    .markdown-body em {
        font-style: italic;
    }

    .markdown-body blockquote {
        margin: 10px 0;
        padding: 10px 14px;
        border-left: 4px solid #A7C8F2;
        background: #F6FAFF;
        border-radius: 10px;
        color: #42526E;
    }

    .markdown-body hr {
        border: none;
        border-top: 1px solid rgba(30, 91, 184, 0.14);
        margin: 16px 0;
    }

    .markdown-body code {
        background: #F4F7FB;
        padding: 2px 6px;
        border-radius: 6px;
        font-size: 13px;
        color: #A33D1F;
    }

    .markdown-body pre {
        background: #F7FAFE;
        border: 1px solid rgba(30, 91, 184, 0.10);
        padding: 12px 14px;
        border-radius: 12px;
        overflow-x: auto;
        margin: 10px 0;
    }

    .markdown-body pre code {
        background: transparent;
        padding: 0;
        color: #24364B;
    }

    .markdown-body table {
        width: auto !important;
        border-collapse: collapse !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
        background: #fff !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    .markdown-body th,
    .markdown-body td {
        border: 1px solid rgba(30, 91, 184, 0.12) !important;
        padding: 8px 12px !important;
        text-align: left !important;
        vertical-align: top !important;
    }

    .markdown-body th {
        background: #F4F8FF !important;
        font-weight: 700 !important;
    }


    div[data-testid="stCameraInput"] button:hover {
        background: linear-gradient(180deg, #EEF6FF 0%, #E4F0FF 100%) !important;
        border-color: #7EB7F0 !important;
        color: #0B3D91 !important;
    }

    div[data-testid="stCameraInput"] [data-testid="stImage"],
    div[data-testid="stCameraInput"] [data-testid="stMarkdownContainer"],
    div[data-testid="stCameraInput"] [data-testid="stCaptionContainer"] {
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ========== 安全警告横幅 ==========
    if st.session_state.show_warning:
        st.markdown(f"""
        <div class="warning-banner">
            <span style="font-size: 24px;">⚠️</span>
            <span style="font-size: 15px; font-weight: 600;">{lang["warning_text"]}</span>
        </div>
        """, unsafe_allow_html=True)

    if not st.session_state.messages:
        render_welcome_panel()
    else:
        seen_ids = set()
        for i, msg in enumerate(st.session_state.messages):
            if "id" not in msg or not msg["id"] or msg["id"] in seen_ids:
                msg["id"] = str(uuid.uuid4())
            seen_ids.add(msg["id"])

    # ========== 显示历史消息 ==========
    st.markdown('<div class="chat-container"><div class="chat-lane">', unsafe_allow_html=True)

    seen_ids = set()
    for i, msg in enumerate(st.session_state.messages):
        if "id" not in msg or not msg["id"] or msg["id"] in seen_ids:
            msg["id"] = str(uuid.uuid4())
        seen_ids.add(msg["id"])

    render_seq = 0

    for idx, msg in enumerate(st.session_state.messages):
        role = msg.get("role", "")
        content_text = str(msg.get("content", "")).replace("\r\n", "\n").strip()

        # =========================
        # assistant：左侧，头像下方放翻译按钮
        # =========================
        if role == "assistant":
            original_lang = msg.get("original_lang", "中文")
            translation_visible = msg.get("translation_visible", False)
            translation = msg.get("translation", "")
            translation_lang = msg.get("translation_lang", "")
            translate_btn_text = "翻译" if st.session_state.language == "中文" else "Translate"

            table_df = looks_like_markdown_table(content_text)

            render_seq += 1
            button_key = f"translate_btn_{st.session_state.session_id}_{idx}_{render_seq}"

            # 左：头像+按钮；右：消息体
            left_col, body_col, spacer_col = st.columns([0.9, 8.1, 1.0], vertical_alignment="top")

            with left_col:
                st.markdown(
                    f"""
                    <div class="chat-avatar-wrap">
                        <img src="{ASSISTANT_AVATAR_SVG}" class="chat-avatar" />
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(translate_btn_text, key=button_key):
                    if st.session_state.messages[idx].get("translation_visible", False):
                        st.session_state.messages[idx]["translation_visible"] = False
                    else:
                        target_lang = "English" if original_lang == "中文" else "中文"

                        if (
                                not st.session_state.messages[idx].get("translation")
                                or st.session_state.messages[idx].get("translation_lang") != target_lang
                        ):
                            with st.spinner("正在翻译..." if st.session_state.language == "中文" else "Translating..."):
                                translated_text = translate_text_with_model(msg["content"], target_lang)

                            st.session_state.messages[idx]["translation"] = translated_text
                            st.session_state.messages[idx]["translation_lang"] = target_lang

                        st.session_state.messages[idx]["translation_visible"] = True

                    st.rerun()

            with body_col:
                if table_df is None:
                    assistant_html = markdown_to_html(content_text)

                    if original_lang == "中文" and translation_visible and translation and translation_lang == "English":
                        assistant_html += f"""
                        <div class="assistant-translation-box">
                            <b>English:</b><br>{markdown_to_html(translation)}
                        </div>
                        """

                    st.markdown(
                        f"""
                        <div class="msg-main msg-main-left">
                            <div class="chat-name chat-name-left">{lang.get("assistant_label", "Assistant")}</div>
                            <div class="chat-bubble assistant-message markdown-body">
                                {assistant_html}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                else:
                    st.markdown(
                        f"""
                        <div class="msg-main msg-main-left">
                            <div class="chat-name chat-name-left">{lang.get("assistant_label", "Assistant")}</div>
                            <div class="assistant-table-header">表格内容</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.table(table_df)

                    with st.expander("查看原始文本", expanded=False):
                        st.code(content_text, language="markdown")

                    if translation_visible and translation:
                        st.markdown("**翻译内容：**")
                        st.markdown(translation)

                refs = msg.get("references", [])
                if refs:
                    st.markdown('<div class="chat-ref-title">📚 引用来源</div>', unsafe_allow_html=True)
                    for ref in refs:
                        st.caption(
                            f"[{ref.get('n', '-')}] {ref.get('source', '未知来源')} (页 {ref.get('page', '-')})"
                        )

            with spacer_col:
                st.empty()

            if table_df is None and original_lang == "English" and translation_visible and translation and translation_lang == "中文":
                trans_left, trans_body, trans_spacer = st.columns([0.9, 8.1, 1.0], vertical_alignment="top")
                with trans_body:
                    st.markdown(
                        f"""
                        <div class="translation-cn-box markdown-body">
                            <b>中文翻译：</b><br>{markdown_to_html(translation)}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


        # =========================
        # user：右侧，头像贴着气泡尾巴
        # =========================
        elif role == "user":
            # 左留白 | 消息体 | 头像
            left_space, body_col, avatar_col = st.columns([3.9, 5.55, 0.55], vertical_alignment="top")

            with body_col:
                user_html = markdown_to_html(content_text)

                st.markdown(
                    f"""
                    <div class="msg-main msg-main-right">
                        <div class="chat-name chat-name-right">{lang["user_label"]}</div>
                        <div class="chat-bubble user-message">{user_html}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if "image" in msg:
                    try:
                        img_left, img_right = st.columns([1.55, 1.0])
                        with img_right:
                            st.image(msg["image"], width=300)
                    except Exception as e:
                        st.error(f"图片显示失败: {str(e)}")

            with avatar_col:
                st.markdown(
                    f"""
                    <div class="chat-avatar-wrap" style="padding-top: 26px;">
                        <img src="{USER_AVATAR_SVG}" class="chat-avatar" />
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown('</div></div>', unsafe_allow_html=True)

    # ========== 图片预览 ==========
    if st.session_state.pending_image is not None:
        st.markdown('<div class="attachment-panel"><div class="attachment-card">', unsafe_allow_html=True)
        col_img, col_text, col_remove = st.columns([1.5, 7.5, 2])

        with col_img:
            try:
                from PIL import ImageFile

                ImageFile.LOAD_TRUNCATED_IMAGES = True
                st.session_state.pending_image.seek(0)
                image = Image.open(st.session_state.pending_image)
                st.image(image, width=90)
            except Exception as e:
                st.error(f"图片预览失败: {str(e)}")

    # ========== 语音录音器 ==========
    if st.session_state.show_audio_input:
        audio_input_file = st.audio_input(lang["record_audio"], key="audio_input_main")

        if audio_input_file is not None:
            if not hasattr(audio_input_file, "name"):
                audio_input_file.name = "recorded_audio.wav"
            if not hasattr(audio_input_file, "type"):
                audio_input_file.type = "audio/wav"

            st.session_state.pending_audio = audio_input_file
            st.success(lang["record_success"])

# ========== 输入区样式 ==========
st.markdown("""
<style>
.main .block-container {
    padding-bottom: 180px !important;
}

/* 附件/录音面板统一宽度 */
.attachment-panel {
    max-width: 980px;
    margin: 0 auto 12px auto;
}


/* 固定底部输入栏容器 */
.fixed-chatbar-wrap {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: min(980px, calc(100vw - 420px));
    z-index: 999;
}


/* 输入框样式 */
div[data-testid="stTextInput"] input {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #24364B !important;
    font-size: 16px !important;
    height: 46px !important;
}

/* 输入框外层 */
div[data-testid="stTextInput"] > div {
    background: transparent !important;
}

div[data-testid="stTextInput"] > div > div {
    background: transparent !important;
    border: none !important;
}

/* 固定栏里的按钮 */
.fixed-chatbar .stButton button {
    height: 46px !important;
    min-height: 46px !important;
    border-radius: 12px !important;
    background: rgba(77, 171, 247, 0.10) !important;
    border: 1px solid rgba(77, 171, 247, 0.24) !important;
    color: #69b6ff !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 0 10px !important;
    white-space: nowrap !important;
}

.fixed-chatbar .stButton button:hover {
    background: rgba(77, 171, 247, 0.18) !important;
    border-color: rgba(77, 171, 247, 0.35) !important;
}

/* uploader 和 audio input 控件区域 */
section.main div[data-testid="stFileUploader"] {
    max-width: 980px;
    margin: 0 auto 12px auto;
}

@media (max-width: 1200px) {
    .fixed-chatbar-wrap {
        width: calc(100vw - 80px);
        left: calc(50% + 120px);
        transform: translateX(-50%);
    }
}
</style>
""", unsafe_allow_html=True)
# ========== 图片来源选择区 ==========
if st.session_state.show_uploader:
    st.markdown('<div class="attachment-panel"><div class="attachment-card uploader-card">', unsafe_allow_html=True)
    st.markdown("##### 请选择图片来源" if st.session_state.language == "中文" else "##### Please choose image source")

    col1, col2, col3 = st.columns([1.2, 1.4, 6])

    with col1:
        if st.button("📷 拍照", key="choose_camera_btn", use_container_width=True):
            st.session_state.upload_mode = "camera"
            st.rerun()

    with col2:
        if st.button("🖼️ 上传文件", key="choose_file_btn", use_container_width=True):
            st.session_state.upload_mode = "file"
            st.rerun()

    if st.session_state.upload_mode == "camera":
        camera_file = st.camera_input(
            "拍照上传" if st.session_state.language == "中文" else "Take a photo",
            key="camera_input_main"
        )
        if camera_file is not None:
            st.session_state.pending_image = camera_file
            st.session_state.pending_image_source = "camera"
            st.session_state.show_uploader = False
            st.session_state.upload_mode = None
            st.rerun()

    elif st.session_state.upload_mode == "file":
        uploaded_file = st.file_uploader(
            lang["upload_label"],
            type=["png", "jpg", "jpeg"],
            key="file_uploader_main",
            help=lang["upload_help"]
        )
        if uploaded_file is not None:
            st.session_state.pending_image = uploaded_file
            st.session_state.pending_image_source = "upload"
            st.session_state.show_uploader = False
            st.session_state.upload_mode = None
            st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)

if page == lang["nav_chat"]:
    fixed_bar = st.container()
    with fixed_bar:
        st.markdown('<div class="fixed-chatbar-wrap"><div class="fixed-chatbar">', unsafe_allow_html=True)

        col_input, col_voice, col_upload, col_lang_btn, col_send = st.columns([16, 1.2, 1.2, 1.8, 1.2])
        if st.session_state.clear_chat_input_next_run:
            st.session_state.chat_input_main_custom = ""
            st.session_state.clear_chat_input_next_run = False

        with col_input:
            user_input = st.text_input(
                "消息输入框",
                key="chat_input_main_custom",
                placeholder=lang["chat_placeholder"],
                label_visibility="collapsed"
            )

        with col_voice:
            voice_clicked = st.button(lang["voice_icon"], key="voice_btn_main", use_container_width=True)

        with col_upload:
            upload_clicked = st.button(lang["upload_icon"], key="upload_btn_main", use_container_width=True)

        with col_lang_btn:
            lang_clicked = st.button(
                "🌐 EN" if st.session_state.language == "中文" else "🌐 中",
                key="lang_btn_main",
                use_container_width=True
            )

        with col_send:
            send_clicked = st.button(lang["send_icon"], key="send_btn_main", use_container_width=True)

        st.markdown('</div></div>', unsafe_allow_html=True)

    if voice_clicked:
        st.session_state.show_audio_input = not st.session_state.show_audio_input
        st.rerun()

    if upload_clicked:
        st.session_state.show_uploader = not st.session_state.show_uploader
        st.rerun()

    if lang_clicked:
        new_lang = "English" if st.session_state.language == "中文" else "中文"
        st.session_state.language = new_lang

        st.rerun()

    if send_clicked:
        if (

                (user_input and user_input.strip())
                or st.session_state.pending_image is not None
                or st.session_state.pending_audio is not None
        ):
            handle_user_submission(user_input)


# =========================================================
# 页面主体
# =========================================================
elif page == lang["nav_graph"]:

    # =====================================================
    # Session State 初始化
    # =====================================================
    if "graph_all_data" not in st.session_state:
        st.session_state["graph_all_data"] = {
            "nodes": [], "edges": [], "paths": [], "source": "", "raw": {}
        }

    if "graph_fault_tree_data" not in st.session_state:
        st.session_state["graph_fault_tree_data"] = {
            "nodes": [], "edges": [], "paths": [], "source": "", "raw": {}, "summary": {}, "worker_tips": []
        }

    if "graph_query_text" not in st.session_state:
        st.session_state["graph_query_text"] = "排烟温度高"

    if "graph_loaded_once" not in st.session_state:
        st.session_state["graph_loaded_once"] = False

    # 温度专题状态
    if "temperature_topic_data" not in st.session_state:
        st.session_state["temperature_topic_data"] = {
            "topic": "",
            "cards": [],
            "overview_fault_tree": {}
        }

    if "temperature_selected_detail" not in st.session_state:
        st.session_state["temperature_selected_detail"] = ""

    if "temperature_topic_loaded" not in st.session_state:
        st.session_state["temperature_topic_loaded"] = False

    # =====================================================
    # 头部 Banner
    # =====================================================
    graph_ok, graph_msg = get_graph_service_health()
    graph_status_text = "正常" if graph_ok else "异常"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0D47A1 0%, #42A5F5 100%);
        border-radius: 28px;
        padding: 30px 34px;
        color: white;
        box-shadow: 0 10px 24px rgba(21,101,192,0.16);
        margin-bottom: 18px;
    ">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:20px;flex-wrap:wrap;">
            <div>
                <div style="font-size: 30px; font-weight: 800; margin-bottom: 10px;">
                    船舶设备知识图谱与故障树分析平台
                </div>
                <div style="font-size: 15px; line-height: 1.85; opacity: 0.96; max-width:820px;">
                    面向设备故障定位、原因追溯、诊断建议与维修决策，支持多路径故障树分析、知识图谱关联探索。
                </div>
            </div>
            <div style="
                background:rgba(255,255,255,0.12);
                border:1px solid rgba(255,255,255,0.18);
                border-radius:18px;
                padding:14px 16px;
                min-width:220px;
            ">
                <div style="font-size:13px;opacity:0.9;">当前服务状态</div>
                <div style="font-size:20px;font-weight:800;margin-top:4px;">{graph_status_text}</div>
                <div style="font-size:12px;opacity:0.88;margin-top:6px;">{graph_msg if graph_msg else '图谱服务连接正常'}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =====================================================
    # 初次加载全图
    # =====================================================
    if not st.session_state.get("graph_loaded_once", False) and graph_ok:
        try:
            st.session_state["graph_all_data"] = fetch_all_graph_from_a()
            st.session_state["graph_loaded_once"] = True
        except Exception as e:
            st.warning(f"初始化加载图谱失败：{e}")

    all_graph_data = st.session_state.get(
        "graph_all_data",
        {"nodes": [], "edges": [], "paths": [], "source": "", "raw": {}}
    )
    all_node_df = build_node_df(all_graph_data)
    all_edge_df = build_edge_df(all_graph_data)
    type_stats_df = build_type_stats(all_node_df)
    relation_stats_df = build_relation_stats(all_edge_df)
    degree_stats_df = build_degree_stats(all_node_df, all_edge_df)

    # 顶部统计改为固定值
    overview_stats = {
        "系统覆盖数": 12,
        "设备覆盖数": 45,
        "故障现象数": 1055,
        "故障原因数": 1323,
        "维修方案数": 1680
    }

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("系统覆盖数", overview_stats["系统覆盖数"])
    with c2:
        st.metric("设备覆盖数", overview_stats["设备覆盖数"])
    with c3:
        st.metric("故障现象数", overview_stats["故障现象数"])
    with c4:
        st.metric("故障原因数", overview_stats["故障原因数"])
    with c5:
        st.metric("维修方案数", overview_stats["维修方案数"])

    st.markdown("### 节点类型图例")
    render_legend()

    tab_overview, tab_fault_tree, tab_graph, tab_query, tab_maintain, tab_analysis = st.tabs([
        "总览",
        "故障树分析",
        "知识关联图谱",
        "节点查询",
        "图谱维护",
        "诊断分析"
    ])

    # =====================================================
    # 总览
    # =====================================================
    with tab_overview:
        st.markdown("## 诊断能力总览")
        st.caption("用于查看知识库整体覆盖、结构层级与专题分析结果。")

        q1, q2 = st.columns([4, 1])

        with q1:
            quick_query = st.text_input(
                "输入故障现象，快速进入故障分析",
                value=st.session_state.get("graph_query_text", ""),
                placeholder="例如：排烟温度高 / 船舶主机温度偏高",
                key="overview_fault_query"
            )

        with q2:
            quick_search_btn = st.button("开始分析", use_container_width=True, key="overview_search_btn")

        if quick_search_btn:
            try:
                query_text = quick_query.strip()
                st.session_state["graph_query_text"] = query_text

                if query_text == "船舶主机温度偏高":
                    try:
                        topic_data = fetch_temperature_options_from_a(query_text)
                        st.session_state["temperature_topic_data"] = topic_data
                        st.session_state["temperature_topic_loaded"] = True
                    except Exception:
                        st.session_state["temperature_topic_data"] = {
                            "topic": query_text,
                            "cards": [],
                            "overview_fault_tree": {}
                        }
                        st.session_state["temperature_topic_loaded"] = False

                    st.session_state["temperature_selected_detail"] = ""
                    st.session_state["graph_fault_tree_data"] = fetch_fault_tree_from_a(query_text)

                else:
                    st.session_state["temperature_topic_loaded"] = False
                    st.session_state["temperature_topic_data"] = {
                        "topic": "",
                        "cards": [],
                        "overview_fault_tree": {}
                    }
                    st.session_state["temperature_selected_detail"] = ""
                    st.session_state["graph_fault_tree_data"] = fetch_fault_tree_from_a(query_text)

                st.success("故障分析完成，请切换到“故障树分析”查看结果。")
            except Exception as e:
                st.error(f"故障分析失败：{e}")

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            render_type_donut_chart(type_stats_df, title="知识类型构成占比")
        with row1_col2:
            render_relation_bar_chart(relation_stats_df, title="关系覆盖情况")

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.caption("提示：若系统级映射尚未建立完整，该图仅供参考。")
            render_system_sunburst_chart(all_graph_data, title="系统-设备-故障现象层级分布")
        with row2_col2:
            render_symptom_frequency_chart(all_graph_data, title="故障现象覆盖排行")

    # =====================================================
    # 故障树分析
    # =====================================================
    with tab_fault_tree:
        st.markdown("## 故障树多路径分析")

        ft1, ft2 = st.columns([4, 1])

        with ft1:
            symptom_query = st.text_input(
                "请输入故障现象",
                value=st.session_state.get("graph_query_text", ""),
                placeholder="例如：排烟温度高 / 船舶主机温度偏高 / 第3缸温度异常",
                key="fault_tree_query_input"
            )

        with ft2:
            do_fault_tree_query = st.button("开始分析", use_container_width=True, key="fault_tree_query_btn")

        suggest_kw = st.text_input("可选：先按关键词检索故障现象", value="", key="symptom_suggest_kw")

        if suggest_kw.strip():
            try:
                suggestions = search_symptom_from_a(suggest_kw, limit=8)
                if suggestions:
                    st.caption("推荐故障现象：请选择更接近现场情况的标准名称")
                    sug_cols = st.columns(2)
                    for idx, item in enumerate(suggestions):
                        with sug_cols[idx % 2]:
                            if st.button(item, key=f"suggest_symptom_{idx}", use_container_width=True):
                                st.session_state["graph_query_text"] = item

                                if item == "船舶主机温度偏高":
                                    try:
                                        topic_data = fetch_temperature_options_from_a(item)
                                        st.session_state["temperature_topic_data"] = topic_data
                                        st.session_state["temperature_topic_loaded"] = True
                                    except Exception:
                                        st.session_state["temperature_topic_data"] = {
                                            "topic": item,
                                            "cards": [],
                                            "overview_fault_tree": {}
                                        }
                                        st.session_state["temperature_topic_loaded"] = False

                                    st.session_state["temperature_selected_detail"] = ""
                                    st.session_state["graph_fault_tree_data"] = fetch_fault_tree_from_a(item)

                                elif item == "第3缸温度异常":
                                    detail_data = fetch_temperature_detail_from_a(item)
                                    st.session_state["temperature_selected_detail"] = item
                                    st.session_state["graph_fault_tree_data"] = detail_data

                                else:
                                    st.session_state["temperature_topic_loaded"] = False
                                    st.session_state["temperature_topic_data"] = {
                                        "topic": "",
                                        "cards": [],
                                        "overview_fault_tree": {}
                                    }
                                    st.session_state["temperature_selected_detail"] = ""
                                    st.session_state["graph_fault_tree_data"] = fetch_fault_tree_from_a(item)

                                st.success(f"已按推荐故障现象“{item}”完成分析")
                                st.rerun()
                else:
                    st.caption("未找到匹配故障现象")
            except Exception as e:
                st.warning(f"症状联想失败：{e}")

        if do_fault_tree_query:
            try:
                query_text = symptom_query.strip()
                st.session_state["graph_query_text"] = query_text

                if query_text == "船舶主机温度偏高":
                    try:
                        topic_data = fetch_temperature_options_from_a(query_text)
                        st.session_state["temperature_topic_data"] = topic_data
                        st.session_state["temperature_topic_loaded"] = True
                    except Exception:
                        st.session_state["temperature_topic_data"] = {
                            "topic": query_text,
                            "cards": [],
                            "overview_fault_tree": {}
                        }
                        st.session_state["temperature_topic_loaded"] = False

                    main_fault_tree = fetch_fault_tree_from_a(query_text)
                    st.session_state["temperature_selected_detail"] = ""
                    st.session_state["graph_fault_tree_data"] = main_fault_tree

                elif query_text == "第3缸温度异常":
                    detail_data = fetch_temperature_detail_from_a(query_text)
                    st.session_state["temperature_topic_loaded"] = False
                    st.session_state["temperature_selected_detail"] = query_text
                    st.session_state["graph_fault_tree_data"] = detail_data

                else:
                    st.session_state["temperature_topic_loaded"] = False
                    st.session_state["temperature_topic_data"] = {
                        "topic": "",
                        "cards": [],
                        "overview_fault_tree": {}
                    }
                    st.session_state["temperature_selected_detail"] = ""
                    st.session_state["graph_fault_tree_data"] = fetch_fault_tree_from_a(query_text)

                st.success("故障树分析完成")

            except Exception as e:
                st.session_state["graph_fault_tree_data"] = {
                    "nodes": [],
                    "edges": [],
                    "paths": [],
                    "source": "fault-tree",
                    "raw": {},
                    "summary": {},
                    "worker_tips": []
                }
                st.error(f"故障树分析失败：{e}")

        fault_tree_data = st.session_state.get("graph_fault_tree_data", {
            "nodes": [], "edges": [], "paths": [], "source": "", "raw": {}, "summary": {}, "worker_tips": []
        })
        ft_path_df = build_path_df(fault_tree_data)
        ft_summary = fault_tree_data.get("summary", {}) or {}

        if st.session_state.get("graph_query_text", "") == "船舶主机温度偏高" and not st.session_state.get("temperature_selected_detail", ""):
            st.markdown("""
            <div style="
                background:#F8FBFF;border:1px solid #DCE9F8;border-radius:18px;
                padding:14px 16px;margin:10px 0 12px 0;">
                <div style="font-size:13px;color:#58708B;">当前分析对象</div>
                <div style="font-size:20px;font-weight:800;color:#173B7A;">船舶主机温度偏高</div>
            </div>
            """, unsafe_allow_html=True)

        elif st.session_state.get("temperature_selected_detail", ""):
            st.markdown(f"""
            <div style="
                background:#EEF5FF;border:1px solid #CFE0FA;border-radius:18px;padding:14px 16px;
                margin:10px 0 12px 0;">
                <div style="font-size:13px;color:#58708B;">当前专题详情</div>
                <div style="font-size:20px;font-weight:800;color:#173B7A;">{st.session_state.get("temperature_selected_detail", "")}</div>
            </div>
            """, unsafe_allow_html=True)

        render_fault_summary_cards(ft_summary)
        render_worker_action_panel(fault_tree_data)

        if ft_path_df.empty:
            st.warning(
                "当前未检索到有效故障树路径。请优先从上方推荐故障现象中选择更标准的名称，或补充报警代码、异常声音、温度/压力/电流变化、发生工况等信息。"
            )
            render_compact_empty_card(
                "故障树分析视图",
                "当前没有可展示的故障路径结构，因此不显示空白图区域。建议先选择更标准的故障现象再分析。"
            )
        else:
            st.markdown("### 故障树结构总览")
            current_symptom_name = st.session_state.get("temperature_selected_detail", "") or st.session_state.get("graph_query_text", "")
            render_fault_tree_html(
                ft_path_df,
                symptom_name=current_symptom_name,
                topic_name="船舶主机温度偏高专题" if (
                    st.session_state.get("graph_query_text", "") == "船舶主机温度偏高"
                    or st.session_state.get("temperature_selected_detail", "")
                ) else ""
            )

            st.markdown("### 多路径流向分析")
            current_title = st.session_state.get("temperature_selected_detail", "") or st.session_state.get("graph_query_text", "")
            render_fault_sankey_chart(ft_path_df, title=f"{current_title} 流向分析")

            st.markdown("### 详细故障路径卡片")
            render_fault_tree_cards(ft_path_df)

            render_recommendation_panel(ft_path_df)

            st.caption("下图展示当前故障相关的结构关系，优先使用后端返回的真实图谱关系。")
            st.markdown("### 故障树关联结构图")
            render_pyvis_graph(fault_tree_data, height=660, hierarchical=True, show_title=False)

        # 仅在搜索“船舶主机温度偏高”后显示其分支按钮
        if (
            st.session_state.get("temperature_topic_loaded", False)
            and st.session_state.get("temperature_topic_data", {}).get("cards")
            and st.session_state.get("graph_query_text", "") == "船舶主机温度偏高"
        ):
            clicked_name = render_temperature_topic_buttons(
                st.session_state.get("temperature_topic_data", {}).get("cards", []),
                selected_name=st.session_state.get("temperature_selected_detail", "")
            )

            if clicked_name:
                try:
                    detail_data = fetch_temperature_detail_from_a(clicked_name)
                    st.session_state["temperature_selected_detail"] = clicked_name
                    st.session_state["graph_fault_tree_data"] = detail_data
                    st.success(f"已切换到“{clicked_name}”故障树")
                    st.rerun()
                except Exception as e:
                    st.error(f"加载专题详情失败：{e}")

        with st.expander("查看路径摘要表", expanded=False):
            if not ft_path_df.empty:
                st.dataframe(ft_path_df, use_container_width=True, hide_index=True)
            else:
                st.info("暂无路径数据")

    # =====================================================
    # 知识关联图谱
    # =====================================================
    with tab_graph:
        st.markdown("## 知识关联图谱")
        st.caption("用于查看系统、设备、故障现象、原因、方案等知识之间的关联结构。")

        if st.button("重新加载全图", use_container_width=False, key="kg_reload_all_btn"):
            try:
                st.session_state["graph_all_data"] = fetch_all_graph_from_a()
                st.success("图谱加载成功")
                st.rerun()
            except Exception as e:
                st.error(f"加载失败：{e}")

        all_graph_data = st.session_state.get("graph_all_data", {"nodes": [], "edges": []})
        all_types = sorted(list(set([n.get("type", "Unknown") for n in all_graph_data.get("nodes", [])])))

        default_types = [t for t in all_types if t not in ["Keyword", "Unknown"]]
        if not default_types:
            default_types = all_types[:6] if len(all_types) > 6 else all_types

        kg1, kg2, kg3 = st.columns([2, 2, 1])
        with kg1:
            selected_types = st.multiselect(
                "按节点类型筛选",
                options=all_types,
                default=default_types,
                key="kg_selected_types"
            )
        with kg2:
            graph_keyword = st.text_input("按名称关键词过滤", value="", key="kg_filter_keyword")
        with kg3:
            max_render_nodes = st.slider("最多渲染节点", 50, 1000, 300, 50, key="kg_max_render_nodes")

        filtered_graph = filter_graph_data(
            all_graph_data,
            selected_types=selected_types,
            keyword=graph_keyword,
            max_nodes=max_render_nodes
        )

        fg_node_df = build_node_df(filtered_graph)
        fg_edge_df = build_edge_df(filtered_graph)

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("当前展示节点", len(fg_node_df))
        with k2:
            st.metric("当前展示关系", len(fg_edge_df))
        with k3:
            st.metric("展示模式", "知识关联探索")

        if len(all_graph_data.get("nodes", [])) > max_render_nodes:
            st.warning(f"当前图谱节点较多，为保证交互流畅，已限制展示前 {max_render_nodes} 个过滤结果。")

        st.markdown("### 知识关联图谱")
        render_pyvis_graph(filtered_graph, height=740, hierarchical=False, show_title=False)

        with st.expander("查看当前子图明细", expanded=False):
            if not fg_node_df.empty:
                show_df = fg_node_df.copy()
                show_df["节点类型"] = show_df["type"].map(lambda x: TYPE_NAME_MAP.get(x, x))
                st.dataframe(show_df[["label", "节点类型", "desc"]], use_container_width=True, hide_index=True)
            else:
                st.info("暂无节点")

            if not fg_edge_df.empty:
                edge_show = fg_edge_df.copy()
                edge_show["关系类型"] = edge_show["label_cn"]
                st.dataframe(edge_show[["from", "to", "关系类型"]], use_container_width=True, hide_index=True)
            else:
                st.info("暂无关系")

    # =====================================================
    # 节点查询
    # =====================================================
    with tab_query:
        st.markdown("## 节点查询与局部关联分析")
        st.caption("输入节点关键词，仅查看局部关联范围，适合大规模图谱快速定位。")

        nq1, nq2 = st.columns([3, 1])
        with nq1:
            node_keyword = st.text_input("输入节点名称关键词", value="", key="node_query_keyword")
        with nq2:
            max_neighbors = st.slider("局部范围上限", 10, 200, 60, 10, key="node_query_max_neighbors")

        if node_keyword.strip():
            subgraph = extract_neighbors_subgraph(
                st.session_state.get("graph_all_data", {"nodes": [], "edges": []}),
                node_keyword,
                max_neighbors=max_neighbors
            )
            sub_node_df = build_node_df(subgraph)
            sub_edge_df = build_edge_df(subgraph)

            q1, q2 = st.columns(2)
            with q1:
                st.metric("局部节点数", len(sub_node_df))
            with q2:
                st.metric("局部关系数", len(sub_edge_df))

            st.markdown("### 局部知识关联图")
            render_pyvis_graph(subgraph, height=640, hierarchical=False, show_title=False)

            if not sub_node_df.empty:
                show_df = sub_node_df.copy()
                show_df["节点类型"] = show_df["type"].map(lambda x: TYPE_NAME_MAP.get(x, x))
                st.dataframe(show_df[["label", "节点类型", "desc"]], use_container_width=True, hide_index=True)
            else:
                st.info("未找到匹配节点")

            if not sub_edge_df.empty:
                edge_show = sub_edge_df.copy()
                edge_show["关系类型"] = edge_show["label_cn"]
                st.dataframe(edge_show[["from", "to", "关系类型"]], use_container_width=True, hide_index=True)
        else:
            st.info("请输入节点名称关键词，例如：喷油器、燃油系统、排烟温度高")

    # =====================================================
    # 图谱维护
    # =====================================================
    with tab_maintain:
        st.markdown("## 图谱维护")
        st.caption("用于节点与关系的增删改维护，建议由知识管理员操作。")
        maintain_tab1, maintain_tab2 = st.tabs(["节点维护", "关系维护"])

        with maintain_tab1:
            op = st.radio("节点操作", ["新增节点", "修改节点", "删除节点"], horizontal=True, key="node_op")

            if op == "新增节点":
                c1, c2 = st.columns(2)
                with c1:
                    add_label = st.selectbox("节点类型", VALID_LABELS, key="add_node_label")
                with c2:
                    add_name = st.text_input("节点名称", key="add_node_name")

                if st.button("提交新增节点", use_container_width=True, key="submit_add_node"):
                    try:
                        result = add_node_to_a(add_label, add_name)
                        st.success(result.get("message", "新增成功"))
                    except Exception as e:
                        st.error(f"新增失败：{e}")

            elif op == "修改节点":
                c1, c2, c3 = st.columns(3)
                with c1:
                    upd_label = st.selectbox("节点类型", VALID_LABELS, key="upd_node_label")
                with c2:
                    old_name = st.text_input("原节点名称", key="upd_old_name")
                with c3:
                    new_name = st.text_input("新节点名称", key="upd_new_name")

                if st.button("提交修改节点", use_container_width=True, key="submit_upd_node"):
                    try:
                        result = update_node_to_a(upd_label, old_name, new_name)
                        st.success(result.get("message", "修改成功"))
                    except Exception as e:
                        st.error(f"修改失败：{e}")

            else:
                c1, c2 = st.columns(2)
                with c1:
                    del_label = st.selectbox("节点类型", VALID_LABELS, key="del_node_label")
                with c2:
                    del_name = st.text_input("节点名称", key="del_node_name")

                if st.button("提交删除节点", use_container_width=True, key="submit_del_node"):
                    try:
                        result = delete_node_to_a(del_label, del_name)
                        st.success(result.get("message", "删除成功"))
                    except Exception as e:
                        st.error(f"删除失败：{e}")

        with maintain_tab2:
            rel_op = st.radio("关系操作", ["新增关系", "删除关系"], horizontal=True, key="rel_op")

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                start_label = st.selectbox("起点类型", VALID_LABELS, key="rel_start_label")
            with c2:
                start_name = st.text_input("起点名称", key="rel_start_name")
            with c3:
                relationship = st.selectbox("关系类型", VALID_RELATIONSHIPS, key="rel_type")
            with c4:
                end_label = st.selectbox("终点类型", VALID_LABELS, key="rel_end_label")
            with c5:
                end_name = st.text_input("终点名称", key="rel_end_name")

            if rel_op == "新增关系":
                if st.button("提交新增关系", use_container_width=True, key="submit_add_rel"):
                    try:
                        result = add_relation_to_a(start_label, start_name, relationship, end_label, end_name)
                        st.success(result.get("message", "新增成功"))
                    except Exception as e:
                        st.error(f"新增关系失败：{e}")
            else:
                if st.button("提交删除关系", use_container_width=True, key="submit_del_rel"):
                    try:
                        result = delete_relation_to_a(start_label, start_name, relationship, end_label, end_name)
                        st.success(result.get("message", "删除成功"))
                    except Exception as e:
                        st.error(f"删除关系失败：{e}")

    # =====================================================
    # 诊断分析
    # =====================================================
    with tab_analysis:
        st.markdown("## 诊断分析")
        st.caption("用于查看关键知识节点、原因分支分布、维修建议分布以及当前故障摘要。")

        ft_path_df = build_path_df(st.session_state.get("graph_fault_tree_data", {
            "nodes": [], "edges": [], "paths": [], "summary": {}, "worker_tips": []
        }))

        has_degree = degree_stats_df is not None and not degree_stats_df.empty
        has_cause = (
            ft_path_df is not None and not ft_path_df.empty
            and "原因分支" in ft_path_df.columns
            and ft_path_df["原因分支"].dropna().astype(str).str.strip().ne("").any()
        )
        has_repair = (
            ft_path_df is not None and not ft_path_df.empty
            and "维修建议" in ft_path_df.columns
            and ft_path_df["维修建议"].dropna().astype(str).str.strip().ne("").any()
        )

        if st.session_state.get("temperature_selected_detail", ""):
            st.markdown(f"""
            <div style="
                background:#F8FBFF;border:1px solid #DCE9F8;border-radius:18px;padding:16px 18px;margin-bottom:12px;">
                <div style="font-size:13px;color:#58708B;">当前专题详情</div>
                <div style="font-size:20px;font-weight:800;color:#173B7A;margin-top:4px;">{st.session_state.get("temperature_selected_detail", "")}</div>
            </div>
            """, unsafe_allow_html=True)

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            if has_degree:
                render_top_degree_bar_chart(degree_stats_df, title="高关联知识节点排行", top_n=15)
            else:
                render_compact_empty_card("高关联知识节点排行", "当前图谱中暂无可用于排行的节点关联数据。")

        with row1_col2:
            if has_cause:
                render_cause_frequency_chart(ft_path_df, title="原因分支分布", top_n=10)
            else:
                render_compact_empty_card("原因分支分布", "当前故障尚未提取到明确原因分支。")

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            if has_repair:
                render_repair_frequency_chart(ft_path_df, title="维修建议分布", top_n=10)
            else:
                render_compact_empty_card("维修建议分布", "当前故障尚未生成明确维修建议。")

        with row2_col2:
            if not ft_path_df.empty:
                render_recommendation_panel(ft_path_df)
            else:
                render_compact_empty_card("当前故障摘要", "请先完成故障树分析，生成有效路径后再查看。")




# ─────────────────────────────────────────
# 页面3：故障记录
# ─────────────────────────────────────────
elif page == lang["nav_records"]:
    import re
    import html
    from collections import defaultdict

    # =========================
    # 页面状态
    # =========================
    if "records_view_mode" not in st.session_state:
        st.session_state.records_view_mode = "list"  # list / dialog

    if "selected_chat_session_id" not in st.session_state:
        st.session_state.selected_chat_session_id = None

    if "records_report_session_id" not in st.session_state:
        st.session_state.records_report_session_id = None

    # =========================
    # 样式
    # =========================
    st.markdown("""
    <style>
    .block-container {
        padding-top: 1.05rem;
        padding-bottom: 2rem;
        max-width: 96%;
    }

    .records-hero {
        background: linear-gradient(135deg, #0B3E91 0%, #1867C9 55%, #57B5FF 100%);
        border-radius: 26px;
        padding: 30px 34px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 18px 36px rgba(24, 103, 201, 0.16);
    }

    .records-hero-title {
        font-size: 34px;
        font-weight: 900;
        margin-bottom: 10px;
    }

    .records-hero-subtitle {
        font-size: 15px;
        line-height: 1.85;
        color: rgba(255,255,255,0.96);
    }

    .records-badge {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        margin-right: 10px;
        margin-top: 14px;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.18);
        color: white;
        font-size: 13px;
        font-weight: 700;
    }

    .records-stat {
        background: linear-gradient(180deg, #FFFFFF 0%, #F7FBFF 100%);
        border: 1px solid rgba(24, 103, 201, 0.10);
        border-radius: 20px;
        padding: 18px 20px;
        box-shadow: 0 10px 24px rgba(24, 103, 201, 0.08);
        min-height: 114px;
        margin-bottom: 12px;
    }

    .records-stat-title {
        font-size: 14px;
        color: #6E8DB1;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .records-stat-value {
        font-size: 30px;
        color: #0C4FA3;
        font-weight: 900;
    }

    .panel-box {
        background: linear-gradient(180deg, #FFFFFF 0%, #F9FCFF 100%);
        border: 1px solid rgba(24, 103, 201, 0.10);
        border-radius: 22px;
        padding: 18px 20px;
        box-shadow: 0 12px 28px rgba(24, 103, 201, 0.08);
        margin-bottom: 16px;
    }

    .panel-title {
        font-size: 22px;
        font-weight: 900;
        color: #173B66;
        margin-bottom: 8px;
    }

    .panel-subtitle {
        font-size: 13px;
        color: #7E98B5;
        line-height: 1.75;
    }

    .topic-card {
        background: linear-gradient(180deg, #FFFFFF 0%, #F7FBFF 100%);
        border: 1px solid rgba(24, 103, 201, 0.10);
        border-radius: 18px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 8px 18px rgba(24, 103, 201, 0.06);
        min-height: 152px;
    }

    .topic-card-active {
        background: linear-gradient(180deg, #F5FAFF 0%, #EAF4FF 100%);
        border: 1px solid rgba(24, 103, 201, 0.22);
        box-shadow: 0 12px 24px rgba(24, 103, 201, 0.10);
    }

    .topic-title {
        font-size: 16px;
        font-weight: 900;
        color: #173B66;
        margin-bottom: 8px;
        line-height: 1.5;
    }

    .topic-meta {
        font-size: 12px;
        color: #7E98B5;
        margin-bottom: 5px;
        line-height: 1.7;
    }

    .topic-desc {
        font-size: 13px;
        color: #4F6C8C;
        line-height: 1.7;
        word-break: break-all;
    }

    .selected-box {
        background: #EAF4FF;
        border: 1px solid rgba(24, 103, 201, 0.12);
        color: #1457A8;
        padding: 12px 14px;
        border-radius: 14px;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .detail-card {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
        border: 1px solid rgba(24, 103, 201, 0.10);
        border-radius: 18px;
        padding: 18px 18px 14px 18px;
        margin-bottom: 14px;
        box-shadow: 0 8px 18px rgba(24, 103, 201, 0.06);
    }

    .detail-title {
        font-size: 20px;
        font-weight: 900;
        color: #173B66;
        margin-bottom: 14px;
        line-height: 1.6;
    }

    .detail-meta {
        font-size: 15px;
        color: #2C4A6E;
        line-height: 2.0;
    }

    .empty-box {
        background: linear-gradient(180deg, #F8FBFF 0%, #EEF5FF 100%);
        border: 1px dashed rgba(24, 103, 201, 0.18);
        border-radius: 18px;
        padding: 22px;
        color: #6080A6;
        text-align: center;
    }

    .chat-user {
        background: linear-gradient(135deg, #EAF4FF 0%, #F7FBFF 100%);
        border: 1px solid rgba(24, 103, 201, 0.10);
        border-radius: 18px 18px 18px 6px;
        padding: 14px 16px;
        margin: 8px 70px 8px 0;
        color: #123A66;
        box-shadow: 0 8px 18px rgba(24, 103, 201, 0.05);
    }

    .chat-ai {
        background: linear-gradient(135deg, #0D4EA3 0%, #2A87E8 100%);
        border-radius: 18px 18px 6px 18px;
        padding: 14px 16px;
        margin: 8px 0 8px 70px;
        color: white;
        box-shadow: 0 10px 20px rgba(24, 103, 201, 0.12);
    }

    .chat-role {
        font-size: 12px;
        font-weight: 800;
        margin-bottom: 6px;
        opacity: 0.95;
    }

    .chat-text {
        font-size: 14px;
        line-height: 1.85;
        white-space: pre-wrap;
        word-break: break-word;
    }

    .action-tip {
        background: linear-gradient(180deg, #F7FBFF 0%, #EEF6FF 100%);
        border: 1px solid rgba(24, 103, 201, 0.10);
        border-radius: 16px;
        padding: 14px 16px;
        color: #55769D;
        font-size: 13px;
        line-height: 1.8;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .report-box {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
        border: 1px solid rgba(24, 103, 201, 0.10);
        border-radius: 18px;
        padding: 16px;
        margin-top: 14px;
        margin-bottom: 14px;
        box-shadow: 0 8px 18px rgba(24, 103, 201, 0.06);
    }

    .danger-note {
        color: #C73C3C;
        font-size: 12px;
        margin-top: 6px;
        line-height: 1.6;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 14px;
        height: 44px;
        font-weight: 800;
        font-size: 15px;
        border: none;
        color: white;
        background: linear-gradient(135deg, #1565C0 0%, #2196F3 100%);
        box-shadow: 0 10px 20px rgba(33, 150, 243, 0.22);
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #0D47A1 0%, #1976D2 100%);
    }
    </style>
    """, unsafe_allow_html=True)


    # =========================
    # 工具函数
    # =========================
    def safe_text(x):
        return "" if x is None else str(x)


    def short_text(text, n=40):
        text = safe_text(text).strip()
        return text if len(text) <= n else text[:n] + "..."


    def tokenize(text):
        text = safe_text(text)
        parts = re.split(r"[，。；：、,\s\n\t（）()\\-_/]+", text)
        parts = [p.strip() for p in parts if p.strip()]
        return [p for p in parts if len(p) >= 2]


    def build_auto_topic_from_text(text):
        t = safe_text(text).strip()
        if not t:
            return "未命名主题"

        rule_map = [
            ("发热", "发热故障"),
            ("过热", "发热故障"),
            ("高温", "高温故障"),
            ("黑烟", "冒黑烟故障"),
            ("冒烟", "冒烟故障"),
            ("振动", "振动异常"),
            ("异响", "异响故障"),
            ("压力低", "压力不足"),
            ("压力不足", "压力不足"),
            ("漏油", "漏油故障"),
            ("报警", "报警故障"),
            ("启动困难", "启动困难"),
            ("无法启动", "无法启动"),
            ("温度高", "温度异常"),
            ("温度过高", "温度异常"),
        ]

        for k, v in rule_map:
            if k in t:
                return v

        t = re.sub(r"(是什么原因|怎么办|怎么处理|如何处理|如何解决|\\?|？)$", "", t)
        return short_text(t, 16) if t else "未命名主题"


    def infer_topic_for_session(sess):
        topic = safe_text(sess.get("topic", "")).strip()
        if topic:
            return topic
        messages = sess.get("messages", []) or []
        first_user = ""
        for m in messages:
            if m.get("role") == "user":
                first_user = safe_text(m.get("content", ""))
                break
        return build_auto_topic_from_text(first_user)


    def count_user_turns(messages):
        return sum(1 for m in (messages or []) if m.get("role") == "user")


    def count_total_messages(chat_sessions):
        return sum(len(sess.get("messages", []) or []) for sess in (chat_sessions or []))


    def count_confirmed_from_history(chat_sessions, records):
        session_confirmed_values = []
        for sess in chat_sessions or []:
            if "is_confirmed" in sess:
                session_confirmed_values.append(1 if sess.get("is_confirmed") else 0)
            elif "confirmed" in sess:
                session_confirmed_values.append(1 if sess.get("confirmed") else 0)

        if session_confirmed_values:
            return sum(session_confirmed_values)

        return sum(1 for r in (records or []) if len(r) > 6 and r[6] == 1)


    def get_selected_session(chat_sessions):
        selected_id = st.session_state.get("selected_chat_session_id")
        if not chat_sessions:
            return None

        for sess in chat_sessions:
            if sess["session_id"] == selected_id:
                return sess

        st.session_state.selected_chat_session_id = chat_sessions[0]["session_id"]
        return chat_sessions[0]


    def render_messages(messages):
        if not messages:
            st.markdown('<div class="empty-box">当前主题暂无消息内容</div>', unsafe_allow_html=True)
            return

        for msg in messages:
            role = msg.get("role", "")
            content = safe_text(msg.get("content", "")).strip()
            if not content:
                continue

            safe_html = html.escape(content).replace("\\n", "<br>")

            if role == "user":
                st.markdown(f"""
                <div class="chat-user">
                    <div class="chat-role">用户输入</div>
                    <div class="chat-text">{safe_html}</div>
                </div>
                """, unsafe_allow_html=True)

            elif role == "assistant":
                st.markdown(f"""
                <div class="chat-ai">
                    <div class="chat-role">系统回复</div>
                    <div class="chat-text">{safe_html}</div>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                <div class="chat-user">
                    <div class="chat-role">{html.escape(role or "消息")}</div>
                    <div class="chat-text">{safe_html}</div>
                </div>
                """, unsafe_allow_html=True)


    def get_delete_session_func():
        return (
                globals().get("delete_chat_session")
                or globals().get("delete_chat_session_by_id")
                or globals().get("remove_chat_session")
                or globals().get("delete_session_by_id")
        )


    # =========================
    # 数据读取
    # =========================
    records = get_all_fault_records()
    logs = get_all_logs()

    session_rows = get_all_chat_sessions()
    chat_sessions = convert_session_rows(session_rows) if session_rows else []

    for sess in chat_sessions:
        sess["topic"] = infer_topic_for_session(sess)

    record_count = len(chat_sessions)
    topic_count = len(chat_sessions)
    log_count = count_total_messages(chat_sessions)
    confirmed_count = count_confirmed_from_history(chat_sessions, records)

    if chat_sessions and not st.session_state.selected_chat_session_id:
        st.session_state.selected_chat_session_id = chat_sessions[0]["session_id"]

    selected_session = get_selected_session(chat_sessions)

    # =========================
    # 顶部横幅
    # =========================
    st.markdown(f"""
    <div class="records-hero">
        <div class="records-hero-title">故障处理记录中心</div>
        <div class="records-hero-subtitle">
            支持按历史主题查看会话记录。点击左侧主题后，右侧可选择查看完整对话、继续对话或生成 AI 报告，并支持删除历史记录。
        </div>
        <div>
            <span class="records-badge">故障记录 {record_count}</span>
            <span class="records-badge">历史主题 {topic_count}</span>
            <span class="records-badge">问答日志 {log_count}</span>
            <span class="records-badge">已确认 {confirmed_count}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # 概览卡片
    # =========================
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="records-stat">
            <div class="records-stat-title">故障记录总数</div>
            <div class="records-stat-value">{record_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="records-stat">
            <div class="records-stat-title">历史主题数量</div>
            <div class="records-stat-value">{topic_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="records-stat">
            <div class="records-stat-title">问答日志数量</div>
            <div class="records-stat-value">{log_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="records-stat">
            <div class="records-stat-title">已确认故障数</div>
            <div class="records-stat-value">{confirmed_count}</div>
        </div>
        """, unsafe_allow_html=True)

    # =========================
    # Tabs
    # =========================
    tab1, tab2 = st.tabs(["➕ 新增记录", "🕘 历史记录"])

    # =========================
    # Tab1：新增记录
    # =========================
    with tab1:
        st.markdown("""
        <div class="panel-box">
            <div class="panel-title">新增故障记录</div>
            <div class="panel-subtitle">
                填写本次故障现象、原因和处理方案，形成标准化故障记录。
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("fault_form_new_style_only_ui"):
            equipment_options = (
                ["发动机", "液压系统", "电气设备", "甲板机械", "导航系统", "其他"]
                if st.session_state.language == "中文"
                else ["Engine", "Hydraulic System", "Electrical Equipment", "Deck Machinery", "Navigation System",
                      "Other"]
            )

            col_a, col_b = st.columns(2)

            with col_a:
                equipment = st.selectbox(lang["records_equipment"], equipment_options)
                cause = st.text_input(
                    lang["records_cause"],
                    placeholder=lang["records_cause_placeholder"]
                )

            with col_b:
                description = st.text_area(
                    lang["records_description"],
                    placeholder=lang["records_description_placeholder"],
                    height=150
                )
                solution = st.text_area(
                    lang["records_solution"],
                    placeholder=lang["records_solution_placeholder"],
                    height=150
                )

            submit_btn = st.form_submit_button("提交故障记录", type="primary")

            if submit_btn:
                if description.strip() and cause.strip() and solution.strip():
                    save_fault_record(
                        equipment_type=equipment,
                        description=description.strip(),
                        cause=cause.strip(),
                        solution=solution.strip()
                    )
                    st.success("故障记录已保存")
                    st.rerun()
                else:
                    st.error("请完整填写故障现象、故障原因和解决方案")

    # =========================
    # Tab2：历史记录
    # =========================
    with tab2:
        head1, head2 = st.columns([6, 1])

        with head1:
            st.markdown("""
            <div class="panel-box">
                <div class="panel-title">历史主题记录</div>
                <div class="panel-subtitle">
                    左侧展示已保存的历史主题；点击后右侧会出现三个操作入口：查看完整对话、继续对话、生成 AI 报告。
                </div>
            </div>
            """, unsafe_allow_html=True)

        with head2:
            st.write("")
            st.write("")
            if st.button("刷新", key="chat_session_refresh_btn"):
                st.rerun()

        if st.session_state.records_view_mode == "dialog":
            current_dialog_session = get_selected_session(chat_sessions)

            top_back_col, top_title_col = st.columns([1, 5])
            with top_back_col:
                if st.button("← 返回历史记录", key="back_to_records_list_btn", use_container_width=True):
                    st.session_state.records_view_mode = "list"
                    st.rerun()

            with top_title_col:
                st.markdown("""
                <div class="panel-box">
                    <div class="panel-title">完整对话详情</div>
                    <div class="panel-subtitle">
                        当前页面展示该历史主题的完整问答过程，可用于复盘、导出和继续诊断。
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if current_dialog_session:
                st.markdown(f"""
                <div class="detail-card">
                    <div class="detail-title">主题：{html.escape(safe_text(current_dialog_session['topic']))}</div>
                    <div class="detail-meta"><b>创建时间：</b> {html.escape(safe_text(current_dialog_session['created_at']))}</div>
                    <div class="detail-meta"><b>最后更新：</b> {html.escape(safe_text(current_dialog_session['updated_at']))}</div>
                    <div class="detail-meta"><b>会话ID：</b> {html.escape(safe_text(current_dialog_session['session_id']))}</div>
                    <div class="detail-meta"><b>船舶IMO：</b> {html.escape(safe_text(current_dialog_session.get('ship_imo', '')))}</div>
                    <div class="detail-meta"><b>语言：</b> {html.escape(safe_text(current_dialog_session.get('language', '')))}</div>
                    <div class="detail-meta"><b>消息数量：</b> {len(current_dialog_session.get('messages', []) or [])}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("### 💬 完整对话")
                render_messages(current_dialog_session.get("messages", []))

                dialog_op1, dialog_op2 = st.columns(2)

                with dialog_op1:
                    if st.button("继续对话", key="continue_from_dialog_page_btn", use_container_width=True):
                        ok = load_chat_session_to_current(current_dialog_session["session_id"])
                        if ok:
                            st.session_state.force_nav_page = lang["nav_chat"]
                            st.success("已加载历史主题，正在跳转到智能问答页面")
                            st.rerun()
                        else:
                            st.error("加载历史会话失败")

                with dialog_op2:
                    if st.button("返回主题详情", key="back_to_topic_detail_btn", use_container_width=True):
                        st.session_state.records_view_mode = "list"
                        st.rerun()
            else:
                st.markdown('<div class="empty-box">未找到当前会话内容</div>', unsafe_allow_html=True)

        else:
            left_col, right_col = st.columns([1.05, 1.95], gap="large")

            # -------------------------
            # 左侧：主题会话列表
            # -------------------------
            with left_col:
                st.markdown("### 📂 主题列表")

                if chat_sessions:
                    for i, sess in enumerate(chat_sessions):
                        is_active = st.session_state.selected_chat_session_id == sess["session_id"]
                        user_count = count_user_turns(sess.get("messages", []))
                        msg_count = len(sess.get("messages", []))

                        active_class = "topic-card topic-card-active" if is_active else "topic-card"

                        st.markdown(f"""
                        <div class="{active_class}">
                            <div class="topic-title">{html.escape(safe_text(sess["topic"]))}</div>
                            <div class="topic-meta">创建时间：{html.escape(safe_text(sess["created_at"]))}</div>
                            <div class="topic-meta">最后更新：{html.escape(safe_text(sess["updated_at"]))}</div>
                            <div class="topic-meta">用户轮次：{user_count}</div>
                            <div class="topic-meta">消息总数：{msg_count}</div>
                            <div class="topic-desc">{html.escape(short_text(sess["session_id"], 38))}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        if is_active:
                            st.markdown(
                                '<div class="selected-box">当前已选中该主题</div>',
                                unsafe_allow_html=True
                            )

                        if st.button(
                                f"查看主题 #{i + 1}",
                                key=f"chat_session_select_{sess['session_id']}",
                                use_container_width=True
                        ):
                            st.session_state.selected_chat_session_id = sess["session_id"]
                            st.session_state.records_report_session_id = None
                            st.rerun()
                else:
                    st.markdown('<div class="empty-box">暂无历史会话主题</div>', unsafe_allow_html=True)

            # -------------------------
            # 右侧：主题详情 + 三个操作
            # -------------------------
            with right_col:
                st.markdown("### 📝 主题详情")

                if selected_session:
                    st.markdown(f"""
                    <div class="detail-card">
                        <div class="detail-title">主题：{html.escape(safe_text(selected_session['topic']))}</div>
                        <div class="detail-meta"><b>创建时间：</b> {html.escape(safe_text(selected_session['created_at']))}</div>
                        <div class="detail-meta"><b>最后更新：</b> {html.escape(safe_text(selected_session['updated_at']))}</div>
                        <div class="detail-meta"><b>会话ID：</b> {html.escape(safe_text(selected_session['session_id']))}</div>
                        <div class="detail-meta"><b>船舶IMO：</b> {html.escape(safe_text(selected_session.get('ship_imo', '')))}</div>
                        <div class="detail-meta"><b>语言：</b> {html.escape(safe_text(selected_session.get('language', '')))}</div>
                        <div class="detail-meta"><b>消息数量：</b> {len(selected_session.get('messages', []) or [])}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("""
                    <div class="action-tip">
                        请选择下方操作：<b>查看完整对话</b>、<b>继续对话</b> 或 <b>生成 AI 报告</b>。
                    </div>
                    """, unsafe_allow_html=True)

                    b1, b2, b3 = st.columns(3)

                    with b1:
                        if st.button("查看完整对话", key="view_full_dialog_btn", use_container_width=True):
                            st.session_state.records_view_mode = "dialog"
                            st.rerun()

                    with b2:
                        if st.button("继续对话", key="continue_selected_chat_btn", use_container_width=True):
                            ok = load_chat_session_to_current(selected_session["session_id"])
                            if ok:
                                st.session_state.force_nav_page = lang["nav_chat"]
                                st.success("已加载该历史主题，正在跳转到智能问答页面")
                                st.rerun()
                            else:
                                st.error("加载历史会话失败")

                    with b3:
                        if st.button("生成 AI 报告", key="generate_ai_report_btn", use_container_width=True):
                            try:
                                with st.spinner("正在生成 AI 报告，请稍候..."):
                                    report_text = generate_ai_report_for_session(selected_session)

                                if not report_text or not str(report_text).strip():
                                    st.error("AI 报告生成失败：模型返回为空")
                                else:
                                    st.session_state.records_report_session_id = selected_session["session_id"]
                                    st.session_state.generated_report_text = report_text

                                    ok = update_chat_session_report(selected_session["session_id"], report_text)
                                    if ok:
                                        st.success("AI 报告已生成并保存，可下载 TXT 或 PDF")
                                    else:
                                        st.warning("AI 报告已生成，但写入数据库失败，仅当前页面可见")

                                    st.rerun()

                            except Exception as e:
                                st.error(f"生成 AI 报告失败：{str(e)}")
                    st.markdown("#### 🗑️ 删除历史记录")

                    danger_left, danger_right = st.columns([2, 3])

                    with danger_left:
                        confirm_delete = st.checkbox(
                            "确认删除当前记录",
                            key=f"confirm_delete_{selected_session['session_id']}"
                        )

                    with danger_right:
                        delete_disabled = not confirm_delete
                        if st.button(
                                "删除历史记录",
                                key=f"delete_selected_session_{selected_session['session_id']}",
                                use_container_width=True,
                                disabled=delete_disabled
                        ):
                            try:
                                ok = delete_chat_session(selected_session["session_id"])
                                if ok:
                                    st.success("历史记录已删除")
                                    st.session_state.selected_chat_session_id = None
                                    st.session_state.records_report_session_id = None
                                    st.session_state.records_view_mode = "list"
                                    st.rerun()
                                else:
                                    st.error("删除失败，未找到对应记录或删除未成功")
                            except Exception as e:
                                st.error(f"删除失败：{e}")
                    # -------------------------
                    # AI 报告展示与下载
                    # -------------------------
                    st.markdown("---")

                    current_report = ""

                    if (
                            st.session_state.get("records_report_session_id") == selected_session["session_id"]
                            and st.session_state.get("generated_report_text")
                    ):
                        current_report = st.session_state.get("generated_report_text", "")
                    elif selected_session.get("report_text"):
                        current_report = selected_session.get("report_text", "")

                    if current_report and str(current_report).strip():
                        st.markdown("### 🤖 AI 报告预览")

                        st.text_area(
                            "report_preview",
                            value=current_report,
                            height=320,
                            key=f"report_preview_{selected_session['session_id']}"
                        )

                        d1, d2 = st.columns(2)

                        with d1:
                            st.download_button(
                                label="下载 TXT",
                                data=current_report,
                                file_name=f"AI报告_{selected_session['session_id']}.txt",
                                mime="text/plain",
                                key=f"download_txt_{selected_session['session_id']}",
                                use_container_width=True
                            )

                        with d2:
                            pdf_bytes = generate_pdf_bytes(
                                title=f"AI报告 - {selected_session.get('topic', '未命名主题')}",
                                content=current_report
                            )
                            st.download_button(
                                label="下载 PDF",
                                data=pdf_bytes,
                                file_name=f"AI报告_{selected_session['session_id']}.pdf",
                                mime="application/pdf",
                                key=f"download_pdf_{selected_session['session_id']}",
                                use_container_width=True
                            )
