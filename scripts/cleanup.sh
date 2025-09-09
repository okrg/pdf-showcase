#!/usr/bin/env bash
set -euo pipefail

# Determine output directory relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)/output"

if [ ! -d "${OUTPUT_DIR}" ]; then
  echo "Output directory not found: ${OUTPUT_DIR}" >&2
  exit 1
fi

# Delete files older than 24 hours
find "${OUTPUT_DIR}" -type f -mtime +0 -delete