# -*- coding: utf-8 -*-
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from neo4j import GraphDatabase

app = Flask(__name__)
CORS(app)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

ALLOWED_LABELS = {
    "System", "Subsystem", "Equipment", "Component", "Part",
    "Symptom", "Cause", "Reason", "Diagnosis", "Repair",
    "Solution", "MaintenanceCase", "Tool", "Keyword",
    "Warning", "RiskLevel"
}

ALLOWED_RELATIONSHIPS = {
    "HAS_EQUIPMENT", "HAS_COMPONENT", "RELATED_COMPONENT",
    "BELONGS_TO", "HAS_SUBSYSTEM",
    "HAS_CAUSE", "CAUSED_BY",
    "HAS_DIAGNOSIS", "REQUIRES_DIAGNOSIS",
    "HAS_REPAIR", "REPAIRED_BY", "FIXES",
    "INSTANCE_OF", "CONFIRMED_CAUSE", "USED_REPAIR",
    "USE_TOOL", "REPLACE_PART", "EXHIBITS"
}

# =========================================================
# 船舶主机温度专题按钮入口
# =========================================================
TEMPERATURE_TOPIC_OPTIONS = {
    "船舶主机温度偏高": [
        {
            "name": "第1缸温度异常",
            "system": "排气系统",
            "equipment": "第1缸喷油器/第1缸排气阀",
            "has_detail": False
        },
        {
            "name": "第2缸温度异常",
            "system": "排气系统",
            "equipment": "第2缸喷油器/第2缸排气阀",
            "has_detail": False
        },
        {
            "name": "第3缸温度异常",
            "system": "排气系统",
            "equipment": "第3缸喷油器/第3缸排气阀",
            "has_detail": True
        },
        {
            "name": "第4缸温度异常",
            "system": "排气系统",
            "equipment": "第4缸喷油器/第4缸排气阀",
            "has_detail": False
        },
        {
            "name": "第5缸温度异常",
            "system": "排气系统",
            "equipment": "第5缸喷油器/第5缸排气阀",
            "has_detail": False
        },
        {
            "name": "第6缸温度异常",
            "system": "排气系统",
            "equipment": "第6缸喷油器/第6缸排气阀",
            "has_detail": False
        },
        {
            "name": "多缸温度异常",
            "system": "进气/扫气系统",
            "equipment": "增压器",
            "has_detail": False
        },
        {
            "name": "所有气缸温度普遍偏高",
            "system": "进气/扫气系统",
            "equipment": "空气冷却器",
            "has_detail": False
        },
        {
            "name": "主机冷却水温度偏高",
            "system": "冷却系统",
            "equipment": "冷却水泵",
            "has_detail": True
        },
        {
            "name": "缸套水温偏高",
            "system": "冷却系统",
            "equipment": "气缸套",
            "has_detail": False
        },
        {
            "name": "主机滑油温度偏高",
            "system": "润滑系统",
            "equipment": "滑油冷却器",
            "has_detail": True
        },
        {
            "name": "活塞冷却油温偏高",
            "system": "冷却系统",
            "equipment": "活塞",
            "has_detail": False
        },
        {
            "name": "排气阀温度偏高",
            "system": "排气系统",
            "equipment": "排气阀",
            "has_detail": False
        },
        {
            "name": "增压器排气温度偏高",
            "system": "进气/扫气系统",
            "equipment": "增压器",
            "has_detail": False
        },
        {
            "name": "主轴承温度偏高",
            "system": "润滑系统",
            "equipment": "主轴承",
            "has_detail": False
        },
        {
            "name": "排气总管温度偏高",
            "system": "排气系统",
            "equipment": "排气总管",
            "has_detail": False
        }
    ]
}

TEMPERATURE_DETAIL_MAP = {
    "第3缸温度异常": "第3缸排气温度异常偏高",
    "第3缸排气温度偏高": "第3缸排气温度异常偏高",
    "第3缸排温高": "第3缸排气温度异常偏高",
    "主机冷却水温度偏高": "主机冷却水温度偏高",
    "主机滑油温度偏高": "主机滑油温度偏高"
}

