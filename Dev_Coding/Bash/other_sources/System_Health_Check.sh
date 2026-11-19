#!/bin/bash
# Other Sources: System Resource and Health Check Utility
# Summarizes system uptime, disk usage, memory, and top active processes

echo "=========================================="
echo "          SYSTEM HEALTH REPORT            "
echo "=========================================="
echo "Date / Time: $(date)"
echo ""

echo "--- Host & Kernel Info ---"
uname -a 2>/dev/null || echo "Host: $HOSTNAME"
echo ""

echo "--- Disk Space Usage ---"
df -h . 2>/dev/null || echo "Disk check skipped."
echo ""

echo "--- Memory Usage ---"
free -m 2>/dev/null || echo "Memory check skipped."
echo ""

echo "=========================================="
echo "Report generated successfully."
