#!/usr/bin/env python3
"""
generate_xml.py
Generates all required XML configuration files for the Apigee proxy-demo-1 bundle.
Each XML file is written into the correct folder under apiproxy/.
"""

import os
import sys
import textwrap

PROXY_NAME = "proxy-demo-1"
BASE_PATH = "."

# ─────────────────────────────────────────────
# XML content definitions
# ─────────────────────────────────────────────

def proxy_descriptor_xml() -> str:
    """Root proxy descriptor: apiproxy/proxy-demo-1.xml"""
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <APIProxy revision="1" name="{PROXY_NAME}">
            <DisplayName>{PROXY_NAME}</DisplayName>
            <Description>Demo API Proxy deployed via GitHub Actions</Description>
            <BasePath>/proxy-demo-1</BasePath>
            <Policies>
                <Policy>AM-SetCORSHeaders</Policy>
                <Policy>RF-InvalidRequest</Policy>
                <Policy>Quota-Default</Policy>
                <Policy>SC-LogRequest</Policy>
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
    """Proxy endpoint: apiproxy/proxies/default.xml"""
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <ProxyEndpoint name="default">
            <Description>Default Proxy Endpoint</Description>

            <PreFlow name="PreFlow">
                <Request>
                    <Step>
                        <Name>Quota-Default</Name>
                    </Step>
                    <Step>
                        <Name>AM-SetCORSHeaders</Name>
                    </Step>
                </Request>
                <Response/>
            </PreFlow>

            <PostFlow name="PostFlow">
                <Request/>
                <Response>
                    <Step>
                        <Name>SC-LogRequest</Name>
                    </Step>
                </Response>
            </PostFlow>

            <Flows>
                <Flow name="GetResource">
                    <Description>Handles GET requests</Description>
                    <Request>
                        <Step>
                            <Condition>request.verb != "GET"</Condition>
                            <Name>RF-InvalidRequest</Name>
                        </Step>
                    </Request>
                    <Response/>
                    <Condition>(proxy.pathsuffix MatchesPath "/resource") and (request.verb = "GET")</Condition>
                </Flow>
            </Flows>

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


def assign_message_cors_xml() -> str:
    """CORS headers policy: apiproxy/policies/AM-SetCORSHeaders.xml"""
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <AssignMessage name="AM-SetCORSHeaders" continueOnError="false" enabled="true">
            <DisplayName>AM-SetCORSHeaders</DisplayName>
            <Add>
                <Headers>
                    <Header name="Access-Control-Allow-Origin">*</Header>
                    <Header name="Access-Control-Allow-Headers">Origin, X-Requested-With, Content-Type, Accept, Authorization</Header>
                    <Header name="Access-Control-Allow-Methods">GET, POST, PUT, DELETE, OPTIONS</Header>
                </Headers>
            </Add>
            <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
            <AssignTo createNew="false" transport="http" type="response"/>
        </AssignMessage>
    """)


def raise_fault_xml() -> str:
    """Raise fault for invalid requests: apiproxy/policies/RF-InvalidRequest.xml"""
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <RaiseFault name="RF-InvalidRequest" continueOnError="false" enabled="true">
            <DisplayName>RF-InvalidRequest</DisplayName>
            <FaultResponse>
                <Set>
                    <StatusCode>405</StatusCode>
                    <ReasonPhrase>Method Not Allowed</ReasonPhrase>
                    <Payload contentType="application/json">
                        {
                            "error": "Method Not Allowed",
                            "message": "The HTTP method used is not supported for this resource."
                        }
                    </Payload>
                </Set>
            </FaultResponse>
            <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
        </RaiseFault>
    """)


def quota_policy_xml() -> str:
    """Quota policy: apiproxy/policies/Quota-Default.xml"""
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


def service_callout_log_xml() -> str:
    """Service callout for logging: apiproxy/policies/SC-LogRequest.xml"""
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <ServiceCallout name="SC-LogRequest" continueOnError="true" enabled="true">
            <DisplayName>SC-LogRequest</DisplayName>
            <Request clearPayload="false" variable="loggingRequest">
                <Set>
                    <Headers>
                        <Header name="Content-Type">application/json</Header>
                    </Headers>
                    <Payload contentType="application/json">
                        {
                            "proxy": "{proxy.name}",
                            "path": "{proxy.pathsuffix}",
                            "verb": "{request.verb}",
                            "client_ip": "{client.ip}",
                            "timestamp": "{system.timestamp}"
                        }
                    </Payload>
                    <Verb>POST</Verb>
                </Set>
            </Request>
            <Response>loggingResponse</Response>
            <HTTPTargetConnection>
                <URL>https://logging.example.com/log</URL>
            </HTTPTargetConnection>
        </ServiceCallout>
    """)


# ─────────────────────────────────────────────
# File manifest
# ─────────────────────────────────────────────

FILE_MANIFEST = [
    (f"apiproxy/{PROXY_NAME}.xml",              proxy_descriptor_xml),
    ("apiproxy/proxies/default.xml",            proxy_endpoint_xml),
    ("apiproxy/targets/default.xml",            target_endpoint_xml),
    ("apiproxy/policies/AM-SetCORSHeaders.xml", assign_message_cors_xml),
    ("apiproxy/policies/RF-InvalidRequest.xml", raise_fault_xml),
    ("apiproxy/policies/Quota-Default.xml",     quota_policy_xml),
    ("apiproxy/policies/SC-LogRequest.xml",     service_callout_log_xml),
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