# =========================================================
# 船舶主机温度异常知识库
# =========================================================
FAULT_KB = {
    "船舶主机温度偏高": {
        "aliases": [
            "主机温度高",
            "主机温度偏高",
            "船舶主机温度高",
            "船舶主机温度偏高",
            "主机高温",
            "温度异常偏高"
        ],
        "systems": [
            "燃油系统",
            "喷油系统",
            "进气/扫气系统",
            "排气系统",
            "冷却系统",
            "润滑系统",
            "气缸机械系统",
            "测量与监测系统"
        ],
        "equipment": [
            "喷油器",
            "高压油泵",
            "增压器",
            "空气冷却器",
            "扫气箱",
            "排气阀",
            "排气总管",
            "活塞",
            "活塞环",
            "气缸套",
            "气缸盖",
            "冷却水泵",
            "中央冷却器",
            "滑油冷却器",
            "主轴承",
            "热电偶",
            "温度显示模块"
        ],
        "causes": [
            "单缸排气温度异常偏高",
            "多缸排气温度整体偏高",
            "所有气缸排气温度普遍偏高",
            "主机冷却水温度偏高",
            "缸套水温偏高",
            "主机滑油温度偏高",
            "活塞冷却油温偏高",
            "排气阀温度偏高",
            "增压器排气温度偏高",
            "主轴承温度偏高",
            "排气总管温度偏高"
        ],
        "diagnosis": [
            "先判断是单点局部高温还是系统性高温",
            "确认是测量异常还是真实过热",
            "按类别进入对应详细故障线路",
            "优先查看排气温度类、冷却系统类、润滑系统类和局部部件过热类",
            "进入单缸排温高详细线路",
            "检查主机负荷和增压状态",
            "检查全机工况和空气冷却器",
            "检查冷却水泵与冷却器",
            "检查缸套水流量和燃烧状态",
            "检查滑油冷却器和油品状态",
            "检查活塞冷却油流量",
            "检查排气阀密封和配气状态",
            "检查增压器效率和排气背压",
            "检查润滑、间隙和摩擦状态",
            "对比各缸排温与总管温度"
        ],
        "repair": [
            "根据选中的具体高温异常项执行针对性维修",
            "优先处理真实过热和高风险部位",
            "必要时降低主机负荷并持续监测",
            "进入单缸排温高对应维修方案",
            "清洗空气冷却器",
            "检修增压器",
            "降低主机负荷",
            "校准温度采集系统",
            "检修冷却水泵",
            "清洗冷却器",
            "清洗缸套冷却水道",
            "清洗滑油冷却器",
            "更换或处理滑油",
            "检修冷却油泵",
            "清理喷嘴与通路",
            "研磨或更换排气阀",
            "清洗增压器",
            "恢复正常润滑供给",
            "更换或修复轴承",
            "清理排气总管积碳",
            "处理异常缸燃烧问题"
        ],
        "analysis_paths": [
            "船舶主机温度偏高→选择异常类别→进入详细故障线路→定位根因→制定维修方案"
        ],
        "device_to_system": {
            "喷油器": "喷油系统",
            "高压油泵": "喷油系统",
            "增压器": "进气/扫气系统",
            "空气冷却器": "进气/扫气系统",
            "扫气箱": "进气/扫气系统",
            "排气阀": "排气系统",
            "排气总管": "排气系统",
            "活塞": "气缸机械系统",
            "活塞环": "气缸机械系统",
            "气缸套": "气缸机械系统",
            "气缸盖": "气缸机械系统",
            "冷却水泵": "冷却系统",
            "中央冷却器": "冷却系统",
            "滑油冷却器": "润滑系统",
            "主轴承": "润滑系统",
            "热电偶": "测量与监测系统",
            "温度显示模块": "测量与监测系统"
        },
        "cause_to_device": {
            "单缸排气温度异常偏高": "喷油器",
            "多缸排气温度整体偏高": "增压器",
            "所有气缸排气温度普遍偏高": "空气冷却器",
            "主机冷却水温度偏高": "冷却水泵",
            "缸套水温偏高": "气缸套",
            "主机滑油温度偏高": "滑油冷却器",
            "活塞冷却油温偏高": "活塞",
            "排气阀温度偏高": "排气阀",
            "增压器排气温度偏高": "增压器",
            "主轴承温度偏高": "主轴承",
            "排气总管温度偏高": "排气总管"
        },
        "cause_to_diagnosis": {
            "单缸排气温度异常偏高": ["进入单缸排温高详细线路"],
            "多缸排气温度整体偏高": ["检查主机负荷和增压状态"],
            "所有气缸排气温度普遍偏高": ["检查全机工况和空气冷却器"],
            "主机冷却水温度偏高": ["检查冷却水泵与冷却器"],
            "缸套水温偏高": ["检查缸套水流量和燃烧状态"],
            "主机滑油温度偏高": ["检查滑油冷却器和油品状态"],
            "活塞冷却油温偏高": ["检查活塞冷却油流量"],
            "排气阀温度偏高": ["检查排气阀密封和配气状态"],
            "增压器排气温度偏高": ["检查增压器效率和排气背压"],
            "主轴承温度偏高": ["检查润滑、间隙和摩擦状态"],
            "排气总管温度偏高": ["对比各缸排温与总管温度"]
        },
        "cause_to_repair": {
            "单缸排气温度异常偏高": ["进入单缸排温高对应维修方案"],
            "多缸排气温度整体偏高": ["清洗空气冷却器", "检修增压器"],
            "所有气缸排气温度普遍偏高": ["降低主机负荷", "校准温度采集系统"],
            "主机冷却水温度偏高": ["检修冷却水泵", "清洗冷却器"],
            "缸套水温偏高": ["清洗缸套冷却水道"],
            "主机滑油温度偏高": ["清洗滑油冷却器", "更换或处理滑油"],
            "活塞冷却油温偏高": ["检修冷却油泵", "清理喷嘴与通路"],
            "排气阀温度偏高": ["研磨或更换排气阀"],
            "增压器排气温度偏高": ["清洗增压器", "清洗空气冷却器"],
            "主轴承温度偏高": ["恢复正常润滑供给", "更换或修复轴承"],
            "排气总管温度偏高": ["清理排气总管积碳", "处理异常缸燃烧问题"]
        }
    },

    "主机单缸排气温度高": {
        "aliases": [
            "排烟温度高",
            "排气温度高",
            "单缸排温高",
            "单缸排气温度高",
            "主机排烟温度高",
            "主机排气温度高",
            "主机单缸排气温度高"
        ],
        "systems": [
            "燃油系统",
            "喷油系统",
            "进气/扫气系统",
            "排气系统",
            "气缸机械系统",
            "测量与监测系统"
        ],
        "equipment": [
            "喷油器",
            "高压油泵",
            "燃油滤器",
            "燃油加热器",
            "燃油黏度控制装置",
            "增压器",
            "空气冷却器",
            "扫气箱",
            "进气管路",
            "排气阀",
            "排气阀阀座",
            "排气通道",
            "活塞",
            "活塞环",
            "气缸套",
            "气缸盖",
            "热电偶",
            "温度显示模块"
        ],
        "causes": [
            "喷油器雾化不良",
            "喷油器滴漏",
            "喷孔堵塞",
            "喷油器开启压力异常",
            "高压油泵供油量过大",
            "高压油泵供油量不足",
            "喷油定时过迟",
            "喷油定时过早",
            "燃油品质差",
            "燃油中含水",
            "燃油黏度异常",
            "扫气压力不足",
            "增压器效率下降",
            "增压器叶轮脏污",
            "空气冷却器堵塞",
            "进气温度过高",
            "排气阀漏气",
            "排气阀烧蚀",
            "排气通道积炭",
            "活塞环磨损",
            "活塞环卡滞",
            "气缸套磨损",
            "压缩压力不足",
            "热电偶测量失准"
        ],
        "diagnosis": [
            "核实该缸排温是否真实偏高",
            "对比各缸排气温度差值",
            "检查是否仅单缸异常",
            "检查是否伴随黑烟",
            "检查是否伴随功率下降",
            "检查是否伴随敲缸声",
            "检查热电偶及接线",
            "校验温度显示模块",
            "检查喷油器回油情况",
            "对喷油器做台架试验",
            "检查高压油泵供油状态",
            "校验喷油定时",
            "检查扫气压力",
            "检查增压器转速与脏污情况",
            "检查空气冷却器前后温差",
            "检查排气阀密封状态",
            "分析该缸示功图",
            "检查压缩压力"
        ],
        "repair": [
            "更换热电偶",
            "紧固或修复测温接线",
            "清洗喷油器喷孔",
            "更换喷油器偶件",
            "校正喷油器开启压力",
            "更换喷油器总成",
            "检修高压油泵",
            "校正喷油定时",
            "更换燃油滤芯",
            "调整燃油加热温度和黏度",
            "清洗增压器叶轮",
            "清洗空气冷却器",
            "清理扫气箱和进气通道",
            "研磨或更换排气阀",
            "更换活塞环",
            "修复或更换气缸套"
        ],
        "analysis_paths": [
            "先确认测量是否准确",
            "判断是单缸异常还是多缸异常",
            "判断是否伴随黑烟",
            "优先排查喷油器",
            "再排查高压油泵与喷油定时",
            "然后排查扫气与进气系统",
            "再排查排气阀和压缩压力",
            "最后确认机械磨损并制定维修策略"
        ],
        "device_to_system": {
            "喷油器": "喷油系统",
            "高压油泵": "喷油系统",
            "燃油滤器": "燃油系统",
            "燃油加热器": "燃油系统",
            "燃油黏度控制装置": "燃油系统",
            "增压器": "进气/扫气系统",
            "空气冷却器": "进气/扫气系统",
            "扫气箱": "进气/扫气系统",
            "进气管路": "进气/扫气系统",
            "排气阀": "排气系统",
            "排气阀阀座": "排气系统",
            "排气通道": "排气系统",
            "活塞": "气缸机械系统",
            "活塞环": "气缸机械系统",
            "气缸套": "气缸机械系统",
            "气缸盖": "气缸机械系统",
            "热电偶": "测量与监测系统",
            "温度显示模块": "测量与监测系统"
        },
        "cause_to_device": {
            "喷油器雾化不良": "喷油器",
            "喷油器滴漏": "喷油器",
            "喷孔堵塞": "喷油器",
            "喷油器开启压力异常": "喷油器",
            "高压油泵供油量过大": "高压油泵",
            "高压油泵供油量不足": "高压油泵",
            "喷油定时过迟": "高压油泵",
            "喷油定时过早": "高压油泵",
            "燃油品质差": "燃油滤器",
            "燃油中含水": "燃油滤器",
            "燃油黏度异常": "燃油加热器",
            "扫气压力不足": "扫气箱",
            "增压器效率下降": "增压器",
            "增压器叶轮脏污": "增压器",
            "空气冷却器堵塞": "空气冷却器",
            "进气温度过高": "空气冷却器",
            "排气阀漏气": "排气阀",
            "排气阀烧蚀": "排气阀阀座",
            "排气通道积炭": "排气通道",
            "活塞环磨损": "活塞环",
            "活塞环卡滞": "活塞环",
            "气缸套磨损": "气缸套",
            "压缩压力不足": "气缸盖",
            "热电偶测量失准": "热电偶"
        },
        "cause_to_diagnosis": {
            "喷油器雾化不良": ["对喷油器做台架试验"],
            "喷油器滴漏": ["检查喷油器回油情况", "对喷油器做台架试验"],
            "喷孔堵塞": ["对喷油器做台架试验"],
            "喷油器开启压力异常": ["对喷油器做台架试验"],
            "高压油泵供油量过大": ["检查高压油泵供油状态"],
            "高压油泵供油量不足": ["检查高压油泵供油状态"],
            "喷油定时过迟": ["校验喷油定时"],
            "喷油定时过早": ["校验喷油定时"],
            "燃油品质差": ["检查是否伴随黑烟"],
            "燃油中含水": ["检查是否伴随黑烟"],
            "燃油黏度异常": ["检查是否伴随功率下降"],
            "扫气压力不足": ["检查扫气压力"],
            "增压器效率下降": ["检查增压器转速与脏污情况"],
            "增压器叶轮脏污": ["检查增压器转速与脏污情况"],
            "空气冷却器堵塞": ["检查空气冷却器前后温差"],
            "进气温度过高": ["检查空气冷却器前后温差"],
            "排气阀漏气": ["检查排气阀密封状态", "分析该缸示功图"],
            "排气阀烧蚀": ["检查排气阀密封状态"],
            "排气通道积炭": ["分析该缸示功图"],
            "活塞环磨损": ["检查压缩压力"],
            "活塞环卡滞": ["检查压缩压力"],
            "气缸套磨损": ["检查压缩压力"],
            "压缩压力不足": ["分析该缸示功图", "检查压缩压力"],
            "热电偶测量失准": ["检查热电偶及接线", "校验温度显示模块"]
        },
        "cause_to_repair": {
            "喷油器雾化不良": ["清洗喷油器喷孔", "更换喷油器总成"],
            "喷油器滴漏": ["更换喷油器偶件", "更换喷油器总成"],
            "喷孔堵塞": ["清洗喷油器喷孔"],
            "喷油器开启压力异常": ["校正喷油器开启压力"],
            "高压油泵供油量过大": ["检修高压油泵"],
            "高压油泵供油量不足": ["检修高压油泵"],
            "喷油定时过迟": ["校正喷油定时"],
            "喷油定时过早": ["校正喷油定时"],
            "燃油品质差": ["更换燃油滤芯"],
            "燃油中含水": ["更换燃油滤芯"],
            "燃油黏度异常": ["调整燃油加热温度和黏度"],
            "扫气压力不足": ["清理扫气箱和进气通道"],
            "增压器效率下降": ["清洗增压器叶轮"],
            "增压器叶轮脏污": ["清洗增压器叶轮"],
            "空气冷却器堵塞": ["清洗空气冷却器"],
            "进气温度过高": ["清洗空气冷却器"],
            "排气阀漏气": ["研磨或更换排气阀"],
            "排气阀烧蚀": ["研磨或更换排气阀"],
            "排气通道积炭": ["清理扫气箱和进气通道"],
            "活塞环磨损": ["更换活塞环"],
            "活塞环卡滞": ["更换活塞环"],
            "气缸套磨损": ["修复或更换气缸套"],
            "压缩压力不足": ["更换活塞环"],
            "热电偶测量失准": ["更换热电偶", "紧固或修复测温接线"]
        }
    },

    "第3缸排气温度异常偏高": {
        "aliases": [
            "第3缸温度异常",
            "第三缸温度异常",
            "3缸温度异常",
            "第3缸排温高",
            "3缸排温高",
            "第三缸排气温度高",
            "第三缸排烟温度高",
            "第3缸排气温度异常偏高",
            "第3缸排气温度偏高"
        ],
        "systems": [
            "燃油系统",
            "喷油系统",
            "进气/扫气系统",
            "排气系统",
            "气缸机械系统",
            "冷却系统",
            "测量与监测系统"
        ],
        "equipment": [
            "第3缸喷油器",
            "第3缸高压油泵",
            "第3缸排气阀",
            "第3缸活塞",
            "第3缸活塞环",
            "第3缸气缸套",
            "第3缸缸盖",
            "第3缸排温热电偶",
            "第3缸温度显示通道"
        ],
        "causes": [
            "第3缸喷油器雾化不良",
            "第3缸喷油器滴漏",
            "第3缸喷孔堵塞",
            "第3缸喷油量偏大",
            "第3缸喷油定时过迟",
            "第3缸排气阀漏气",
            "第3缸排气阀烧蚀",
            "第3缸排气通道积炭",
            "第3缸活塞环磨损",
            "第3缸活塞环卡滞",
            "第3缸气缸套磨损",
            "第3缸压缩压力不足",
            "第3缸冷却效果下降",
            "第3缸扫气不足",
            "第3缸热电偶测量失准"
        ],
        "diagnosis": [
            "核实第3缸排温是否真实偏高",
            "对比第3缸与其他缸排温差值",
            "检查第3缸热电偶及接线",
            "检查第3缸温度显示通道",
            "检查第3缸喷油器回油情况",
            "对第3缸喷油器做台架试验",
            "检查第3缸高压油泵供油状态",
            "校验第3缸喷油定时",
            "检查第3缸扫气状态",
            "检查第3缸排气阀密封状态",
            "分析第3缸示功图",
            "检查第3缸压缩压力"
        ],
        "repair": [
            "更换第3缸热电偶",
            "修复第3缸测温接线",
            "清洗第3缸喷油器喷孔",
            "更换第3缸喷油器偶件",
            "更换第3缸喷油器总成",
            "检修第3缸高压油泵",
            "校正第3缸喷油定时",
            "研磨或更换第3缸排气阀",
            "清理第3缸排气通道积炭",
            "更换第3缸活塞环",
            "修复或更换第3缸气缸套",
            "恢复第3缸冷却效果"
        ],
        "analysis_paths": [
            "第3缸排温高→先确认测量是否准确→排查第3缸喷油器→排查第3缸高压油泵与喷油定时→排查第3缸排气阀→排查第3缸压缩压力与机械磨损→确认根因"
        ],
        "device_to_system": {
            "第3缸喷油器": "喷油系统",
            "第3缸高压油泵": "喷油系统",
            "第3缸排气阀": "排气系统",
            "第3缸活塞": "气缸机械系统",
            "第3缸活塞环": "气缸机械系统",
            "第3缸气缸套": "气缸机械系统",
            "第3缸缸盖": "气缸机械系统",
            "第3缸排温热电偶": "测量与监测系统",
            "第3缸温度显示通道": "测量与监测系统"
        },
        "cause_to_device": {
            "第3缸喷油器雾化不良": "第3缸喷油器",
            "第3缸喷油器滴漏": "第3缸喷油器",
            "第3缸喷孔堵塞": "第3缸喷油器",
            "第3缸喷油量偏大": "第3缸高压油泵",
            "第3缸喷油定时过迟": "第3缸高压油泵",
            "第3缸排气阀漏气": "第3缸排气阀",
            "第3缸排气阀烧蚀": "第3缸排气阀",
            "第3缸排气通道积炭": "第3缸排气阀",
            "第3缸活塞环磨损": "第3缸活塞环",
            "第3缸活塞环卡滞": "第3缸活塞环",
            "第3缸气缸套磨损": "第3缸气缸套",
            "第3缸压缩压力不足": "第3缸缸盖",
            "第3缸冷却效果下降": "第3缸缸盖",
            "第3缸扫气不足": "第3缸缸盖",
            "第3缸热电偶测量失准": "第3缸排温热电偶"
        },
        "cause_to_diagnosis": {
            "第3缸喷油器雾化不良": ["对第3缸喷油器做台架试验"],
            "第3缸喷油器滴漏": ["检查第3缸喷油器回油情况", "对第3缸喷油器做台架试验"],
            "第3缸喷孔堵塞": ["对第3缸喷油器做台架试验"],
            "第3缸喷油量偏大": ["检查第3缸高压油泵供油状态"],
            "第3缸喷油定时过迟": ["校验第3缸喷油定时"],
            "第3缸排气阀漏气": ["检查第3缸排气阀密封状态", "分析第3缸示功图"],
            "第3缸排气阀烧蚀": ["检查第3缸排气阀密封状态"],
            "第3缸排气通道积炭": ["分析第3缸示功图"],
            "第3缸活塞环磨损": ["检查第3缸压缩压力"],
            "第3缸活塞环卡滞": ["检查第3缸压缩压力"],
            "第3缸气缸套磨损": ["检查第3缸压缩压力"],
            "第3缸压缩压力不足": ["分析第3缸示功图", "检查第3缸压缩压力"],
            "第3缸冷却效果下降": ["核实第3缸排温是否真实偏高"],
            "第3缸扫气不足": ["检查第3缸扫气状态"],
            "第3缸热电偶测量失准": ["检查第3缸热电偶及接线", "检查第3缸温度显示通道"]
        },
        "cause_to_repair": {
            "第3缸喷油器雾化不良": ["清洗第3缸喷油器喷孔", "更换第3缸喷油器总成"],
            "第3缸喷油器滴漏": ["更换第3缸喷油器偶件", "更换第3缸喷油器总成"],
            "第3缸喷孔堵塞": ["清洗第3缸喷油器喷孔"],
            "第3缸喷油量偏大": ["检修第3缸高压油泵"],
            "第3缸喷油定时过迟": ["校正第3缸喷油定时"],
            "第3缸排气阀漏气": ["研磨或更换第3缸排气阀"],
            "第3缸排气阀烧蚀": ["研磨或更换第3缸排气阀"],
            "第3缸排气通道积炭": ["清理第3缸排气通道积炭"],
            "第3缸活塞环磨损": ["更换第3缸活塞环"],
            "第3缸活塞环卡滞": ["更换第3缸活塞环"],
            "第3缸气缸套磨损": ["修复或更换第3缸气缸套"],
            "第3缸压缩压力不足": ["更换第3缸活塞环"],
            "第3缸冷却效果下降": ["恢复第3缸冷却效果"],
            "第3缸扫气不足": ["检查并恢复第3缸扫气状态"],
            "第3缸热电偶测量失准": ["更换第3缸热电偶", "修复第3缸测温接线"]
        }
    },

    "主机冷却水温度偏高": {
        "aliases": [
            "冷却水温高",
            "主机冷却水温高",
            "主机水温高",
            "冷却水温度偏高"
        ],
        "systems": [
            "冷却系统",
            "测量与监测系统"
        ],
        "equipment": [
            "冷却水泵",
            "中央冷却器",
            "温控阀",
            "冷却水管路",
            "温度传感器"
        ],
        "causes": [
            "冷却水泵效率下降",
            "中央冷却器脏堵",
            "温控阀失灵",
            "冷却水流量不足",
            "主机负荷过高",
            "温度传感器失准"
        ],
        "diagnosis": [
            "确认冷却水温是否持续偏高",
            "检查冷却水泵流量和压力",
            "检查中央冷却器换热效果",
            "检查温控阀工作状态",
            "核对主机负荷",
            "检查温度传感器"
        ],
        "repair": [
            "检修冷却水泵",
            "清洗中央冷却器",
            "更换或修复温控阀",
            "疏通冷却水管路",
            "降低主机负荷",
            "更换温度传感器"
        ],
        "analysis_paths": [
            "冷却水温高→查水泵→查冷却器→查温控阀→查流量→查负荷→查传感器"
        ],
        "device_to_system": {
            "冷却水泵": "冷却系统",
            "中央冷却器": "冷却系统",
            "温控阀": "冷却系统",
            "冷却水管路": "冷却系统",
            "温度传感器": "测量与监测系统"
        },
        "cause_to_device": {
            "冷却水泵效率下降": "冷却水泵",
            "中央冷却器脏堵": "中央冷却器",
            "温控阀失灵": "温控阀",
            "冷却水流量不足": "冷却水管路",
            "主机负荷过高": "冷却水泵",
            "温度传感器失准": "温度传感器"
        },
        "cause_to_diagnosis": {
            "冷却水泵效率下降": ["检查冷却水泵流量和压力"],
            "中央冷却器脏堵": ["检查中央冷却器换热效果"],
            "温控阀失灵": ["检查温控阀工作状态"],
            "冷却水流量不足": ["检查冷却水泵流量和压力"],
            "主机负荷过高": ["核对主机负荷"],
            "温度传感器失准": ["检查温度传感器"]
        },
        "cause_to_repair": {
            "冷却水泵效率下降": ["检修冷却水泵"],
            "中央冷却器脏堵": ["清洗中央冷却器"],
            "温控阀失灵": ["更换或修复温控阀"],
            "冷却水流量不足": ["疏通冷却水管路"],
            "主机负荷过高": ["降低主机负荷"],
            "温度传感器失准": ["更换温度传感器"]
        }
    },

    "主机滑油温度偏高": {
        "aliases": [
            "滑油温高",
            "主机滑油温高",
            "润滑油温高",
            "滑油温度偏高"
        ],
        "systems": [
            "润滑系统",
            "测量与监测系统"
        ],
        "equipment": [
            "滑油泵",
            "滑油冷却器",
            "滑油滤器",
            "主轴承",
            "滑油温度传感器"
        ],
        "causes": [
            "滑油冷却器脏堵",
            "滑油量不足",
            "滑油粘度异常",
            "轴承摩擦加剧",
            "滤器堵塞",
            "温度传感器漂移"
        ],
        "diagnosis": [
            "查看滑油温度变化趋势",
            "检查滑油冷却器进出口温差",
            "检查滑油滤器压差",
            "检测滑油品质和粘度",
            "检查轴承是否异常发热",
            "复核温度传感器"
        ],
        "repair": [
            "清洗滑油冷却器",
            "补充或更换滑油",
            "调整滑油粘度",
            "检修轴承",
            "清洗或更换滤器",
            "更换温度传感器"
        ],
        "analysis_paths": [
            "滑油温高→查冷却器→查油量/油品→查滤器→查轴承摩擦→查传感器"
        ],
        "device_to_system": {
            "滑油泵": "润滑系统",
            "滑油冷却器": "润滑系统",
            "滑油滤器": "润滑系统",
            "主轴承": "润滑系统",
            "滑油温度传感器": "测量与监测系统"
        },
        "cause_to_device": {
            "滑油冷却器脏堵": "滑油冷却器",
            "滑油量不足": "滑油泵",
            "滑油粘度异常": "滑油泵",
            "轴承摩擦加剧": "主轴承",
            "滤器堵塞": "滑油滤器",
            "温度传感器漂移": "滑油温度传感器"
        },
        "cause_to_diagnosis": {
            "滑油冷却器脏堵": ["检查滑油冷却器进出口温差"],
            "滑油量不足": ["查看滑油温度变化趋势"],
            "滑油粘度异常": ["检测滑油品质和粘度"],
            "轴承摩擦加剧": ["检查轴承是否异常发热"],
            "滤器堵塞": ["检查滑油滤器压差"],
            "温度传感器漂移": ["复核温度传感器"]
        },
        "cause_to_repair": {
            "滑油冷却器脏堵": ["清洗滑油冷却器"],
            "滑油量不足": ["补充或更换滑油"],
            "滑油粘度异常": ["调整滑油粘度"],
            "轴承摩擦加剧": ["检修轴承"],
            "滤器堵塞": ["清洗或更换滤器"],
            "温度传感器漂移": ["更换温度传感器"]
        }
    }
}

