#!/bin/bash
# DigitalOcean Infrastructure Discovery
# Queries DigitalOcean API for droplets, databases, apps, and volumes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$REPO_ROOT/infra/infra_graph/sources"

# Check for required environment variables
if [ -z "$DO_API_TOKEN" ] && [ -z "$DIGITALOCEAN_ACCESS_TOKEN" ]; then
    echo "ERROR: Missing DigitalOcean API credentials"
    echo "Required environment variables:"
    echo "  - DO_API_TOKEN or DIGITALOCEAN_ACCESS_TOKEN"
    exit 1
fi

# Use DO_API_TOKEN if available, otherwise DIGITALOCEAN_ACCESS_TOKEN
API_TOKEN="${DO_API_TOKEN:-$DIGITALOCEAN_ACCESS_TOKEN}"
PROJECT_ID="${DO_PROJECT_ID:-29cde7a1-8280-46ad-9fdf-dea7b21a7825}"

echo "============================================================"
echo "DigitalOcean Infrastructure Discovery"
echo "============================================================"
echo ""

mkdir -p "$OUTPUT_DIR"

NODES_FILE="$OUTPUT_DIR/digitalocean_nodes.json"
EDGES_FILE="$OUTPUT_DIR/digitalocean_edges.json"

# Initialize JSON arrays
echo "[]" > "$NODES_FILE"
echo "[]" > "$EDGES_FILE"

# Helper function to add node
add_node() {
    local id="$1"
    local source="$2"
    local kind="$3"
    local key="$4"
    local name="$5"
    local props="$6"

    local node=$(cat <<EOF
{
  "id": "$id",
  "source": "$source",
  "kind": "$kind",
  "key": "$key",
  "name": "$name",
  "props": $props
}
EOF
)

    # Append to nodes array
    jq --argjson node "$node" '. += [$node]' "$NODES_FILE" > "$NODES_FILE.tmp"
    mv "$NODES_FILE.tmp" "$NODES_FILE"
}

# Helper function to add edge
add_edge() {
    local id="$1"
    local source="$2"
    local from_id="$3"
    local to_id="$4"
    local type="$5"
    local props="$6"

    local edge=$(cat <<EOF
{
  "id": "$id",
  "source": "$source",
  "from_id": "$from_id",
  "to_id": "$to_id",
  "type": "$type",
  "props": $props
}
EOF
)

    # Append to edges array
    jq --argjson edge "$edge" '. += [$edge]' "$EDGES_FILE" > "$EDGES_FILE.tmp"
    mv "$EDGES_FILE.tmp" "$EDGES_FILE"
}

# Create project node
PROJECT_NODE_ID="digitalocean:project:$PROJECT_ID"
add_node "$PROJECT_NODE_ID" "digitalocean" "project" "$PROJECT_ID" "fin-workspace" '{"project_id": "'$PROJECT_ID'"}'

echo "Discovering droplets..."
DROPLETS=$(curl -s -X GET \
    -H "Authorization: Bearer $API_TOKEN" \
    "https://api.digitalocean.com/v2/droplets" | jq -r '.droplets // []')

DROPLET_COUNT=$(echo "$DROPLETS" | jq 'length')
echo "  Found $DROPLET_COUNT droplets"

# Process droplets
echo "$DROPLETS" | jq -c '.[]' | while read -r droplet; do
    droplet_id=$(echo "$droplet" | jq -r '.id')
    droplet_name=$(echo "$droplet" | jq -r '.name')
    region=$(echo "$droplet" | jq -r '.region.slug')
    size=$(echo "$droplet" | jq -r '.size.slug')
    status=$(echo "$droplet" | jq -r '.status')
    ip=$(echo "$droplet" | jq -r '.networks.v4[0].ip_address // "none"')
    memory=$(echo "$droplet" | jq -r '.memory')
    vcpus=$(echo "$droplet" | jq -r '.vcpus')
    disk=$(echo "$droplet" | jq -r '.disk')

    node_id="digitalocean:droplet:$droplet_id"
    props=$(cat <<EOF
{
  "droplet_id": "$droplet_id",
  "region": "$region",
  "size": "$size",
  "status": "$status",
  "ip_address": "$ip",
  "memory_mb": $memory,
  "vcpus": $vcpus,
  "disk_gb": $disk
}
EOF
)

    add_node "$node_id" "digitalocean" "droplet" "$droplet_id" "$droplet_name" "$props"
    add_edge "$PROJECT_NODE_ID→$node_id" "digitalocean" "$PROJECT_NODE_ID" "$node_id" "OWNS" '{}'
