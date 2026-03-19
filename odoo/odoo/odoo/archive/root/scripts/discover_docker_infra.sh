#!/bin/bash
# Docker Infrastructure Discovery
# Parses docker-compose.yml files to discover services, networks, and volumes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$REPO_ROOT/infra/infra_graph/sources"

echo "============================================================"
echo "Docker Infrastructure Discovery"
echo "============================================================"
echo ""

mkdir -p "$OUTPUT_DIR"

NODES_FILE="$OUTPUT_DIR/docker_nodes.json"
EDGES_FILE="$OUTPUT_DIR/docker_edges.json"

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

    # Append to nodes array using jq
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

# Discover docker-compose files
COMPOSE_FILES=(
    "$REPO_ROOT/docker-compose.yml"
    "$REPO_ROOT/deploy/docker-compose.prod.yml"
    "$REPO_ROOT/sandbox/dev/docker-compose.yml"
)

TOTAL_SERVICES=0
TOTAL_NETWORKS=0
TOTAL_VOLUMES=0

for compose_file in "${COMPOSE_FILES[@]}"; do
    if [ ! -f "$compose_file" ]; then
        echo "⏭️  Skipping (not found): $compose_file"
        continue
    fi

    echo "Parsing: $compose_file"

    # Extract relative path for stack identification
    relative_path="${compose_file#$REPO_ROOT/}"
    stack_name=$(echo "$relative_path" | tr '/' '-' | sed 's/docker-compose\.yml//' | sed 's/-$//' | sed 's/\.yml$//')
    stack_name="${stack_name:-default}"

    stack_id="docker:stack:$stack_name"

    # Create stack node
    add_node "$stack_id" "docker" "stack" "$stack_name" "Docker Stack: $stack_name" "{\"compose_file\": \"$relative_path\"}"

    # Extract services
    services=$(docker compose -f "$compose_file" config --services 2>/dev/null || echo "")

    if [ -n "$services" ]; then
        service_count=$(echo "$services" | wc -l | tr -d ' ')
        echo "  Found $service_count services"
        TOTAL_SERVICES=$((TOTAL_SERVICES + service_count))

        while IFS= read -r service; do
            if [ -z "$service" ]; then
                continue
            fi

            service_id="docker:service:$stack_name:$service"

            # Get service image (if available)
            image=$(docker compose -f "$compose_file" config | yq eval ".services.$service.image // \"unknown\"" - 2>/dev/null || echo "unknown")

            # Create service node
            props=$(cat <<EOF
{
  "stack": "$stack_name",
  "service_name": "$service",
  "image": "$image",
  "compose_file": "$relative_path"
}
EOF
)
            add_node "$service_id" "docker" "service" "$stack_name:$service" "$service" "$props"

            # Edge: stack HAS_SERVICE service
            add_edge "$stack_id→$service_id" "docker" "$stack_id" "$service_id" "HAS_SERVICE" '{}'

        done <<< "$services"
    fi

    # Extract networks
    networks=$(docker compose -f "$compose_file" config 2>/dev/null | yq eval '.networks | keys | .[]' - 2>/dev/null || echo "")

    if [ -n "$networks" ]; then
        network_count=$(echo "$networks" | grep -v '^$' | wc -l | tr -d ' ')
        if [ "$network_count" -gt 0 ]; then
            echo "  Found $network_count networks"
            TOTAL_NETWORKS=$((TOTAL_NETWORKS + network_count))

            while IFS= read -r network; do
                if [ -z "$network" ] || [ "$network" = "null" ]; then
                    continue
                fi

                network_id="docker:network:$stack_name:$network"

                # Create network node
                props=$(cat <<EOF
{
  "stack": "$stack_name",
  "network_name": "$network",
  "compose_file": "$relative_path"
}
EOF
)
                add_node "$network_id" "docker" "network" "$stack_name:$network" "$network" "$props"

                # Edge: stack HAS_NETWORK network
                add_edge "$stack_id→$network_id" "docker" "$stack_id" "$network_id" "HAS_NETWORK" '{}'

            done <<< "$networks"
        fi
    fi

    # Extract volumes
    volumes=$(docker compose -f "$compose_file" config 2>/dev/null | yq eval '.volumes | keys | .[]' - 2>/dev/null || echo "")

    if [ -n "$volumes" ]; then
        volume_count=$(echo "$volumes" | grep -v '^$' | wc -l | tr -d ' ')
        if [ "$volume_count" -gt 0 ]; then
            echo "  Found $volume_count volumes"
            TOTAL_VOLUMES=$((TOTAL_VOLUMES + volume_count))

            while IFS= read -r volume; do
                if [ -z "$volume" ] || [ "$volume" = "null" ]; then
                    continue
                fi

                volume_id="docker:volume:$stack_name:$volume"

                # Create volume node
                props=$(cat <<EOF
{
  "stack": "$stack_name",
  "volume_name": "$volume",
  "compose_file": "$relative_path"
}
EOF
)
                add_node "$volume_id" "docker" "volume" "$stack_name:$volume" "$volume" "$props"

                # Edge: stack HAS_VOLUME volume
                add_edge "$stack_id→$volume_id" "docker" "$stack_id" "$volume_id" "HAS_VOLUME" '{}'

            done <<< "$volumes"
        fi
    fi

    echo ""
done

# Count final results
TOTAL_NODES=$(jq 'length' "$NODES_FILE")
TOTAL_EDGES=$(jq 'length' "$EDGES_FILE")

echo "============================================================"
echo "✅ Docker discovery complete"
echo "============================================================"
echo "Nodes discovered: $TOTAL_NODES"
echo "  Services: $TOTAL_SERVICES"
echo "  Networks: $TOTAL_NETWORKS"
echo "  Volumes: $TOTAL_VOLUMES"
echo "Edges discovered: $TOTAL_EDGES"
echo ""
echo "Output files:"
echo "  $NODES_FILE"
echo "  $EDGES_FILE"
echo ""
echo "Next step: Run scripts/build_infra_graph.py to merge into unified graph"
echo ""
