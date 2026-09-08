# A 模块

本压缩包内容包括：

1. 当前正式图谱结构说明
2. 故障树层层递进说明
3. 前端接入说明
4. 增删改接口说明
5. 最新版自学习协议样例
6. 完整版 backend/app.py
7. 示例 JSON
8. Neo4j 验证查询

## 当前正式图谱

### 节点类型
- Symptom
- Equipment
- System
- Cause
- Repair
- Diagnosis
- MaintenanceCase

### 关系类型
- HAS_EQUIPMENT
- BELONGS_TO
- HAS_CAUSE
- HAS_REPAIR
- HAS_DIAGNOSIS
- INSTANCE_OF
- CONFIRMED_CAUSE
- USED_REPAIR

## 快速使用

1. 打开 `backend/app.py`
2. 把 `PASSWORD = "你的Neo4j密码"` 改成自己的密码
3. 运行：
   ```bash
   pip install flask neo4j
   python backend/app.py
   ```
4. 前端调用：
   - `POST /graph/update`
   - `GET /graph/fault-tree?symptom=排烟温度高`
   - 其他增删改接口见 `docs/04_增删改接口说明.md`