# =========================================================
# 通用工具
# =========================================================
def ok(data=None, message="ok"):
    return jsonify({
        "success": True,
        "message": message,
        "data": data if data is not None else {}
    })


def fail(message="error", code=400):
    return jsonify({
        "success": False,
        "message": message,
        "data": {}
    }), code


def clean_text(v):
    return str(v).strip() if v is not None else ""


def unique_list(seq):
    result = []
    seen = set()
    for x in seq or []:
        x = clean_text(x)
        if x and x not in seen:
            result.append(x)
            seen.add(x)
    return result


def safe_label(label):
    label = clean_text(label)
    if label not in ALLOWED_LABELS:
        raise ValueError(f"非法标签类型: {label}")
    return label


def safe_relationship(rel):
    rel = clean_text(rel)
    if rel not in ALLOWED_RELATIONSHIPS:
        raise ValueError(f"非法关系类型: {rel}")
    return rel


def primary_type_of_node(node):
    labels = list(node.labels) if node else []
    if not labels:
        return "Unknown"

    priority = [
        "System", "Subsystem", "Equipment", "Component", "Part",
        "Symptom", "Cause", "Reason", "Diagnosis", "Repair",
        "Solution", "MaintenanceCase", "Tool", "Keyword",
        "Warning", "RiskLevel"
    ]
    for p in priority:
        if p in labels:
            return p
    return labels[0]


