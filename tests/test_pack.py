from types import SimpleNamespace

import pytest
import yaml

from modules import config
from modules.config import Group
from modules import pack


@pytest.mark.asyncio
async def test_proxy_groups_can_reference_generated_groups(monkeypatch):
    monkeypatch.setattr(
        config,
        "configInstance",
        SimpleNamespace(
            HEAD={},
            TEST_URL="https://example.test/generate_204",
            RULESET=[],
            CUSTOM_PROXY_GROUP=[
                Group(
                    name="Primary A",
                    type="select",
                    rule=False,
                    regex="node-a",
                ),
                Group(
                    name="Backup Speed Pool",
                    type="url-test",
                    rule=False,
                    regex="node-b|node-c",
                    interval=30,
                    tolerance=20,
                ),
                Group(
                    name="Primary Failover",
                    type="fallback",
                    rule=False,
                    proxy_groups=["Primary A", "Backup Speed Pool"],
                    interval=45,
                    tolerance=30,
                ),
            ],
        ),
    )

    result_yaml = await pack.pack(
        url=["https://example.test/sub.yaml"],
        urlstandalone=[],
        urlstandby=[],
        urlstandbystandalone=[],
        content=[
            """
- name: node-a
- name: node-b
- name: node-c
"""
        ],
        interval="1800",
        domain="example.test",
        short=None,
        notproxyrule="1",
        base_url="http://localhost/",
    )
    result = yaml.safe_load(result_yaml)

    groups = {group["name"]: group for group in result["proxy-groups"]}

    assert groups["Backup Speed Pool"]["type"] == "url-test"
    assert groups["Backup Speed Pool"]["filter"] == "node-b|node-c"
    assert groups["Backup Speed Pool"]["use"] == ["subscription0"]
    assert groups["Backup Speed Pool"]["url"] == "https://example.test/generate_204"
    assert groups["Backup Speed Pool"]["interval"] == 30
    assert groups["Backup Speed Pool"]["tolerance"] == 20

    assert groups["Primary Failover"]["type"] == "fallback"
    assert groups["Primary Failover"]["proxies"] == ["Primary A", "Backup Speed Pool"]
    assert groups["Primary Failover"]["url"] == "https://example.test/generate_204"
    assert groups["Primary Failover"]["interval"] == 45
    assert groups["Primary Failover"]["tolerance"] == 30
