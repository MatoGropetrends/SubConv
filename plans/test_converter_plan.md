# ConvertsV2Ray 函数测试计划

## 概述

本文档描述了对 [`modules/convert/converter.py`](modules/convert/converter.py) 中 `ConvertsV2Ray` 函数的测试计划。

## 测试框架

- **框架**: pytest
- **依赖**: 需要在 `requirements.txt` 中添加 `pytest` 和 `pytest-asyncio`

## 测试文件结构

```
tests/
├── __init__.py
├── conftest.py           # pytest 配置和 fixtures
└── test_converter.py     # 主测试文件
```

## 测试覆盖的协议

根据用户需求，测试将覆盖以下常用协议：

1. **VMess** (两种格式)
2. **VLESS**
3. **Trojan**
4. **Shadowsocks (ss)**

---

## 测试用例详细设计

### 1. VMess 协议测试 (2 个用例)

- [ ] `test_vmess_base64_json`: Base64 JSON 格式解析 (含 WS 传输层)
- [ ] `test_vmess_url_format`: URL 格式解析

### 2. VLESS 协议测试 (2 个用例)

- [ ] `test_vless_basic`: 基本 VLESS 链接解析
- [ ] `test_vless_reality`: Reality 安全配置

### 3. Trojan 协议测试 (1 个用例)

- [ ] `test_trojan_basic`: 基本 Trojan 链接解析 (含 SNI)

### 4. Shadowsocks (ss) 协议测试 (2 个用例)

- [ ] `test_ss_sip002_format`: SIP002 格式解析
- [ ] `test_ss_plain_format`: 明文格式解析

### 5. 通用测试 (3 个用例)

- [ ] `test_mixed_protocols`: 混合协议输入 + Base64 编码
- [ ] `test_empty_input`: 空输入应抛出异常
- [ ] `test_duplicate_names`: 重复名称自动添加后缀

---

## 测试数据示例

### VMess Base64 JSON

```python
VMESS_JSON = {
    "v": "2",
    "ps": "TestNode",
    "add": "192.168.1.1",
    "port": "443",
    "id": "a3482e88-686a-4a58-8126-99c9df64b060",
    "aid": "0",
    "scy": "auto",
    "net": "ws",
    "type": "none",
    "host": "example.com",
    "path": "/vmess",
    "tls": "tls"
}
# vmess:// + base64(json.dumps(VMESS_JSON))
```

### VLESS

```python
VLESS_LINK = "vless://a3482e88-686a-4a58-8126-99c9df64b060@192.168.1.1:443?encryption=none&security=tls&sni=example.com&type=ws&host=example.com&path=/vless#TestVLESS"
```

### Trojan

```python
TROJAN_LINK = "trojan://password123@192.168.1.1:443?security=tls&sni=example.com&type=tcp#TestTrojan"
```

### Shadowsocks

```python
# method:password = aes-256-gcm:testpassword
SS_LINK = "ss://YWVzLTI1Ni1nY206dGVzdHBhc3N3b3Jk@192.168.1.1:8388#TestSS"
```

---

## 预期输出结构

每个协议解析后应返回类似以下结构的字典：

```python
{
    "name": "节点名称",
    "type": "协议类型",  # vmess, vless, trojan, ss
    "server": "服务器地址",
    "port": 端口号,
    "uuid": "UUID (vmess/vless)",  # 或 "password" (trojan/ss)
    # ... 其他协议特定字段
}
```

---

## 环境配置

### 1. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### 2. 安装依赖

```bash
# 安装项目依赖
pip install -r requirements.txt

# 安装测试依赖
pip install -r requirements-dev.txt
```

---

## 运行测试

```bash
# 确保虚拟环境已激活
source .venv/bin/activate  # macOS/Linux

# 运行所有测试
pytest tests/test_converter.py -v

# 运行特定协议测试
pytest tests/test_converter.py -v -k "vmess"
pytest tests/test_converter.py -v -k "vless"
pytest tests/test_converter.py -v -k "trojan"
pytest tests/test_converter.py -v -k "ss"

# 查看测试覆盖率
pytest tests/test_converter.py -v --cov=modules/convert
```

---

## 实现步骤

1. 创建 `requirements-dev.txt` 包含测试依赖
2. 更新 `.gitignore` 忽略虚拟环境目录
3. 创建 `tests/` 目录结构
4. 创建 `tests/conftest.py` 配置异步测试支持
5. 创建 `tests/test_converter.py` 实现测试用例

---

## 新增文件清单

| 文件 | 描述 |
|------|------|
| `requirements-dev.txt` | 测试依赖 (pytest, pytest-asyncio, pytest-cov) |
| `tests/__init__.py` | 测试包初始化 |
| `tests/conftest.py` | pytest 配置和 fixtures |
| `tests/test_converter.py` | 主测试文件 |
