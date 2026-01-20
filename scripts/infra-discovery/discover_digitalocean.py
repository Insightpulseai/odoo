#!/usr/bin/env python3
"""
DigitalOcean Infrastructure Discovery

Discovers droplets, managed databases, and other DO resources.
"""

import logging
import os
from typing import Any, Dict

import requests

logger = logging.getLogger(__name__)

DO_API_URL = 'https://api.digitalocean.com/v2'


def discover_digitalocean(orchestrator) -> Dict[str, Any]:
    """
    Discover DigitalOcean infrastructure and store in KG.

    Returns summary of discovered resources.
    """
    token = os.environ.get('DIGITALOCEAN_TOKEN')

    if not token:
        logger.warning("DIGITALOCEAN_TOKEN not set, skipping DO discovery")
        return {'skipped': True, 'reason': 'DIGITALOCEAN_TOKEN not set'}

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    discovered = {
        'droplets': 0,
        'databases': 0,
        'domains': 0,
        'volumes': 0
    }

    try:
        # Discover Droplets
        droplets_resp = requests.get(f'{DO_API_URL}/droplets', headers=headers)
        droplets_resp.raise_for_status()
        droplets = droplets_resp.json().get('droplets', [])

        droplet_nodes = {}

        for droplet in droplets:
            # Get public IPv4
            public_ip = None
            for network in droplet.get('networks', {}).get('v4', []):
                if network.get('type') == 'public':
                    public_ip = network.get('ip_address')
                    break

            node_id = orchestrator.upsert_node(
                kind='droplet',
                key=f"do:droplet:{droplet['id']}",
                label=droplet['name'],
                attrs={
                    'do_id': droplet['id'],
                    'region': droplet['region']['slug'],
                    'size': droplet['size_slug'],
                    'vcpus': droplet['vcpus'],
                    'memory': droplet['memory'],
                    'disk': droplet['disk'],
                    'status': droplet['status'],
                    'public_ip': public_ip,
                    'image': droplet['image']['slug'] if droplet.get('image') else None,
                    'created_at': droplet.get('created_at'),
                    'tags': droplet.get('tags', [])
                }
            )
            droplet_nodes[droplet['id']] = node_id
            discovered['droplets'] += 1

        # Discover Managed Databases
        databases_resp = requests.get(f'{DO_API_URL}/databases', headers=headers)
        databases_resp.raise_for_status()
        databases = databases_resp.json().get('databases', [])

        db_nodes = {}

        for db in databases:
            node_id = orchestrator.upsert_node(
                kind='managed_db',
                key=f"do:database:{db['id']}",
                label=db['name'],
                attrs={
                    'do_id': db['id'],
                    'engine': db['engine'],
                    'version': db['version'],
                    'region': db['region'],
                    'size': db['size'],
                    'num_nodes': db['num_nodes'],
                    'status': db['status'],
                    'host': db.get('connection', {}).get('host'),
                    'port': db.get('connection', {}).get('port'),
                    'created_at': db.get('created_at'),
                    'tags': db.get('tags', [])
                }
            )
            db_nodes[db['id']] = node_id
            discovered['databases'] += 1

            # Create edges from droplets that might use this database
            # (based on tags or naming convention)
            for droplet_id, droplet_node_id in droplet_nodes.items():
                if 'odoo' in db['name'].lower():
                    orchestrator.upsert_edge(
                        src_node_id=droplet_node_id,
                        predicate='USES_DB',
                        dst_node_id=node_id,
                        source_type='digitalocean',
                        source_ref=f"do:inferred:{droplet_id}:{db['id']}"
                    )

        # Discover Domains
        domains_resp = requests.get(f'{DO_API_URL}/domains', headers=headers)
        domains_resp.raise_for_status()
        domains = domains_resp.json().get('domains', [])

        for domain in domains:
            domain_node_id = orchestrator.upsert_node(
                kind='domain',
                key=f"do:domain:{domain['name']}",
                label=domain['name'],
                attrs={
                    'ttl': domain.get('ttl'),
                    'zone_file': domain.get('zone_file')
                }
            )
            discovered['domains'] += 1

            # Get domain records
            records_resp = requests.get(
                f'{DO_API_URL}/domains/{domain["name"]}/records',
                headers=headers
            )
            if records_resp.status_code == 200:
                records = records_resp.json().get('domain_records', [])

                for record in records:
                    if record['type'] == 'A':
                        # Link A records to droplets by IP
                        for droplet in droplets:
                            for network in droplet.get('networks', {}).get('v4', []):
                                if network.get('ip_address') == record.get('data'):
                                    orchestrator.upsert_edge(
                                        src_node_id=domain_node_id,
                                        predicate='ROUTES_TO',
                                        dst_node_id=droplet_nodes.get(droplet['id']),
                                        source_type='digitalocean',
                                        source_ref=f"do:dns:{domain['name']}:{record['id']}"
                                    )

        # Discover Volumes
        volumes_resp = requests.get(f'{DO_API_URL}/volumes', headers=headers)
        volumes_resp.raise_for_status()
        volumes = volumes_resp.json().get('volumes', [])

        for volume in volumes:
            volume_node_id = orchestrator.upsert_node(
                kind='volume',
                key=f"do:volume:{volume['id']}",
                label=volume['name'],
                attrs={
                    'do_id': volume['id'],
                    'region': volume['region']['slug'],
                    'size_gigabytes': volume['size_gigabytes'],
                    'filesystem_type': volume.get('filesystem_type'),
                    'created_at': volume.get('created_at')
                }
            )
            discovered['volumes'] += 1

            # Link to attached droplets
            for droplet_id in volume.get('droplet_ids', []):
                if droplet_id in droplet_nodes:
                    orchestrator.upsert_edge(
                        src_node_id=volume_node_id,
                        predicate='ATTACHED_TO',
                        dst_node_id=droplet_nodes[droplet_id],
                        source_type='digitalocean',
                        source_ref=f"do:volume:{volume['id']}"
                    )

    except requests.RequestException as e:
        logger.error(f"DigitalOcean API error: {e}")
        discovered['error'] = str(e)

    return discovered


if __name__ == '__main__':
    # Standalone test
    class MockOrchestrator:
        def upsert_node(self, kind, key, label, attrs):
            print(f"Node: {kind}/{key} ({label})")
            return key

        def upsert_edge(self, src_node_id, predicate, dst_node_id, **kwargs):
            print(f"Edge: {src_node_id} --{predicate}--> {dst_node_id}")
            return f"{src_node_id}:{predicate}:{dst_node_id}"

    result = discover_digitalocean(MockOrchestrator())
    print(f"Result: {result}")