def node_name(node):
    if node is None:
        return ""
    for k in ["name", "label", "title"]:
        if k in node and clean_text(node.get(k)):
            return clean_text(node.get(k))
    return clean_text(node.element_id)


def node_to_dict(node):
    n_type = primary_type_of_node(node)
    n_name = node_name(node)
    return {
        "id": f"{n_type}:{n_name}" if n_name else f"{n_type}:{node.element_id}",
        "label": n_name,
        "name": n_name,
        "type": n_type,
        "type_name": n_type,
        "desc": clean_text(node.get("desc")) or n_name,
        "raw_labels": list(node.labels),
        "properties": dict(node)
    }


def rel_to_dict(rel, start_node=None, end_node=None):
    if start_node is None or end_node is None:
        return {
            "label": rel.type,
            "type": rel.type,
            "properties": dict(rel)
        }

    s = node_to_dict(start_node)
    t = node_to_dict(end_node)
    return {
        "from": s["id"],
        "to": t["id"],
        "label": rel.type,
        "type": rel.type,
        "properties": dict(rel)
    }


def dedupe_nodes(nodes):
    result = []
    seen = set()
    for n in nodes:
        nid = n.get("id")
        if nid and nid not in seen:
            result.append(n)
            seen.add(nid)
    return result


def dedupe_edges(edges):
    result = []
    seen = set()
    for e in edges:
        key = (e.get("from"), e.get("to"), e.get("label"))
        if key not in seen:
            result.append(e)
            seen.add(key)
    return result


def run_query(query, params=None):
    with driver.session() as session:
        return list(session.run(query, params or {}))


# =========================================================
# 内置知识库匹配工具
# =========================================================
def normalize_symptom_keyword(symptom_keyword):
    kw_raw = clean_text(symptom_keyword)
    kw = kw_raw.lower()
    if not kw:
        return ""

    if kw_raw in TEMPERATURE_DETAIL_MAP:
        return TEMPERATURE_DETAIL_MAP[kw_raw]

    for canonical, payload in FAULT_KB.items():
        aliases = payload.get("aliases", [])
        all_names = [canonical] + aliases
        for name in all_names:
            n = clean_text(name)
            if not n:
                continue
            nl = n.lower()
            if kw == nl:
                return canonical

    for canonical, payload in FAULT_KB.items():
        aliases = payload.get("aliases", [])
        all_names = [canonical] + aliases
        for name in all_names:
            n = clean_text(name)
            if not n:
                continue
            nl = n.lower()
            if kw in nl or nl in kw:
                return canonical

    if ("第3缸" in kw_raw or "3缸" in kw_raw or "第三缸" in kw_raw) and ("温度" in kw_raw or "排烟" in kw_raw or "排气" in kw_raw or "排温" in kw_raw):
        return "第3缸排气温度异常偏高"

    if ("排烟" in kw or "排气" in kw or "排温" in kw) and ("高" in kw or "偏高" in kw):
        return "主机单缸排气温度高"

    if ("冷却水" in kw or "水温" in kw) and ("高" in kw or "偏高" in kw):
        return "主机冷却水温度偏高"

    if ("滑油" in kw or "润滑油" in kw) and ("高" in kw or "偏高" in kw):
        return "主机滑油温度偏高"

    if ("主机" in kw or "船舶主机" in kw) and ("温度" in kw) and ("高" in kw or "偏高" in kw):
        return "船舶主机温度偏高"

    return kw_raw


def has_builtin_fault(symptom_keyword):
    canonical = normalize_symptom_keyword(symptom_keyword)
    return canonical in FAULT_KB


def make_builtin_candidate(canonical):
    kb = FAULT_KB[canonical]
    return {
        "symptom": canonical,
        "system": unique_list(kb.get("systems", [])),
        "equipment": unique_list(kb.get("equipment", [])),
        "causes": unique_list(kb.get("causes", [])),
        "diagnosis": unique_list(kb.get("diagnosis", [])),
        "repair": unique_list(kb.get("repair", []))
    }


