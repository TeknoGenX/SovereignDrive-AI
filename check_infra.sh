#!/bin/bash

# AwanDrive X - Infrastructure Health Checker
# Script untuk mengecek apakah semua container pendukung sudah siap.

RED='\033[0-9;31m'
GREEN='\033[0-9;32m'
YELLOW='\033[0-9;33m'
BLUE='\033[0-9;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Memulai Health Check Infrastruktur AwanDrive X...${NC}\n"

check_container() {
    local name=$1
    local port=$2
    
    echo -n "Checking $name ($port)... "
    if nc -z localhost $port; then
        echo -e "${GREEN}ONLINE${NC}"
        return 0
    else
        echo -e "${RED}OFFLINE${NC}"
        return 1
    fi
}

# 1. Cek PostgreSQL
check_container "PostgreSQL" 5432
RET_DB=$?

# 2. Cek Redis
check_container "Redis" 6379
RET_RD=$?

# 3. Cek Elasticsearch
check_container "Elasticsearch" 9200
RET_ES=$?

echo -e "\n--------------------------------------------"

if [ $RET_DB -eq 0 ] && [ $RET_RD -eq 0 ] && [ $RET_ES -eq 0 ]; then
    echo -e "${GREEN}🚀 SEMUA SISTEM SIAP! Silakan mulai coding.${NC}"
else
    echo -e "${YELLOW}⚠️  PERHATIAN: Beberapa layanan belum siap.${NC}"
    echo -e "Jalankan: ${BLUE}./run_services.sh${NC} untuk memulai infrastruktur."
fi
echo -e "--------------------------------------------\n"
