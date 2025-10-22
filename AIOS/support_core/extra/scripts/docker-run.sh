#!/bin/bash
# CARMA Docker Run Script
# Provides easy commands to run different CARMA components in Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== CARMA Docker Management Script ===${NC}"

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build           - Build the Docker image"
    echo "  test            - Run basic functionality test"
    echo "  human-eval      - Run human evaluation system"
    echo "  ablation        - Run ablation tests (dry-run)"
    echo "  luna            - Run Luna learning system"
    echo "  shell           - Open interactive shell in container"
    echo "  logs            - Show container logs"
    echo "  clean           - Clean up containers and images"
    echo "  compose-up      - Start all services with docker-compose"
    echo "  compose-down    - Stop all services"
    echo ""
}

# Function to build image
build_image() {
    echo -e "${YELLOW}Building CARMA Docker image...${NC}"
    docker build -t carma-system .
    echo -e "${GREEN}✓ Image built successfully${NC}"
}

# Function to run basic test
run_test() {
    echo -e "${YELLOW}Running basic functionality test...${NC}"
    docker run --rm carma-system python human_eval/human_eval_prep.py --sample --questions 5
    echo -e "${GREEN}✓ Test completed successfully${NC}"
}

# Function to run human evaluation
run_human_eval() {
    echo -e "${YELLOW}Running human evaluation system...${NC}"
    docker run --rm -v "$(pwd)/human_eval:/app/human_eval" -v "$(pwd)/reports:/app/reports" \
        carma-system python human_eval/human_eval_prep.py --sample --questions 120
    echo -e "${GREEN}✓ Human evaluation completed${NC}"
}

# Function to run ablation tests
run_ablation() {
    echo -e "${YELLOW}Running ablation tests (dry-run)...${NC}"
    docker run --rm -v "$(pwd)/ablation_results:/app/ablation_results" \
        carma-system python "Hive Mind/ablation_runner.py" --dry-run
    echo -e "${GREEN}✓ Ablation tests completed${NC}"
}

# Function to run Luna system
run_luna() {
    echo -e "${YELLOW}Running Luna learning system...${NC}"
    echo -e "${RED}Note: This requires LM Studio running on host at localhost:1234${NC}"
    docker run --rm -v "$(pwd)/carma_data:/app/carma_data" -v "$(pwd)/telemetry_data:/app/telemetry_data" \
        carma-system python "Hive Mind/luna_main.py" --mode real_learning --questions 10
    echo -e "${GREEN}✓ Luna system completed${NC}"
}

# Function to open shell
open_shell() {
    echo -e "${YELLOW}Opening interactive shell in CARMA container...${NC}"
    docker run --rm -it -v "$(pwd):/app/host" carma-system /bin/bash
}

# Function to show logs
show_logs() {
    echo -e "${YELLOW}Showing container logs...${NC}"
    docker logs carma-system 2>/dev/null || echo "No running container found"
}

# Function to clean up
cleanup() {
    echo -e "${YELLOW}Cleaning up Docker resources...${NC}"
    docker stop $(docker ps -q --filter ancestor=carma-system) 2>/dev/null || true
    docker rm $(docker ps -aq --filter ancestor=carma-system) 2>/dev/null || true
    docker rmi carma-system 2>/dev/null || true
    echo -e "${GREEN}✓ Cleanup completed${NC}"
}

# Function to start with docker-compose
compose_up() {
    echo -e "${YELLOW}Starting CARMA services with docker-compose...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✓ Services started${NC}"
    echo "Services available:"
    echo "  - CARMA System: carma-system"
    echo "  - Redis: localhost:6379"
    echo "  - Human Eval: carma-human-eval"
    echo "  - Ablation: carma-ablation"
}

# Function to stop with docker-compose
compose_down() {
    echo -e "${YELLOW}Stopping CARMA services...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ Services stopped${NC}"
}

# Main command handling
case "${1:-}" in
    "build")
        build_image
        ;;
    "test")
        run_test
        ;;
    "human-eval")
        run_human_eval
        ;;
    "ablation")
        run_ablation
        ;;
    "luna")
        run_luna
        ;;
    "shell")
        open_shell
        ;;
    "logs")
        show_logs
        ;;
    "clean")
        cleanup
        ;;
    "compose-up")
        compose_up
        ;;
    "compose-down")
        compose_down
        ;;
    *)
        show_usage
        ;;
esac