def build_builtin_fault_tree_paths(canonical):
    kb = FAULT_KB[canonical]
    paths = []

    cause_to_device = kb.get("cause_to_device", {})
    device_to_system = kb.get("device_to_system", {})
    cause_to_diagnosis = kb.get("cause_to_diagnosis", {})
    cause_to_repair = kb.get("cause_to_repair", {})

    for cause in kb.get("causes", []):
        device = cause_to_device.get(cause, "")
        system = device_to_system.get(device, "")
        diagnoses = cause_to_diagnosis.get(cause, [""])
        repairs = cause_to_repair.get(cause, [""])

        if not diagnoses:
            diagnoses = [""]
        if not repairs:
            repairs = [""]

        max_len = max(len(diagnoses), len(repairs))
        for i in range(max_len):
            diag = diagnoses[i] if i < len(diagnoses) else ""
            rep = repairs[i] if i < len(repairs) else ""
            paths.append({
                "symptom": canonical,
                "equipment": device,
                "system": system,
                "cause": cause,
                "diagnosis": diag,
                "repair": rep
            })

    if not paths:
        paths.append({
            "symptom": canonical,
            "equipment": "",
            "system": "",
            "cause": "",
            "diagnosis": "",
            "repair": ""
        })

    return paths


def build_builtin_fault_tree_graph(canonical):
    kb = FAULT_KB[canonical]

    nodes = []
    edges = []
    relationships = []

    node_index = set()

    def add_node(n_type, name, desc=""):
        name = clean_text(name)
        if not name:
            return
        node_id = f"{n_type}:{name}"
        if node_id in node_index:
            return
        node_index.add(node_id)
        nodes.append({
            "id": node_id,
            "label": name,
            "name": name,
            "type": n_type,
            "type_name": n_type,
            "desc": desc or name,
            "raw_labels": [n_type],
            "properties": {"name": name, "desc": desc or name}
        })

    def add_edge(from_type, from_name, to_type, to_name, rel_type):
        from_name = clean_text(from_name)
        to_name = clean_text(to_name)
        if not from_name or not to_name:
            return
        add_node(from_type, from_name, from_name)
        add_node(to_type, to_name, to_name)
        edge = {
            "from": f"{from_type}:{from_name}",
            "to": f"{to_type}:{to_name}",
            "label": rel_type,
            "type": rel_type,
            "properties": {}
        }
        edges.append(edge)
        relationships.append({
            "start": edge["from"],
            "end": edge["to"],
            "type": rel_type,
            "properties": {}
        })

    add_node("Symptom", canonical, canonical)

    for system in kb.get("systems", []):
        add_node("System", system, system)

    for equipment in kb.get("equipment", []):
        add_node("Equipment", equipment, equipment)

    for cause in kb.get("causes", []):
        add_node("Cause", cause, cause)

    for diag in kb.get("diagnosis", []):
        add_node("Diagnosis", diag, diag)

    for repair in kb.get("repair", []):
        add_node("Repair", repair, repair)

    for cause, diags in kb.get("cause_to_diagnosis", {}).items():
        for diag in diags or []:
            add_node("Diagnosis", diag, diag)

    for cause, reps in kb.get("cause_to_repair", {}).items():
        for rep in reps or []:
            add_node("Repair", rep, rep)

    for device, system in kb.get("device_to_system", {}).items():
        add_node("Equipment", device, device)
        add_node("System", system, system)

    for cause, device in kb.get("cause_to_device", {}).items():
        add_node("Cause", cause, cause)
        add_node("Equipment", device, device)

    for equipment in unique_list(kb.get("equipment", [])):
        add_edge("Equipment", equipment, "Symptom", canonical, "EXHIBITS")

    for device, system in kb.get("device_to_system", {}).items():
        add_edge("Equipment", device, "System", system, "BELONGS_TO")

    for cause in unique_list(kb.get("causes", [])):
        add_edge("Symptom", canonical, "Cause", cause, "CAUSED_BY")

    for cause, diags in kb.get("cause_to_diagnosis", {}).items():
        for diag in diags:
            add_edge("Cause", cause, "Diagnosis", diag, "REQUIRES_DIAGNOSIS")

    for cause, repairs in kb.get("cause_to_repair", {}).items():
        for repair in repairs:
            add_edge("Repair", repair, "Cause", cause, "FIXES")

    nodes = dedupe_nodes(nodes)
    edges = dedupe_edges(edges)

    return {
        "nodes": nodes,
        "edges": edges,
        "relationships": relationships
    }


def build_builtin_fault_tree_result(symptom_keyword):
    canonical = normalize_symptom_keyword(symptom_keyword)
    if canonical not in FAULT_KB:
        return None

    kb = FAULT_KB[canonical]
    candidate = make_builtin_candidate(canonical)
    graph = build_builtin_fault_tree_graph(canonical)
    paths = build_builtin_fault_tree_paths(canonical)

    return {
        "canonical_symptom": canonical,
        "candidates": [candidate],
        "graph": graph,
        "paths": paths,
        "summary": {
            "systems": len(unique_list(kb.get("systems", []))),
            "equipment": len(unique_list(kb.get("equipment", []))),
            "causes": len(unique_list(kb.get("causes", []))),
            "diagnosis": len(unique_list(kb.get("diagnosis", []))),
            "repair": len(unique_list(kb.get("repair", []))),
            "analysis_paths": len(unique_list(kb.get("analysis_paths", [])))
        },
        "analysis_paths": kb.get("analysis_paths", []),
        "systems": kb.get("systems", []),
        "equipment": kb.get("equipment", []),
        "causes": kb.get("causes", []),
        "diagnosis": kb.get("diagnosis", []),
        "repair": kb.get("repair", [])
    }


def build_temperature_topic_cards():
    cards = []

    for item in TEMPERATURE_TOPIC_OPTIONS.get("船舶主机温度偏高", []):
        name = clean_text(item.get("name"))
        system = clean_text(item.get("system"))
        equipment = clean_text(item.get("equipment"))
        has_detail = bool(item.get("has_detail", False))

        if name == "第1缸温度异常":
            cause = "第1缸排气温度异常偏高"
            diagnosis = "建议优先检查该缸喷油器、喷油定时、排气阀和压缩压力"
            repair = "根据检查结果处理该缸喷油器、高压油泵、排气阀或活塞环等部件"
        elif name == "第2缸温度异常":
            cause = "第2缸排气温度异常偏高"
            diagnosis = "建议优先检查该缸喷油器、喷油定时、排气阀和压缩压力"
            repair = "根据检查结果处理该缸喷油器、高压油泵、排气阀或活塞环等部件"
        elif name == "第3缸温度异常":
            cause = "第3缸排气温度异常偏高"
            diagnosis = "建议优先核实第3缸排温真实性，并检查喷油器、喷油定时、排气阀和压缩压力"
            repair = "根据诊断结果处理第3缸喷油器、高压油泵、排气阀或活塞环等部件"
        elif name == "第4缸温度异常":
            cause = "第4缸排气温度异常偏高"
            diagnosis = "建议优先检查该缸喷油器、喷油定时、排气阀和压缩压力"
            repair = "根据检查结果处理该缸喷油器、高压油泵、排气阀或活塞环等部件"
        elif name == "第5缸温度异常":
            cause = "第5缸排气温度异常偏高"
            diagnosis = "建议优先检查该缸喷油器、喷油定时、排气阀和压缩压力"
            repair = "根据检查结果处理该缸喷油器、高压油泵、排气阀或活塞环等部件"
        elif name == "第6缸温度异常":
            cause = "第6缸排气温度异常偏高"
            diagnosis = "建议优先检查该缸喷油器、喷油定时、排气阀和压缩压力"
            repair = "根据检查结果处理该缸喷油器、高压油泵、排气阀或活塞环等部件"
        elif name == "多缸温度异常":
            cause = "多缸排气温度整体偏高"
            diagnosis = "建议检查主机负荷、增压器状态及空气冷却器换热效果"
            repair = "优先清洗空气冷却器并检修增压器"
        elif name == "所有气缸温度普遍偏高":
            cause = "所有气缸排气温度普遍偏高"
            diagnosis = "建议检查全机工况、空气冷却器和温度采集系统"
            repair = "必要时降低主机负荷并校准温度采集系统"
        elif name == "主机冷却水温度偏高":
            cause = "主机冷却水温度偏高"
            diagnosis = "建议检查冷却水泵、中央冷却器、温控阀和流量"
            repair = "检修冷却水泵并清洗冷却器"
        elif name == "缸套水温偏高":
            cause = "缸套水温偏高"
            diagnosis = "建议检查缸套水流量、冷却水道和燃烧状态"
            repair = "清洗缸套冷却水道并恢复正常冷却"
        elif name == "主机滑油温度偏高":
            cause = "主机滑油温度偏高"
            diagnosis = "建议检查滑油冷却器、滑油品质、滤器和润滑状态"
            repair = "清洗滑油冷却器并更换或处理滑油"
        elif name == "活塞冷却油温偏高":
            cause = "活塞冷却油温偏高"
            diagnosis = "建议检查冷却油流量、油泵状态和喷嘴通路"
            repair = "检修冷却油泵并清理喷嘴与通路"
        elif name == "排气阀温度偏高":
            cause = "排气阀温度偏高"
            diagnosis = "建议检查排气阀密封、烧蚀和配气状态"
            repair = "研磨或更换排气阀"
        elif name == "增压器排气温度偏高":
            cause = "增压器排气温度偏高"
            diagnosis = "建议检查增压器效率、转速、背压和空气冷却器"
            repair = "清洗增压器并清洗空气冷却器"
        elif name == "主轴承温度偏高":
            cause = "主轴承温度偏高"
            diagnosis = "建议检查润滑供给、轴承间隙和摩擦状态"
            repair = "恢复正常润滑供给并视情况更换或修复轴承"
        elif name == "排气总管温度偏高":
            cause = "排气总管温度偏高"
            diagnosis = "建议对比各缸排温，检查总管积碳及异常燃烧缸"
            repair = "清理排气总管积碳并处理异常缸燃烧问题"
        else:
            cause = name
            diagnosis = "建议结合现场参数进一步排查"
            repair = "建议根据诊断结果执行针对性维修"

        cards.append({
            "name": name,
            "system": system,
            "equipment": equipment,
            "symptom": "船舶主机温度偏高",
            "cause": cause,
            "diagnosis": diagnosis,
            "repair": repair,
            "has_detail": has_detail,
            "detail_key": name if has_detail else ""
        })

    return cards


