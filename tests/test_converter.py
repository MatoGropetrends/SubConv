import pytest
import json
import base64
from modules.convert import converter

# --- Helper Functions ---

def encode_base64(content: str) -> str:
    return base64.b64encode(content.encode('utf-8')).decode('utf-8')

def create_vmess_json(ps="test", add="127.0.0.1", port="443", id="uuid", net="ws", tls="tls"):
    return json.dumps({
        "v": "2",
        "ps": ps,
        "add": add,
        "port": port,
        "id": id,
        "aid": "0",
        "scy": "auto",
        "net": net,
        "type": "none",
        "host": add,
        "path": "/",
        "tls": tls
    })

# --- Test Cases ---

@pytest.mark.asyncio
async def test_vmess_base64_json():
    """测试 Base64 编码的 VMess JSON 格式 (含 WS 传输层)"""
    vmess_data = create_vmess_json(ps="vmess_ws_tls", net="ws", tls="tls")
    link = "vmess://" + encode_base64(vmess_data)
    
    proxies = await converter.ConvertsV2Ray(link)
    
    assert len(proxies) == 1
    p = proxies[0]
    assert p["name"] == "vmess_ws_tls"
    assert p["type"] == "vmess"
    assert p["server"] == "127.0.0.1"
    assert p["port"] == "443"
    assert p["uuid"] == "uuid"
    assert p["network"] == "ws"
    assert p["tls"] is True
    assert p["ws-opts"]["path"] == "/"

@pytest.mark.asyncio
async def test_vmess_url_format():
    """测试 VMess URL 格式 (Xray VMessAEAD)"""
    link = "vmess://uuid@127.0.0.1:443?security=tls&type=ws&path=/&host=example.com#vmess_url"
    
    proxies = await converter.ConvertsV2Ray(link)
    
    assert len(proxies) == 1
    p = proxies[0]
    assert p["name"] == "vmess_url"
    assert p["type"] == "vmess"
    assert p["server"] == "127.0.0.1"
    assert p["port"] == 443
    assert p["uuid"] == "uuid"
    assert p["network"] == "ws"
    assert p["tls"] is True
    assert p["ws-opts"]["headers"]["Host"] == "example.com"

@pytest.mark.asyncio
async def test_vless_basic():
    """测试基本 VLESS 链接解析"""
    link = "vless://uuid@127.0.0.1:443?encryption=none&security=tls&type=ws&host=example.com&path=/#vless_basic"
    
    proxies = await converter.ConvertsV2Ray(link)
    
    assert len(proxies) == 1
    p = proxies[0]
    assert p["name"] == "vless_basic"
    assert p["type"] == "vless"
    assert p["server"] == "127.0.0.1"
    assert p["port"] == 443
    assert p["uuid"] == "uuid"
    assert p["tls"] is True
    assert p["network"] == "ws"

@pytest.mark.asyncio
async def test_vless_reality():
    """测试 VLESS Reality 安全配置"""
    link = "vless://uuid@127.0.0.1:443?encryption=none&security=reality&pbk=public_key&sid=short_id&fp=chrome&type=tcp&sni=example.com#vless_reality"
    
    proxies = await converter.ConvertsV2Ray(link)
    
    assert len(proxies) == 1
    p = proxies[0]
    assert p["name"] == "vless_reality"
    assert p["type"] == "vless"
    assert p["tls"] is True
    assert p["servername"] == "example.com"
    assert p["reality-opts"]["public-key"] == "public_key"
    assert p["reality-opts"]["short-id"] == "short_id"
    assert p["client-fingerprint"] == "chrome"

@pytest.mark.asyncio
async def test_trojan_basic():
    """测试基本 Trojan 链接解析 (含 SNI)"""
    link = "trojan://password@127.0.0.1:443?security=tls&sni=example.com&type=tcp#trojan_basic"
    
    proxies = await converter.ConvertsV2Ray(link)
    
    assert len(proxies) == 1
    p = proxies[0]
    assert p["name"] == "trojan_basic"
    assert p["type"] == "trojan"
    assert p["server"] == "127.0.0.1"
    assert p["port"] == 443
    assert p["password"] == "password"
    assert p["sni"] == "example.com"

