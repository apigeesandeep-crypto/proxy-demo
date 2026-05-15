#!/usr/bin/env python3
"""
generate_xml.py
Generates all required XML configuration files for the Apigee proxy-demo-1 bundle.
Proxy enforces a single Quota policy on every inbound request.
"""

import os
import sys
import textwrap

PROXY_NAME = "proxy-demo-1"


# ─────────────────────────────────────────────
# XML content definitions
# ─────────────────────────────────────────────

def proxy_descriptor_xml() -> str:
    """Root proxy descriptor: apiproxy/proxy-demo-1.xml"""
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <APIProxy revision="1" name="{PROXY_NAME}">
            <DisplayName>{PROXY_NAME}</DisplayName>
            <Description>Demo API Proxy with Quota enforcement, deployed via GitHub Actions</Description>
            <BasePaths>/{PROXY_NAME}</BasePaths>
            <Policies>
                <Policy>Quota-Default</Policy>
            </Policies>
            <ProxyEndpoints>
                <ProxyEndpoint>default</ProxyEndpoint>
            </ProxyEndpoints>
            <TargetEndpoints>
                <TargetEndpoint>default</TargetEndpoint>
            </TargetEndpoints>
        </APIProxy>
    """)


def proxy_endpoint_xml() -> str:
    """Proxy endpoint: apiproxy/proxies/default.xml
    Quota-Default is applied in the PreFlow so every request is checked
    before it reaches the target, regardless of path or verb.
    """
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <ProxyEndpoint name="default">
            <Description>Default Proxy Endpoint - Quota enforced on all requests</Description>

            <PreFlow name="PreFlow">
                <Request>
                    <Step>
                        <Name>Quota-Default</Name>
                    </Step>
                </Request>
                <Response/>
            </PreFlow>

            <PostFlow name="PostFlow">
                <Request/>
                <Response/>
            </PostFlow>

            <Flows/>

            <HTTPProxyConnection>
                <BasePath>/{PROXY_NAME}</BasePath>
                <VirtualHost>secure</VirtualHost>
            </HTTPProxyConnection>

            <RouteRule name="default">
                <TargetEndpoint>default</TargetEndpoint>
            </RouteRule>
        </ProxyEndpoint>
    """)


def target_endpoint_xml() -> str:
    """Target endpoint: apiproxy/targets/default.xml"""
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <TargetEndpoint name="default">
            <Description>Default Target Endpoint</Description>

            <PreFlow name="PreFlow">
                <Request/>
                <Response/>
            </PreFlow>

            <PostFlow name="PostFlow">
                <Request/>
                <Response/>
            </PostFlow>

            <HTTPTargetConnection>
                <URL>https://mocktarget.apigee.net</URL>
            </HTTPTargetConnection>
        </TargetEndpoint>
    """)


def quota_policy_xml() -> str:
    """Quota policy: apiproxy/policies/Quota-Default.xml
    Allows 1000 calls per month per client. Distributed + synchronous
    ensures accurate counting across all Apigee instances.
    """
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Quota name="Quota-Default" continueOnError="false" enabled="true">
            <DisplayName>Quota-Default</DisplayName>
            <Allow count="3"/>
            <Interval>1</Interval>
            <TimeUnit>minute</TimeUnit>
            <Distributed>true</Distributed>
            <Synchronous>true</Synchronous>
            <UseQuotaConfigInAPIProduct>true</UseQuotaConfigInAPIProduct>
        </Quota>
    """)


# ─────────────────────────────────────────────
# File manifest  (only 4 files — no other policies)
# ─────────────────────────────────────────────

FILE_MANIFEST = [
    (f"apiproxy/{PROXY_NAME}.xml",             proxy_descriptor_xml),
    ("apiproxy/proxies/default.xml",           proxy_endpoint_xml),
    ("apiproxy/targets/default.xml",           target_endpoint_xml),
    ("apiproxy/policies/Quota-Default.xml",    quota_policy_xml),
]


def write_files(base_path: str = ".") -> None:
    for relative_path, content_fn in FILE_MANIFEST:
        full_path = os.path.join(base_path, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        content = content_fn()
        with open(full_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"[OK] Written: {full_path}")


def main():
    base_path = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"==> Generating XML files under: {os.path.abspath(base_path)}")
    write_files(base_path)
    print("==> XML generation complete.")


if __name__ == "__main__":
    main()