# =========================================================
# 健康检查
# =========================================================
@app.route("/health", methods=["GET"])
def health():
    try:
        with driver.session() as session:
            session.run("RETURN 1 AS ok").single()
        return ok({"neo4j": "up"}, "service healthy")
    except Exception as e:
        return fail(f"service unhealthy: {e}", 500)


# =========================================================
# 获取全图
# =========================================================
@app.route("/graph/all", methods=["GET"])
def graph_all():
    try:
        node_limit = int(request.args.get("node_limit", 3000))
        rel_limit = int(request.args.get("rel_limit", 5000))

        node_query = f"""
        MATCH (n)
        RETURN n
        LIMIT {node_limit}
        """
        rel_query = f"""
        MATCH (a)-[r]->(b)
        RETURN a, r, b
        LIMIT {rel_limit}
        """

        node_records = run_query(node_query)
        rel_records = run_query(rel_query)

        nodes = []
        for rec in node_records:
            nodes.append(node_to_dict(rec["n"]))

        edges = []
        rels = []
        rel_nodes = []

        for rec in rel_records:
            a = rec["a"]
            r = rec["r"]
            b = rec["b"]

            rel_nodes.append(node_to_dict(a))
            rel_nodes.append(node_to_dict(b))

            edge = rel_to_dict(r, a, b)
            edges.append(edge)
            rels.append({
                "start": node_to_dict(a)["id"],
                "end": node_to_dict(b)["id"],
                "type": r.type,
                "properties": dict(r)
            })

        nodes = dedupe_nodes(nodes + rel_nodes)
        edges = dedupe_edges(edges)

        return ok({
            "nodes": nodes,
            "edges": edges,
            "relationships": rels
        }, "all graph fetched")

    except Exception as e:
        return fail(f"获取全图失败: {e}", 500)


# =========================================================
# 故障现象联想搜索
# =========================================================
@app.route("/graph/symptom/search", methods=["GET"])
def graph_symptom_search():
    try:
        q = clean_text(request.args.get("q"))
        limit = int(request.args.get("limit", 10))

        if not q:
            return ok([], "empty keyword")

        builtin_results = []
        for canonical, payload in FAULT_KB.items():
            all_names = [canonical] + payload.get("aliases", [])
            for name in all_names:
                if q in clean_text(name) or clean_text(name) in q:
                    builtin_results.append(canonical)
                    break

        if "温度" in q and ("主机" in q or "船舶主机" in q):
            builtin_results = ["船舶主机温度偏高"] + builtin_results

        builtin_results = unique_list(builtin_results)

        query = """
        MATCH (s:Symptom)
        WHERE toLower(coalesce(s.name, '')) CONTAINS toLower($q)
        RETURN DISTINCT coalesce(s.name, '') AS name
        ORDER BY name
        LIMIT $limit
        """
        db_records = run_query(query, {"q": q, "limit": limit})
        db_results = [clean_text(r["name"]) for r in db_records if clean_text(r["name"])]

        result = unique_list(builtin_results + db_results)[:limit]
        return ok(result, "symptom searched")

    except Exception as e:
        return fail(f"故障现象搜索失败: {e}", 500)


# =========================================================
# 故障树核心
# =========================================================
def query_matched_symptoms(symptom_keyword, limit=20):
    kw = clean_text(symptom_keyword)
    if not kw:
        return []

    canonical = normalize_symptom_keyword(kw)

    query = """
    MATCH (s:Symptom)
    WHERE
        toLower(coalesce(s.name, '')) CONTAINS toLower($kw)
        OR toLower(coalesce(s.name, '')) CONTAINS toLower(replace($kw, '故障', ''))
        OR toLower(coalesce(s.name, '')) CONTAINS toLower(replace($kw, '异常', ''))
        OR toLower(coalesce(s.name, '')) CONTAINS toLower(replace($kw, '过高', '高'))
        OR toLower(coalesce(s.name, '')) CONTAINS toLower(replace($kw, '过低', '低'))
        OR toLower(coalesce(s.name, '')) CONTAINS toLower(replace($kw, '无法', '不'))
        OR toLower(coalesce(s.name, '')) CONTAINS toLower(replace($kw, '不能', '不'))
        OR toLower(coalesce(s.name, '')) CONTAINS toLower($canonical)
    RETURN DISTINCT s
    ORDER BY
        CASE
            WHEN toLower(coalesce(s.name, '')) = toLower($kw) THEN 0
            WHEN toLower(coalesce(s.name, '')) = toLower($canonical) THEN 0
            WHEN toLower(coalesce(s.name, '')) STARTS WITH toLower($kw) THEN 1
            WHEN toLower(coalesce(s.name, '')) STARTS WITH toLower($canonical) THEN 1
            ELSE 2
        END,
        size(coalesce(s.name, '')),
        coalesce(s.name, '')
    LIMIT $limit
    """
    records = run_query(query, {"kw": kw, "canonical": canonical, "limit": limit})
    return [r["s"] for r in records]


def score_candidate(item):
    score = 0
    score += len(item.get("equipment", [])) * 2
    score += len(item.get("system", [])) * 1
    score += len(item.get("causes", [])) * 4
    score += len(item.get("diagnosis", [])) * 2
    score += len(item.get("repair", [])) * 2
    return score


def build_fault_tree_candidates(symptom_keyword):
    builtin = build_builtin_fault_tree_result(symptom_keyword)
    if builtin:
        return builtin["candidates"]

    matched_symptoms = query_matched_symptoms(symptom_keyword, limit=20)
    candidates = []

    for s in matched_symptoms:
        symptom_name = node_name(s)

        eq_query = """
        MATCH (e)-[:EXHIBITS]->(s:Symptom)
        WHERE s.name = $symptom_name
        RETURN DISTINCT coalesce(e.name, '') AS name
        ORDER BY name
        """
        equipments = [
            r["name"] for r in run_query(eq_query, {"symptom_name": symptom_name})
            if clean_text(r["name"])
        ]

        sys_query = """
        MATCH (e)-[:EXHIBITS]->(s:Symptom)
        OPTIONAL MATCH (e)-[:BELONGS_TO]->(sys)
        WHERE s.name = $symptom_name
        RETURN DISTINCT coalesce(sys.name, '') AS name
        ORDER BY name
        """
        systems = [
            r["name"] for r in run_query(sys_query, {"symptom_name": symptom_name})
            if clean_text(r["name"])
        ]

        cause_query = """
        MATCH (s:Symptom)-[:CAUSED_BY]->(c)
        WHERE s.name = $symptom_name
        RETURN DISTINCT coalesce(c.name, '') AS name
        ORDER BY name
        """
        causes = [
            r["name"] for r in run_query(cause_query, {"symptom_name": symptom_name})
            if clean_text(r["name"])
        ]

        diagnosis_query = """
        MATCH (s:Symptom)-[:CAUSED_BY]->(c)-[:REQUIRES_DIAGNOSIS]->(d)
        WHERE s.name = $symptom_name
        RETURN DISTINCT coalesce(d.name, '') AS name
        ORDER BY name
        """
        diagnoses = [
            r["name"] for r in run_query(diagnosis_query, {"symptom_name": symptom_name})
            if clean_text(r["name"])
        ]

        repair_query = """
        MATCH (s:Symptom)-[:CAUSED_BY]->(c)
        OPTIONAL MATCH (r)-[:FIXES]->(c)
        WHERE s.name = $symptom_name
        RETURN DISTINCT coalesce(r.name, '') AS name
        ORDER BY name
        """
        repairs = [
            r["name"] for r in run_query(repair_query, {"symptom_name": symptom_name})
            if clean_text(r["name"])
        ]

        candidates.append({
            "symptom": symptom_name,
            "system": unique_list(systems),
            "equipment": unique_list(equipments),
            "causes": unique_list(causes),
            "diagnosis": unique_list(diagnoses),
            "repair": unique_list(repairs)
        })

    candidates = sorted(candidates, key=score_candidate, reverse=True)
    return candidates[:10]

