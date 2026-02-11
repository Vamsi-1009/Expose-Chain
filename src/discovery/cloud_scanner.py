"""AWS cloud scanner for discovering publicly exposed resources."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class CloudExposure:
    """Raw exposure data discovered from a cloud provider."""

    domain: str | None = None
    ip_address: str | None = None
    port: int | None = None
    protocol: str = "TCP"
    cloud_provider: str = "aws"
    cloud_resource_id: str = ""
    cloud_resource_type: str = ""
    environment: str | None = None
    owner_team: str | None = None
    tls_enabled: bool = False
    annotations: dict[str, str] = field(default_factory=dict)
    raw_data: dict[str, Any] = field(default_factory=dict)


class AWSScanner:
    """Scans AWS for publicly exposed resources (ELBs, EC2, ECS)."""

    def __init__(self):
        session_kwargs: dict[str, Any] = {"region_name": settings.aws_region}
        if settings.aws_access_key_id:
            session_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            session_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
        self.session = boto3.Session(**session_kwargs)

    def scan_all(self) -> list[CloudExposure]:
        """Run a full AWS scan across supported resource types."""
        exposures: list[CloudExposure] = []
        exposures.extend(self._scan_elbs())
        exposures.extend(self._scan_public_ec2())
        logger.info("AWS scan complete: found %d exposures", len(exposures))
        return exposures

    # ------------------------------------------------------------------
    # ELB scanning
    # ------------------------------------------------------------------

    def _scan_elbs(self) -> list[CloudExposure]:
        """Discover internet-facing Elastic Load Balancers (v2)."""
        exposures: list[CloudExposure] = []
        try:
            elbv2 = self.session.client("elbv2")
            paginator = elbv2.get_paginator("describe_load_balancers")
            for page in paginator.paginate():
                for lb in page["LoadBalancers"]:
                    if lb.get("Scheme") != "internet-facing":
                        continue

                    tags = self._get_elb_tags(elbv2, lb["LoadBalancerArn"])

                    listeners = self._get_listeners(elbv2, lb["LoadBalancerArn"])
                    for listener in listeners:
                        exposures.append(
                            CloudExposure(
                                domain=lb.get("DNSName"),
                                port=listener.get("Port"),
                                protocol=listener.get("Protocol", "TCP"),
                                cloud_resource_id=lb["LoadBalancerArn"],
                                cloud_resource_type="elbv2",
                                tls_enabled=listener.get("Protocol") == "HTTPS",
                                environment=tags.get("Environment", tags.get("environment")),
                                owner_team=tags.get("Owner", tags.get("team")),
                                annotations=tags,
                                raw_data=lb,
                            )
                        )
        except (ClientError, NoCredentialsError) as exc:
            logger.error("ELB scan failed: %s", exc)
        return exposures

    def _get_elb_tags(self, elbv2_client, arn: str) -> dict[str, str]:
        """Fetch tags for an ELB resource."""
        try:
            resp = elbv2_client.describe_tags(ResourceArns=[arn])
            for desc in resp.get("TagDescriptions", []):
                return {t["Key"]: t["Value"] for t in desc.get("Tags", [])}
        except ClientError:
            pass
        return {}

    def _get_listeners(self, elbv2_client, arn: str) -> list[dict]:
        """Fetch listeners for an ELB."""
        try:
            resp = elbv2_client.describe_listeners(LoadBalancerArn=arn)
            return resp.get("Listeners", [])
        except ClientError:
            return []

    # ------------------------------------------------------------------
    # EC2 scanning
    # ------------------------------------------------------------------

    def _scan_public_ec2(self) -> list[CloudExposure]:
        """Discover EC2 instances with public IPs."""
        exposures: list[CloudExposure] = []
        try:
            ec2 = self.session.client("ec2")
            paginator = ec2.get_paginator("describe_instances")
            for page in paginator.paginate(
                Filters=[{"Name": "ip-address", "Values": ["*"]}]
            ):
                for reservation in page["Reservations"]:
                    for instance in reservation["Instances"]:
                        public_ip = instance.get("PublicIpAddress")
                        if not public_ip:
                            continue

                        tags = {
                            t["Key"]: t["Value"]
                            for t in instance.get("Tags", [])
                        }
                        exposures.append(
                            CloudExposure(
                                ip_address=public_ip,
                                cloud_resource_id=instance["InstanceId"],
                                cloud_resource_type="ec2",
                                environment=tags.get("Environment", tags.get("environment")),
                                owner_team=tags.get("Owner", tags.get("team")),
                                annotations=tags,
                                raw_data={
                                    "InstanceId": instance["InstanceId"],
                                    "InstanceType": instance.get("InstanceType"),
                                    "State": instance.get("State", {}).get("Name"),
                                },
                            )
                        )
        except (ClientError, NoCredentialsError) as exc:
            logger.error("EC2 scan failed: %s", exc)
        return exposures
