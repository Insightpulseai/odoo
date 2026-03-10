#!/usr/bin/env python3
"""
Docker Infrastructure Discovery

Discovers Docker containers, images, networks, and volumes.
Works with local Docker daemon or remote Docker host via SSH.
"""

import json
import logging
import os
import subprocess
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def run_docker_command(cmd: list, host: Optional[str] = None) -> Optional[str]:
    """Run a docker command locally or via SSH."""
    if host:
        full_cmd = ["ssh", host, "docker"] + cmd
    else:
        full_cmd = ["docker"] + cmd

    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
        else:
            logger.warning(f"Docker command failed: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        logger.error("Docker command timed out")
        return None
    except FileNotFoundError:
        logger.error("Docker not found")
        return None


def discover_docker(orchestrator) -> Dict[str, Any]:
    """
    Discover Docker infrastructure and store in KG.

    Returns summary of discovered resources.
    """
    docker_host = os.environ.get("DOCKER_HOST_SSH")  # e.g., root@178.128.112.214

    discovered = {"containers": 0, "images": 0, "networks": 0, "volumes": 0}

    # Check if Docker is available
    version = run_docker_command(["--version"], docker_host)
    if not version:
        return {"skipped": True, "reason": "Docker not available"}

    try:
        # Create Docker host node
        host_label = docker_host if docker_host else "local"
        host_node_id = orchestrator.upsert_node(
            kind="docker_host",
            key=f"docker:host:{host_label}",
            label=f"Docker Host ({host_label})",
            attrs={"version": version.strip(), "host": docker_host or "local"},
        )

        # Discover containers
        containers_json = run_docker_command(
            ["ps", "-a", "--format", "{{json .}}"], docker_host
        )

        if containers_json:
            container_nodes = {}

            for line in containers_json.strip().split("\n"):
                if not line:
                    continue
                try:
                    container = json.loads(line)

                    # Get detailed inspect data
                    inspect_json = run_docker_command(
                        ["inspect", container["ID"]], docker_host
                    )
                    inspect_data = {}
                    if inspect_json:
                        inspect_list = json.loads(inspect_json)
                        if inspect_list:
                            inspect_data = inspect_list[0]

                    node_id = orchestrator.upsert_node(
                        kind="docker_container",
                        key=f"docker:container:{container['ID']}",
                        label=container["Names"],
                        attrs={
                            "container_id": container["ID"],
                            "image": container["Image"],
                            "status": container["Status"],
                            "state": container["State"],
                            "ports": container.get("Ports", ""),
                            "created": container.get("CreatedAt"),
                            "networks": list(
                                inspect_data.get("NetworkSettings", {})
                                .get("Networks", {})
                                .keys()
                            ),
                            "mounts": [
                                m.get("Source") for m in inspect_data.get("Mounts", [])
                            ],
                            "env_vars": [
                                e.split("=")[0]
                                for e in inspect_data.get("Config", {}).get("Env", [])
                                if "=" in e
                            ],
                        },
                    )
                    container_nodes[container["ID"]] = node_id
                    discovered["containers"] += 1

                    # Link container to host
                    orchestrator.upsert_edge(
                        src_node_id=node_id,
                        predicate="RUNS_ON",
                        dst_node_id=host_node_id,
                        source_type="docker",
                        source_ref=f"docker:container:{container['ID']}",
                    )

                except json.JSONDecodeError:
                    continue

        # Discover images
        images_json = run_docker_command(
            ["images", "--format", "{{json .}}"], docker_host
        )

        if images_json:
            image_nodes = {}

            for line in images_json.strip().split("\n"):
                if not line:
                    continue
                try:
                    image = json.loads(line)

                    # Skip dangling images
                    if image["Repository"] == "<none>":
                        continue

                    image_key = f"{image['Repository']}:{image['Tag']}"
                    node_id = orchestrator.upsert_node(
                        kind="docker_image",
                        key=f"docker:image:{image['ID']}",
                        label=image_key,
                        attrs={
                            "image_id": image["ID"],
                            "repository": image["Repository"],
                            "tag": image["Tag"],
                            "size": image["Size"],
                            "created": image.get("CreatedAt"),
                        },
                    )
                    image_nodes[image["ID"]] = node_id
                    discovered["images"] += 1

                    # Link image to containers using it
                    for container_id, container_node_id in container_nodes.items():
                        # Check if container uses this image
                        inspect_json = run_docker_command(
                            ["inspect", "--format", "{{.Image}}", container_id],
                            docker_host,
                        )
                        if inspect_json and image["ID"] in inspect_json:
                            orchestrator.upsert_edge(
                                src_node_id=container_node_id,
                                predicate="USES_IMAGE",
                                dst_node_id=node_id,
                                source_type="docker",
                                source_ref=f"docker:container:{container_id}",
                            )

                except json.JSONDecodeError:
                    continue

        # Discover networks
        networks_json = run_docker_command(
            ["network", "ls", "--format", "{{json .}}"], docker_host
        )

        if networks_json:
            network_nodes = {}

            for line in networks_json.strip().split("\n"):
                if not line:
                    continue
                try:
                    network = json.loads(line)

                    node_id = orchestrator.upsert_node(
                        kind="docker_network",
                        key=f"docker:network:{network['ID']}",
                        label=network["Name"],
                        attrs={
                            "network_id": network["ID"],
                            "driver": network["Driver"],
                            "scope": network["Scope"],
                        },
                    )
                    network_nodes[network["Name"]] = node_id
                    discovered["networks"] += 1

                except json.JSONDecodeError:
                    continue

            # Link containers to networks
            for container_id, container_node_id in container_nodes.items():
                inspect_json = run_docker_command(
                    [
                        "inspect",
                        "--format",
                        "{{json .NetworkSettings.Networks}}",
                        container_id,
                    ],
                    docker_host,
                )
                if inspect_json:
                    try:
                        networks = json.loads(inspect_json)
                        for network_name in networks.keys():
                            if network_name in network_nodes:
                                orchestrator.upsert_edge(
                                    src_node_id=container_node_id,
                                    predicate="CONNECTED_TO",
                                    dst_node_id=network_nodes[network_name],
                                    source_type="docker",
                                    source_ref=f"docker:container:{container_id}:network",
                                )
                    except json.JSONDecodeError:
                        pass

        # Discover volumes
        volumes_json = run_docker_command(
            ["volume", "ls", "--format", "{{json .}}"], docker_host
        )

        if volumes_json:
            for line in volumes_json.strip().split("\n"):
                if not line:
                    continue
                try:
                    volume = json.loads(line)

                    node_id = orchestrator.upsert_node(
                        kind="docker_volume",
                        key=f"docker:volume:{volume['Name']}",
                        label=volume["Name"],
                        attrs={
                            "driver": volume["Driver"],
                            "mountpoint": volume.get("Mountpoint"),
                        },
                    )
                    discovered["volumes"] += 1

                except json.JSONDecodeError:
                    continue

    except Exception as e:
        logger.error(f"Docker discovery error: {e}")
        discovered["error"] = str(e)

    return discovered


if __name__ == "__main__":
    # Standalone test
    class MockOrchestrator:
        def upsert_node(self, kind, key, label, attrs):
            print(f"Node: {kind}/{key} ({label})")
            return key

        def upsert_edge(self, src_node_id, predicate, dst_node_id, **kwargs):
            print(f"Edge: {src_node_id} --{predicate}--> {dst_node_id}")
            return f"{src_node_id}:{predicate}:{dst_node_id}"

    result = discover_docker(MockOrchestrator())
    print(f"Result: {result}")