# =========================================================
# 统一搜索接口
# - 搜索 船舶主机温度偏高 -> 返回按钮 + overview
# - 搜索 第3缸温度异常 -> 返回 detail
# - 其他 -> fault-tree
# =========================================================
@app.route("/graph/search", methods=["GET"])
def graph_search():
    try:
        keyword = clean_text(request.args.get("keyword"))
        if not keyword:
            return fail("keyword 参数不能为空", 400)

        canonical = normalize_symptom_keyword(keyword)

        if canonical == "船舶主机温度偏高":
            cards = build_temperature_topic_cards()
            overview = build_builtin_fault_tree_result("船舶主机温度偏高")
            return ok({
                "mode": "topic",
                "topic": "船舶主机温度偏高",
                "canonical_symptom": canonical,
                "cards": cards,
                "overview": {
                    "canonical_symptom": overview["canonical_symptom"],
                    "candidates": overview["candidates"],
                    "graph": overview["graph"],
                    "paths": overview["paths"],
                    "summary": overview["summary"],
                    "analysis_paths": overview["analysis_paths"],
                    "systems": overview["systems"],
                    "equipment": overview["equipment"],
                    "causes": overview["causes"],
                    "diagnosis": overview["diagnosis"],
                    "repair": overview["repair"],
                    "source": "builtin"
                }
            }, "search result fetched")

        if keyword in TEMPERATURE_DETAIL_MAP or canonical in [
            "第3缸排气温度异常偏高",
            "主机冷却水温度偏高",
            "主机滑油温度偏高"
        ]:
            detail = build_builtin_fault_tree_result(keyword)
            if detail:
                return ok({
                    "mode": "detail",
                    "detail": {
                        "canonical_symptom": detail["canonical_symptom"],
                        "candidates": detail["candidates"],
                        "graph": detail["graph"],
                        "paths": detail["paths"],
                        "summary": detail["summary"],
                        "analysis_paths": detail["analysis_paths"],
                        "systems": detail["systems"],
                        "equipment": detail["equipment"],
                        "causes": detail["causes"],
                        "diagnosis": detail["diagnosis"],
                        "repair": detail["repair"],
                        "source": "builtin"
                    }
                }, "search result fetched")

        builtin = build_builtin_fault_tree_result(keyword)
        if builtin:
            return ok({
                "mode": "fault_tree",
                "fault_tree": {
                    "canonical_symptom": builtin["canonical_symptom"],
                    "candidates": builtin["candidates"],
                    "graph": builtin["graph"],
                    "paths": builtin["paths"],
                    "summary": builtin["summary"],
                    "analysis_paths": builtin["analysis_paths"],
                    "systems": builtin["systems"],
                    "equipment": builtin["equipment"],
                    "causes": builtin["causes"],
                    "diagnosis": builtin["diagnosis"],
                    "repair": builtin["repair"],
                    "source": "builtin"
                }
            }, "search result fetched")

        candidates = build_fault_tree_candidates(keyword)
        graph = build_fault_tree_graph(keyword)
        paths = build_fault_tree_paths(keyword)

        candidate = candidates[0] if candidates else {}
        summary = {
            "systems": len(candidate.get("system", [])),
            "equipment": len(candidate.get("equipment", [])),
            "causes": len(candidate.get("causes", [])),
            "diagnosis": len(candidate.get("diagnosis", [])),
            "repair": len(candidate.get("repair", [])),
            "analysis_paths": len(paths)
        }

        return ok({
            "mode": "fault_tree",
            "fault_tree": {
                "canonical_symptom": keyword,
                "candidates": candidates,
                "graph": graph,
                "paths": paths,
                "summary": summary,
                "source": "neo4j"
            }
        }, "search result fetched")

    except Exception as e:
        return fail(f"统一搜索失败: {e}", 500)

def build_fault_tree_graph(symptom_keyword):
    builtin = build_builtin_fault_tree_result(symptom_keyword)
    if builtin:
        return builtin["graph"]

    matched_symptoms = query_matched_symptoms(symptom_keyword, limit=20)
    if not matched_symptoms:
        return {
            "nodes": [],
            "edges": [],
            "relationships": []
        }

    symptom_names = [node_name(s) for s in matched_symptoms]

    query = """
    MATCH (sym:Symptom)
    WHERE sym.name IN $symptom_names

    OPTIONAL MATCH (eq)-[r1:EXHIBITS]->(sym)
    OPTIONAL MATCH (eq)-[r2:BELONGS_TO]->(sys)
    OPTIONAL MATCH (sym)-[r3:CAUSED_BY]->(cause)
    OPTIONAL MATCH (cause)-[r4:REQUIRES_DIAGNOSIS]->(diag)
    OPTIONAL MATCH (repair)-[r5:FIXES]->(cause)

    RETURN DISTINCT sym, eq, sys, cause, diag, repair, r1, r2, r3, r4, r5
    """

    records = run_query(query, {"symptom_names": symptom_names})

    nodes = []
    edges = []
    relationships = []

    for rec in records:
        for nk in ["sym", "eq", "sys", "cause", "diag", "repair"]:
            n = rec.get(nk)
            if n is not None:
                nodes.append(node_to_dict(n))

        rel_specs = [
            ("r1", "eq", "sym"),
            ("r2", "eq", "sys"),
            ("r3", "sym", "cause"),
            ("r4", "cause", "diag"),
            ("r5", "repair", "cause")
        ]

        for rk, sk, tk in rel_specs:
            r = rec.get(rk)
            s = rec.get(sk)
            t = rec.get(tk)
            if r is not None and s is not None and t is not None:
                edge = rel_to_dict(r, s, t)
                edges.append(edge)
                relationships.append({
                    "start": edge["from"],
                    "end": edge["to"],
                    "type": edge["label"],
                    "properties": dict(r)
                })

    nodes = dedupe_nodes(nodes)
    edges = dedupe_edges(edges)

    return {
        "nodes": nodes,
        "edges": edges,
        "relationships": relationships
    }


def build_fault_tree_paths(symptom_keyword):
    """构建故障树路径列表"""
    builtin = build_builtin_fault_tree_result(symptom_keyword)
    if builtin:
        return builtin["paths"]

    # 如果没有内置知识库匹配，从 Neo4j 构建
    matched_symptoms = query_matched_symptoms(symptom_keyword, limit=10)
    if not matched_symptoms:
        return []

    paths = []
    for s in matched_symptoms:
        symptom_name = node_name(s)

        # 查询该症状的所有路径
        path_query = """
        MATCH (sym:Symptom)-[:CAUSED_BY]->(cause:Cause)
        WHERE sym.name = $symptom_name
        OPTIONAL MATCH (eq)-[:EXHIBITS]->(sym)
        OPTIONAL MATCH (eq)-[:BELONGS_TO]->(sys)
        OPTIONAL MATCH (cause)-[:REQUIRES_DIAGNOSIS]->(diag)
        OPTIONAL MATCH (repair)-[:FIXES]->(cause)
        RETURN DISTINCT
            sym.name AS symptom,
            eq.name AS equipment,
            sys.name AS system,
            cause.name AS cause,
            diag.name AS diagnosis,
            repair.name AS repair
        """
        records = run_query(path_query, {"symptom_name": symptom_name})

        for r in records:
            paths.append({
                "symptom": clean_text(r.get("symptom")),
                "equipment": clean_text(r.get("equipment")),
                "system": clean_text(r.get("system")),
                "cause": clean_text(r.get("cause")),
                "diagnosis": clean_text(r.get("diagnosis")),
                "repair": clean_text(r.get("repair"))
            })

    return paths


# =========================================================
# 故障树接口
# =========================================================
@app.route("/graph/fault-tree", methods=["GET"])
def graph_fault_tree():
    try:
        symptom = clean_text(request.args.get("symptom"))
        if not symptom:
            return fail("symptom 参数不能为空", 400)

        builtin = build_builtin_fault_tree_result(symptom)
        if builtin:
            return ok({
                "canonical_symptom": builtin["canonical_symptom"],
                "candidates": builtin["candidates"],
                "graph": builtin["graph"],
                "paths": builtin["paths"],
                "summary": builtin["summary"],
                "analysis_paths": builtin["analysis_paths"],
                "systems": builtin["systems"],
                "equipment": builtin["equipment"],
                "causes": builtin["causes"],
                "diagnosis": builtin["diagnosis"],
                "repair": builtin["repair"],
                "source": "builtin"
            }, "fault tree fetched")

        candidates = build_fault_tree_candidates(symptom)
        graph = build_fault_tree_graph(symptom)
        paths = build_fault_tree_paths(symptom)

        candidate = candidates[0] if candidates else {}
        summary = {
            "systems": len(candidate.get("system", [])),
            "equipment": len(candidate.get("equipment", [])),
            "causes": len(candidate.get("causes", [])),
            "diagnosis": len(candidate.get("diagnosis", [])),
            "repair": len(candidate.get("repair", [])),
            "analysis_paths": len(paths)
        }

        return ok({
            "canonical_symptom": symptom,
            "candidates": candidates,
            "graph": graph,
            "paths": paths,
            "summary": summary,
            "source": "neo4j"
        }, "fault tree fetched")

    except Exception as e:
        return fail(f"查询故障树失败: {e}", 500)


