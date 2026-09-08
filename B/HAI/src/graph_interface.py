import requests

A_BASE_URL = "http://127.0.0.1:5001"


def query_graph(query_text: str) -> str:
    """
    调用 A 的故障树接口，返回格式化图谱文本
    """
    query_text = (query_text or "").strip()
    if not query_text:
        return ""

    try:
        resp = requests.get(
            f"{A_BASE_URL}/graph/fault-tree",
            params={"symptom": query_text},
            timeout=10
        )

        if resp.status_code != 200:
            return ""

        result = resp.json()
        if not result.get("success"):
            return ""

        data = result.get("data", {})
        candidates = data.get("candidates", [])
        if not candidates:
            return ""

        lines = ["【知识图谱信息】"]
        for item in candidates:
            symptom = item.get("symptom", "")
            systems = item.get("system", []) or []
            equipments = item.get("equipment", []) or []
            causes = item.get("causes", []) or []
            diagnoses = item.get("diagnosis", []) or []
            repairs = item.get("repair", []) or []

            lines.append(f"故障现象：{symptom}")
            if equipments:
                lines.append(f"相关设备：{', '.join(equipments)}")
            if systems:
                lines.append(f"所属系统：{', '.join(systems)}")
            if causes:
                lines.append(f"可能原因：{', '.join(causes)}")
            if diagnoses:
                lines.append(f"诊断方法：{', '.join(diagnoses)}")
            if repairs:
                lines.append(f"维修方案：{', '.join(repairs)}")
            lines.append("---")

        return "\n".join(lines)

    except Exception as e:
        print(f"[graph_interface.query_graph] error: {e}")
        return ""


def send_graph_learning(data: dict) -> dict:
    """
    调用 A 的图谱自学习接口
    """
    try:
        resp = requests.post(
            f"{A_BASE_URL}/graph/update",
            json=data,
            timeout=15
        )

        if resp.status_code != 200:
            return {
                "success": False,
                "message": f"A服务返回状态码: {resp.status_code}"
            }

        return resp.json()

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
