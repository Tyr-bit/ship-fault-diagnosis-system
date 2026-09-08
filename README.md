# 船舶故障诊断智能问答系统

> **Ship Fault Diagnosis & Q&A System** — 面向船舶装备故障诊断场景的智能化解决方案

**Streamlit 前端可视化 · 知识图谱推理 · 本地轻量模型**  |  `Python` · `Neo4j` · `YOLOv8n` · `Whisper` · `Ollama`

---

## 界面预览

<p align="center">
  <img src="pic/船舶诊断登录界面.png" width="700" alt="船舶诊断登录界面">
  <br><em>船舶诊断登录 —— 基于船舶身份信息的会话初始化入口</em>
</p>

<p align="center">
  <img src="pic/智能问答诊断界面—中文版.png" width="700" alt="智能问答诊断界面">
  <br><em>智能问答诊断 —— 基于知识图谱结构的多轮专家问答（中英双语）</em>
</p>

<p align="center">
  <img src="pic/知识图谱总览分析页.png" width="700" alt="知识图谱总览分析页">
  <br><em>知识图谱总览分析 —— 按设备 / 系统 / 故障现象 / 原因 / 维修方案多维可视化</em>
</p>

<p align="center">
  <img src="pic/故障记录历史页.png" width="700" alt="故障处理记录中心">
  <br><em>故障处理记录中心 —— 历史会话管理与 AI 报告生成</em>
</p>

---

## 核心功能

### 1. 知识图谱可视化
基于 Neo4j 图谱数据，通过 `streamlit-agraph` / `pyvis` 实现多维交互式可视化：
- 按设备、系统、故障现象等维度动态展示图谱节点与关系
- 支持缩放、筛选、点击查看节点详情
- 图谱总览页提供数据统计与覆盖分析

### 2. AI 报告生成
对话结束后自动生成结构化诊断报告：
- 基于多轮对话历史，提炼故障现象、排查过程与结论
- 支持导出与历史会话回溯
- 故障记录中心统一管理所有诊断记录

### 3. 智能问答界面
Streamlit 构建的交互式诊断界面：
- 中英双语支持
- 语音输入（Whisper）与图像上传（YOLOv8n）入口
- 侧边栏会话管理与工单追踪

---

## 技术栈

| 领域 | 技术 |
|------|------|
| 可视化 | Streamlit · streamlit-agraph · pyvis |
| 图谱存储 | Neo4j · Cypher |
| 对话引擎 | LangGraph · DeepSeek R1 |
| 报告生成 | LLM 结构化抽取 |
| 多模态输入 | Whisper tiny · YOLOv8n |
| 数据层 | SQLite · JSON |

---

## 快速开始

```bash
pip install -r requests.txt
streamlit run app.py   # http://localhost:8501
```