# =========================================================
# 知识图谱专题接口
# =========================================================
@app.route("/graph/knowledge", methods=["GET"])
def graph_knowledge():
    try:
        symptom = clean_text(request.args.get("symptom"))
        if not symptom:
            return fail("symptom 参数不能为空", 400)

        builtin = build_builtin_fault_tree_result(symptom)
        if builtin:
            return ok({
                "fault": builtin["canonical_symptom"],
                "summary": builtin["summary"],
                "systems": builtin["systems"],
                "equipment": builtin["equipment"],
                "causes": builtin["causes"],
                "diagnosis": builtin["diagnosis"],
                "repair": builtin["repair"],
                "analysis_paths": builtin["analysis_paths"],
                "graph": builtin["graph"],
                "source": "builtin"
            }, "knowledge graph fetched")

        graph = build_fault_tree_graph(symptom)
        return ok({
            "fault": symptom,
            "graph": graph,
            "source": "neo4j"
        }, "knowledge graph fetched")

    except Exception as e:
        return fail(f"知识图谱查询失败: {e}", 500)


# =========================================================
# 温度专题按钮接口
# =========================================================
# =========================================================
# 温度专题按钮接口
# 返回 cards + 总体故障树 overview
# =========================================================
@app.route("/graph/topic/temperature-options", methods=["GET"])
def graph_topic_temperature_options():
    try:
        symptom = clean_text(request.args.get("symptom"))
        canonical = normalize_symptom_keyword(symptom)

        if canonical != "船舶主机温度偏高":
            if symptom in TEMPERATURE_TOPIC_OPTIONS:
                canonical = symptom
            else:
                return fail("当前仅支持 船舶主机温度偏高 专题入口", 400)

        cards = build_temperature_topic_cards()
        overview = build_builtin_fault_tree_result("船舶主机温度偏高")

        return ok({
            "topic": "船舶主机温度偏高",
            "canonical_symptom": canonical,
            "cards": cards,
            "overview": {
                "canonical_symptom": overview["canonical_symptom"],
                "candidates": overview["candidates"],
                "graph": overview["graph"],
                "paths": overview["paths"],
                "summary": overview["summary"],
                "analysis_paths": overview["analysis_paths"],
                "systems": overview["systems"],
                "equipment": overview["equipment"],
                "causes": overview["causes"],
                "diagnosis": overview["diagnosis"],
                "repair": overview["repair"],
                "source": "builtin"
            }
        }, "temperature topic options fetched")

    except Exception as e:
        return fail(f"温度专题入口查询失败: {e}", 500)

# =========================================================
# 温度专题详细接口
# =========================================================
@app.route("/graph/topic/temperature-detail", methods=["GET"])
def graph_topic_temperature_detail():
    try:
        name = clean_text(request.args.get("name"))
        if not name:
            return fail("name 参数不能为空", 400)

        canonical = TEMPERATURE_DETAIL_MAP.get(name, normalize_symptom_keyword(name))
        builtin = build_builtin_fault_tree_result(canonical)

        if not builtin:
            return fail("该专题按钮暂无详细故障树", 404)

        return ok({
            "topic": "船舶主机温度偏高",
            "entry_name": name,
            "canonical_symptom": builtin["canonical_symptom"],
            "candidates": builtin["candidates"],
            "graph": builtin["graph"],
            "paths": builtin["paths"],
            "summary": builtin["summary"],
            "analysis_paths": builtin["analysis_paths"],
            "systems": builtin["systems"],
            "equipment": builtin["equipment"],
            "causes": builtin["causes"],
            "diagnosis": builtin["diagnosis"],
            "repair": builtin["repair"],
            "source": "builtin"
        }, "temperature topic detail fetched")

    except Exception as e:
        return fail(f"温度专题详细查询失败: {e}", 500)


# =========================================================
# 节点维护
# =========================================================
@app.route("/graph/node/add", methods=["POST"])
def graph_node_add():
    try:
        data = request.get_json(force=True)
        label = safe_label(data.get("label"))
        name = clean_text(data.get("name"))

        if not name:
            return fail("name 不能为空", 400)

        query = f"""
        MERGE (n:{label} {{name: $name}})
        RETURN n
        """
        records = run_query(query, {"name": name})
        node = node_to_dict(records[0]["n"]) if records else {}

        return ok({"node": node}, "节点新增成功")

    except Exception as e:
        return fail(f"节点新增失败: {e}", 500)


@app.route("/graph/node/update", methods=["POST"])
def graph_node_update():
    try:
        data = request.get_json(force=True)
        label = safe_label(data.get("label"))
        old_name = clean_text(data.get("old_name"))
        new_name = clean_text(data.get("new_name"))

        if not old_name or not new_name:
            return fail("old_name 和 new_name 不能为空", 400)

        query = f"""
        MATCH (n:{label} {{name: $old_name}})
        SET n.name = $new_name
        RETURN count(n) AS cnt
        """
        records = run_query(query, {"old_name": old_name, "new_name": new_name})
        cnt = records[0]["cnt"] if records else 0

        return ok({"updated": cnt}, "节点修改成功")

    except Exception as e:
        return fail(f"节点修改失败: {e}", 500)


@app.route("/graph/node/delete", methods=["POST"])
def graph_node_delete():
    try:
        data = request.get_json(force=True)
        label = safe_label(data.get("label"))
        name = clean_text(data.get("name"))

        if not name:
            return fail("name 不能为空", 400)

        query = f"""
        MATCH (n:{label} {{name: $name}})
        WITH collect(n) AS nodes, count(n) AS cnt
        FOREACH (x IN nodes | DETACH DELETE x)
        RETURN cnt
        """
        records = run_query(query, {"name": name})
        cnt = records[0]["cnt"] if records else 0

        return ok({"deleted": cnt}, "节点删除成功")

    except Exception as e:
        return fail(f"节点删除失败: {e}", 500)



# =========================================================
# 关系维护
# =========================================================
@app.route("/graph/relation/add", methods=["POST"])
def graph_relation_add():
    try:
        data = request.get_json(force=True)

        start_label = safe_label(data.get("start_label"))
        start_name = clean_text(data.get("start_name"))
        relationship = safe_relationship(data.get("relationship"))
        end_label = safe_label(data.get("end_label"))
        end_name = clean_text(data.get("end_name"))

        if not start_name or not end_name:
            return fail("起点名称和终点名称不能为空", 400)

        query = f"""
        MATCH (a:{start_label} {{name: $start_name}})
        MATCH (b:{end_label} {{name: $end_name}})
        MERGE (a)-[r:{relationship}]->(b)
        RETURN a, r, b
        """
        records = run_query(query, {
            "start_name": start_name,
            "end_name": end_name
        })

        if not records:
            return fail("未找到起点或终点节点", 404)

        rec = records[0]
        edge = rel_to_dict(rec["r"], rec["a"], rec["b"])
        return ok({"edge": edge}, "关系新增成功")

    except Exception as e:
        return fail(f"关系新增失败: {e}", 500)


@app.route("/graph/relation/delete", methods=["POST"])
def graph_relation_delete():
    try:
        data = request.get_json(force=True)

        start_label = safe_label(data.get("start_label"))
        start_name = clean_text(data.get("start_name"))
        relationship = safe_relationship(data.get("relationship"))
        end_label = safe_label(data.get("end_label"))
        end_name = clean_text(data.get("end_name"))

        if not start_name or not end_name:
            return fail("起点名称和终点名称不能为空", 400)

        query = f"""
        MATCH (a:{start_label} {{name: $start_name}})-[r:{relationship}]->(b:{end_label} {{name: $end_name}})
        WITH collect(r) AS rels, count(r) AS cnt
        FOREACH (x IN rels | DELETE x)
        RETURN cnt
        """
        records = run_query(query, {
            "start_name": start_name,
            "end_name": end_name
        })
        cnt = records[0]["cnt"] if records else 0

        return ok({"deleted": cnt}, "关系删除成功")

    except Exception as e:
        return fail(f"关系删除失败: {e}", 500)

@app.errorhandler(404)
def not_found(_e):
    return fail("接口不存在", 404)

# =========================================================
# 首页
# =========================================================
@app.route("/", methods=["GET"])
def index():
    return ok({
        "service": "graph-api",
        "builtin_faults": list(FAULT_KB.keys()),
        "topic_routes": [
            "/graph/topic/temperature-options?symptom=船舶主机温度偏高",
            "/graph/topic/temperature-detail?name=第3缸排气温度偏高"
        ],
        "endpoints": [
            "/health",
            "/graph/all",
            "/graph/fault-tree?symptom=排烟温度高",
            "/graph/fault-tree?symptom=第3缸排气温度偏高",
            "/graph/knowledge?symptom=排烟温度高",
            "/graph/symptom/search?q=排烟",
            "/graph/topic/temperature-options?symptom=船舶主机温度偏高",
            "/graph/topic/temperature-detail?name=第3缸排气温度偏高",
            "/graph/node/add",
            "/graph/node/update",
            "/graph/node/delete",
            "/graph/relation/add",
            "/graph/relation/delete"
        ]
    }, "service ready")


if __name__ == "__main__":
    try:
        with driver.session() as session:
            session.run("RETURN 1").single()
        print("Neo4j connected.")
    except Exception as e:
        print(f"Neo4j connection failed: {e}")

    app.run(host="0.0.0.0", port=5001, debug=True)