done

echo ""
echo "Discovering App Platform apps..."
APPS=$(curl -s -X GET \
    -H "Authorization: Bearer $API_TOKEN" \
    "https://api.digitalocean.com/v2/apps" | jq -r '.apps // []')

APP_COUNT=$(echo "$APPS" | jq 'length')
echo "  Found $APP_COUNT apps"

# Process apps
echo "$APPS" | jq -c '.[]' | while read -r app; do
    app_id=$(echo "$app" | jq -r '.id')
    app_name=$(echo "$app" | jq -r '.spec.name')
    region=$(echo "$app" | jq -r '.region.slug // "unknown"')
    live_url=$(echo "$app" | jq -r '.live_url // "none"')
    default_domain=$(echo "$app" | jq -r '.default_ingress // "none"')

    node_id="digitalocean:app:$app_id"
    props=$(cat <<EOF
{
  "app_id": "$app_id",
  "region": "$region",
  "live_url": "$live_url",
  "default_domain": "$default_domain"
}
EOF
)

    add_node "$node_id" "digitalocean" "app" "$app_id" "$app_name" "$props"
    add_edge "$PROJECT_NODE_ID→$node_id" "digitalocean" "$PROJECT_NODE_ID" "$node_id" "OWNS" '{}'
done

echo ""
echo "Discovering databases..."
DATABASES=$(curl -s -X GET \
    -H "Authorization: Bearer $API_TOKEN" \
    "https://api.digitalocean.com/v2/databases" | jq -r '.databases // []')

DATABASE_COUNT=$(echo "$DATABASES" | jq 'length')
echo "  Found $DATABASE_COUNT databases"

# Process databases
echo "$DATABASES" | jq -c '.[]' | while read -r database; do
    db_id=$(echo "$database" | jq -r '.id')
    db_name=$(echo "$database" | jq -r '.name')
    engine=$(echo "$database" | jq -r '.engine')
    version=$(echo "$database" | jq -r '.version')
    region=$(echo "$database" | jq -r '.region')
    status=$(echo "$database" | jq -r '.status')
    num_nodes=$(echo "$database" | jq -r '.num_nodes')

    node_id="digitalocean:database:$db_id"
    props=$(cat <<EOF
{
  "database_id": "$db_id",
  "engine": "$engine",
  "version": "$version",
  "region": "$region",
  "status": "$status",
  "num_nodes": $num_nodes
}
EOF
)

    add_node "$node_id" "digitalocean" "database" "$db_id" "$db_name" "$props"
    add_edge "$PROJECT_NODE_ID→$node_id" "digitalocean" "$PROJECT_NODE_ID" "$node_id" "OWNS" '{}'
done

# Count final results
TOTAL_NODES=$(jq 'length' "$NODES_FILE")
TOTAL_EDGES=$(jq 'length' "$EDGES_FILE")

echo ""
echo "============================================================"
echo "✅ DigitalOcean discovery complete"
echo "============================================================"
echo "Nodes discovered: $TOTAL_NODES"
echo "  Project: 1"
echo "  Droplets: $DROPLET_COUNT"
echo "  Apps: $APP_COUNT"
echo "  Databases: $DATABASE_COUNT"
echo "Edges discovered: $TOTAL_EDGES"
echo ""
echo "Output files:"
echo "  $NODES_FILE"
echo "  $EDGES_FILE"
echo ""
echo "Next step: Run scripts/build_infra_graph.py to merge into unified graph"
echo ""