@pytest.mark.asyncio
async def test_ss_sip002_format():
    """测试 Shadowsocks SIP002 格式 (Base64 userinfo)"""
    # method:password = aes-256-gcm:password -> YWVzLTI1Ni1nY206cGFzc3dvcmQ=
    userinfo = encode_base64("aes-256-gcm:password")
    link = f"ss://{userinfo}@127.0.0.1:8388#ss_sip002"
    
    proxies = await converter.ConvertsV2Ray(link)
    
    assert len(proxies) == 1
    p = proxies[0]
    assert p["name"] == "ss_sip002"
    assert p["type"] == "ss"
    assert p["server"] == "127.0.0.1"
    assert p["port"] == 8388
    assert p["cipher"] == "aes-256-gcm"
    assert p["password"] == "password"

@pytest.mark.asyncio
async def test_ss_plain_format():
    """测试 Shadowsocks 明文格式"""
    link = "ss://aes-256-gcm:password@127.0.0.1:8388#ss_plain"
    
    proxies = await converter.ConvertsV2Ray(link)
    
    assert len(proxies) == 1
    p = proxies[0]
    assert p["name"] == "ss_plain"
    assert p["type"] == "ss"
    assert p["cipher"] == "aes-256-gcm"
    assert p["password"] == "password"

@pytest.mark.asyncio
async def test_mixed_protocols():
    """测试混合协议输入 + Base64 编码"""
    links = [
        "vmess://" + encode_base64(create_vmess_json(ps="node1")),
        "ss://aes-256-gcm:password@127.0.0.1:8388#node2"
    ]
    content = "\n".join(links)
    # 测试 Base64 编码的订阅内容
    encoded_content = encode_base64(content)
    
    proxies = await converter.ConvertsV2Ray(encoded_content)
    
    assert len(proxies) == 2
    assert proxies[0]["name"] == "node1"
    assert proxies[0]["type"] == "vmess"
    assert proxies[1]["name"] == "node2"
    assert proxies[1]["type"] == "ss"

@pytest.mark.asyncio
async def test_empty_input():
    """测试空输入"""
    # 预期会抛出异常 "No valid proxies found"
    with pytest.raises(Exception, match="No valid proxies found"):
        await converter.ConvertsV2Ray("")
    
    # None 输入会抛出 AttributeError，因为代码中没有对 None 进行检查
    with pytest.raises(AttributeError):
        await converter.ConvertsV2Ray(None)

@pytest.mark.asyncio
async def test_duplicate_names():
    """测试重复名称自动添加后缀"""
    # 两个节点都叫 "test_node"
    links = [
        "ss://aes-256-gcm:p1@1.1.1.1:8388#test_node",
        "ss://aes-256-gcm:p2@2.2.2.2:8388#test_node"
    ]
    content = "\n".join(links)
    
    proxies = await converter.ConvertsV2Ray(content)
    
    assert len(proxies) == 2
    assert proxies[0]["name"] == "test_node"
    assert proxies[1]["name"] == "test_node-01"

@pytest.mark.asyncio
async def test_real_subscription_link():
    """测试真实订阅链接内容解析"""
    # 模拟从 https://yt2.ewpbh.cn/api/v1/client/subscribe?token=93f8927e0bc8847fe488da7ce2d3a72f 获取的内容
    # 内容为 Base64 编码的字符串 "c3M6Ly9ZMmR6T..."
    # 解码后为 "ss://YWVzLTI1Ni1nY206dGVzdHBhc3N3b3Jk@127.0.0.1:8388#TestNode"
    
    # 构造模拟数据
    ss_link = "ss://YWVzLTI1Ni1nY206dGVzdHBhc3N3b3Jk@127.0.0.1:8388#TestNode"
    content = encode_base64(ss_link)
    
    proxies = await converter.ConvertsV2Ray(content)
    
    assert len(proxies) == 1
    p = proxies[0]
    assert p["name"] == "TestNode"
    assert p["type"] == "ss"
    assert p["server"] == "127.0.0.1"
    assert p["port"] == 8388
    assert p["cipher"] == "aes-256-gcm"
    assert p["password"] == "testpassword"
