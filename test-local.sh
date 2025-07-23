#!/bin/bash

# Local testing script for National Grid Home Assistant Add-on
set -e

# Configuration
IMAGE_NAME="nationalgrid-addon-test"
CONTAINER_NAME="nationalgrid-test"
PORT=50583

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required environment variables are set
check_env_vars() {
    if [ -z "$NATIONAL_GRID_USERNAME" ] || [ -z "$NATIONAL_GRID_PASSWORD" ]; then
        print_error "Required environment variables not set!"
        echo "Please set the following environment variables:"
        echo "  export NATIONAL_GRID_USERNAME='your_username'"
        echo "  export NATIONAL_GRID_PASSWORD='your_password'"
        echo ""
        echo "Example:"
        echo "  export NATIONAL_GRID_USERNAME='mdhislam@yahoo.com'"
        echo "  export NATIONAL_GRID_PASSWORD='your_password'"
        echo "  ./test-local.sh"
        exit 1
    fi
}

# Function to build the Docker image locally
build_local_image() {
    print_status "Building local test image..."
    
    # Use amd64 base image for local testing
    local BASE_IMAGE="ghcr.io/home-assistant/amd64-base-python:3.11-alpine3.18"
    
    cd nationalgrid-nyc-metro
    
    if docker build --build-arg BUILD_FROM="$BASE_IMAGE" -t "$IMAGE_NAME" .; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
    
    cd ..
}

# Function to stop and remove existing container
cleanup_container() {
    if docker ps -a --format 'table {{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
        print_status "Stopping and removing existing test container"
        docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
    fi
}

# Function to run the container locally
run_test_container() {
    print_status "Running test container on port $PORT"
    
    if docker run -d \
        --name "$CONTAINER_NAME" \
        -p "$PORT:$PORT" \
        -e USERNAME="$NATIONAL_GRID_USERNAME" \
        -e PASSWORD="$NATIONAL_GRID_PASSWORD" \
        -e LOG_LEVEL="debug" \
        "$IMAGE_NAME"; then
        
        print_success "Test container started successfully"
        
        # Wait for container to start
        print_status "Waiting for container to initialize..."
        sleep 10
        
        # Check if container is running
        if docker ps --filter "name=$CONTAINER_NAME" --filter "status=running" | grep -q "$CONTAINER_NAME"; then
            print_success "Container is running!"
            return 0
        else
            print_error "Container failed to start"
            print_status "Container logs:"
            docker logs "$CONTAINER_NAME"
            return 1
        fi
    else
        print_error "Failed to start test container"
        exit 1
    fi
}

# Function to test API endpoints
test_api_endpoints() {
    print_status "Testing API endpoints..."
    
    echo ""
    print_status "1. Testing health endpoint..."
    if curl -s -f "http://localhost:$PORT/health" > /dev/null; then
        print_success "Health endpoint is working"
        curl -s "http://localhost:$PORT/health" | jq .
    else
        print_error "Health endpoint failed"
        return 1
    fi
    
    echo ""
    print_status "2. Testing API info endpoint..."
    if curl -s -f "http://localhost:$PORT/" > /dev/null; then
        print_success "API info endpoint is working"
        curl -s "http://localhost:$PORT/" | jq .
    else
        print_error "API info endpoint failed"
        return 1
    fi
    
    echo ""
    print_status "3. Testing usage endpoint (this may take a while for browser automation)..."
    print_warning "This will test the actual login process with your credentials..."
    
    # Give it more time for the browser automation
    if timeout 120 curl -s -f "http://localhost:$PORT/usage" > /tmp/usage_test.json; then
        print_success "Usage endpoint is working!"
        
        # Check if we got valid data
        if jq -e '.success' /tmp/usage_test.json > /dev/null; then
            print_success "Got valid usage data!"
            echo "Summary:"
            jq '.data.summary' /tmp/usage_test.json
            
            # Check current month estimate
            if jq -e '.data.current_month_estimate' /tmp/usage_test.json > /dev/null; then
                echo ""
                echo "Current month estimate:"
                jq '.data.current_month_estimate' /tmp/usage_test.json
            fi
        else
            print_error "Got response but with errors:"
            jq . /tmp/usage_test.json
            return 1
        fi
    else
        print_error "Usage endpoint failed or timed out"
        print_status "Container logs (last 50 lines):"
        docker logs --tail 50 "$CONTAINER_NAME"
        return 1
    fi
}

# Function to show container logs
show_logs() {
    print_status "Container logs:"
    docker logs -f "$CONTAINER_NAME"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up test environment..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    docker rmi "$IMAGE_NAME" 2>/dev/null || true
    rm -f /tmp/usage_test.json
    print_success "Cleanup completed"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  test      - Build and run full test (default)"
    echo "  build     - Build Docker image only"
    echo "  run       - Run container only (requires built image)"
    echo "  logs      - Show container logs"
    echo "  stop      - Stop test container"
    echo "  clean     - Remove test container and image"
    echo "  help      - Show this help message"
    echo ""
    echo "Environment Variables Required:"
    echo "  NATIONAL_GRID_USERNAME - Your National Grid username"
    echo "  NATIONAL_GRID_PASSWORD - Your National Grid password"
}

# Main script logic
case "${1:-test}" in
    "test")
        check_env_vars
        cleanup_container
        build_local_image
        if run_test_container; then
            test_api_endpoints
            echo ""
            print_success "All tests passed! 🎉"
            echo ""
            echo "Container is still running for manual testing:"
            echo "  Health: http://localhost:$PORT/health"
            echo "  Usage:  http://localhost:$PORT/usage"
            echo "  Info:   http://localhost:$PORT/"
            echo ""
            echo "To stop: ./test-local.sh stop"
        else
            print_error "Tests failed"
            exit 1
        fi
        ;;
    "build")
        build_local_image
        ;;
    "run")
        check_env_vars
        cleanup_container
        run_test_container
        ;;
    "logs")
        show_logs
        ;;
    "stop")
        cleanup_container
        ;;
    "clean")
        cleanup
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac 