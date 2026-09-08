# -*- coding: utf-8 -*-
"""
Neo4j 知识图谱统计脚本（本地直连版）

用法：
    1. 启动本地 Neo4j 并设置密码环境变量：
       export NEO4J_PASSWORD=你的Neo4j密码
    2. 运行统计：
       python query_neo4j.py

输出：总节点数、节点类型分布、总关系数、关系类型分布。
（原始版本通过 SSH 连接远程服务器执行，仓库中已移除服务器凭据）
"""
import os
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

QUERIES = [
    ("总节点数", "MATCH (n) RETURN count(n) as total"),
    ("按类型统计节点", "MATCH (n) RETURN labels(n)[0] as type, count(n) as count ORDER BY count DESC"),
    ("总关系数", "MATCH ()-[r]->() RETURN count(r) as total"),
    ("按类型统计关系", "MATCH ()-[r]->() RETURN type(r) as type, count(r) as count ORDER BY count DESC"),
]


def main():
    if not NEO4J_PASSWORD:
        raise SystemExit("请先设置环境变量 NEO4J_PASSWORD")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            for name, query in QUERIES:
                print(f"=== {name} ===")
                result = session.run(query)
                for record in result:
                    print(dict(record))
    finally:
        driver.close()


if __name__ == "__main__":
    main()