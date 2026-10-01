"""
core/generators/spiffe_spire.py
=============================================================================
Universal Cognitive Decomposition Engine (UCDE) - Wave 2
Department 4: Information Security, Zero-Trust & DevSecOps Tooling.

Generates SPIFFE/SPIRE Workload Identities and mTLS Sidecar Configurations:
- SPIFFE ID standard: spiffe://cognitive.internal/ns/ministries/sa/{node_name}
- SVID (SPIFFE Verifiable Identity Document) X.509 profiles
- SPIRE Server & Agent configuration files (HCL syntax)
- Envoy Proxy mTLS zero-trust ingress/egress filter definitions
=============================================================================
"""

import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SpiffeRegistrationEntry(BaseModel):
    """SPIRE workload registration entry."""
    model_config = ConfigDict(extra="forbid")

    spiffe_id: str = Field(description="Уникальный идентификатор SPIFFE ID")
    parent_id: str = Field(description="SPIFFE ID агента-родителя")
    selectors: List[str] = Field(description="Селекторы рабочей нагрузки (k8s, unix, docker)")
    ttl_seconds: int = Field(default=3600, ge=300, description="Время жизни SVID сертификата в секундах")
    admin: bool = Field(default=False, description="Признак административных привилегий")


class SpiffeIdentityManifest(BaseModel):
    """Complete SPIFFE/SPIRE Identity & mTLS Manifest."""
    model_config = ConfigDict(extra="forbid")

    trust_domain: str = Field(default="cognitive.internal", description="Доверенный домен SPIFFE")
    server_config_hcl: str = Field(description="Конфигурация SPIRE Server (HCL)")
    agent_config_hcl: str = Field(description="Конфигурация SPIRE Agent (HCL)")
    envoy_mtls_config_yaml: str = Field(description="Конфигурация Envoy mTLS Proxy")
    entries: List[SpiffeRegistrationEntry] = Field(description="Реестр записей рабочих нагрузок 7 Министерств")


class SpiffeSpireGenerator:
    """
    Generates SPIFFE/SPIRE cryptographic identities and mTLS filters.
    """

    def generate(self, security_artifact: Optional[Dict[str, Any]] = None) -> SpiffeIdentityManifest:
        """
        Synthesizes complete SPIFFE/SPIRE configuration for all 7 ministries and core engines.
        """
        trust_domain = "cognitive.internal"
        parent_id = f"spiffe://{trust_domain}/spire/agent/node-orchestrator"

        nodes = [
            ("strategy-cjm", "ministry-1-strategy", False),
            ("finance-finops", "ministry-2-finance", False),
            ("legal-compliance", "ministry-3-legal", False),
            ("infosec-zerotrust", "ministry-4-security", True),
            ("system-architecture", "ministry-5-analysis", False),
            ("hardware-npu", "ministry-6-hardware", False),
            ("vv-certification", "ministry-7-quality", False),
            ("saga-orchestrator", "system-orchestrator", True),
            ("pbft-consensus", "system-consensus", False),
            ("z3-formal-verifier", "system-verifier", False),
        ]

        entries: List[SpiffeRegistrationEntry] = []
        for name, comp_id, is_admin in nodes:
            ns = "system" if "system" in comp_id else "ministries"
            entries.append(SpiffeRegistrationEntry(
                spiffe_id=f"spiffe://{trust_domain}/ns/{ns}/sa/{name}",
                parent_id=parent_id,
                selectors=[
                    f"unix:uid:1000",
                    f"k8s:ns:{ns}",
                    f"k8s:sa:{name}",
                    f"env:COMPONENT_ID:{comp_id}",
                ],
                ttl_seconds=3600,
                admin=is_admin,
            ))

        # SPIRE Server Config
        server_hcl = f"""server {{
  bind_address = "0.0.0.0"
  bind_port = "8081"
  trust_domain = "{trust_domain}"
  data_dir = "/var/spire/data"
  log_level = "INFO"
  default_svid_ttl = "1h"
  ca_subject = {{
    country = ["RU"]
    organization = ["Cognitive Systems JSC"]
    common_name = "{trust_domain} Root CA"
  }}
}}

plugins {{
  DataStore "sql" {{
    plugin_data {{
      database_type = "sqlite3"
      connection_string = "/var/spire/data/datastore.sqlite3"
    }}
  }}
  KeyManager "disk" {{
    plugin_data {{
      keys_path = "/var/spire/data/keys.json"
    }}
  }}
  NodeAttestor "x509pop" {{
    plugin_data {{}}
  }}
}}
"""

        # SPIRE Agent Config
        agent_hcl = f"""agent {{
  data_dir = "/var/spire/agent"
  log_level = "INFO"
  server_address = "spire-server"
  server_port = "8081"
  socket_path = "/tmp/spire-agent/public/api.sock"
  trust_bundle_path = "/var/spire/agent/bootstrap.crt"
  trust_domain = "{trust_domain}"
}}

plugins {{
  NodeAttestor "x509pop" {{
    plugin_data {{}}
  }}
  KeyManager "disk" {{
    plugin_data {{
      directory = "/var/spire/agent"
    }}
  }}
  WorkloadAttestor "unix" {{
    plugin_data {{
      discover_workload_path = true
    }}
  }}
}}
"""

        # Envoy Proxy mTLS Config with SPIFFE validation
        envoy_yaml = f"""static_resources:
  listeners:
  - name: ingress_mtls_listener
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 8443
    filter_chains:
    - transport_socket:
        name: envoy.transport_sockets.tls
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
          common_tls_context:
            tls_params:
              tls_minimum_protocol_version: TLSv1_3
            combined_validation_context:
              default_validation_context:
                match_typed_subject_alt_names:
                - san_type: URI
                  matcher:
                    prefix: "spiffe://{trust_domain}/"
              validation_context_sds_secret_config:
                name: "spiffe://{trust_domain}"
                sds_config:
                  api_config_source:
                    api_type: GRPC
                    transport_api_version: V3
                    grpc_services:
                    - envoy_grpc:
                        cluster_name: spire_agent
            tls_certificate_sds_secret_configs:
            - name: "spiffe://{trust_domain}/ns/system/sa/envoy-proxy"
              sds_config:
                api_config_source:
                  api_type: GRPC
                  transport_api_version: V3
                  grpc_services:
                  - envoy_grpc:
                      cluster_name: spire_agent
          require_client_certificate: true
"""

        return SpiffeIdentityManifest(
            trust_domain=trust_domain,
            server_config_hcl=server_hcl,
            agent_config_hcl=agent_hcl,
            envoy_mtls_config_yaml=envoy_yaml,
            entries=entries,
        )


__all__ = ["SpiffeRegistrationEntry", "SpiffeIdentityManifest", "SpiffeSpireGenerator"]
