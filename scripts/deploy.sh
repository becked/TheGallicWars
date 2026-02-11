#!/bin/bash
# deploy.sh - Deploy GallicWars mod to local Old World mods folder for testing
#
# Prerequisites:
#   .env file with OLDWORLD_MODS_PATH set
#
# Usage: ./scripts/deploy.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Load .env
if [ -f ".env" ]; then
    source ".env"
else
    echo "Error: .env file not found"
    echo "Create a .env file with OLDWORLD_MODS_PATH set"
    echo "See .env.example for template"
    exit 1
fi

if [ -z "$OLDWORLD_MODS_PATH" ]; then
    echo "Error: OLDWORLD_MODS_PATH not set in .env"
    exit 1
fi

MOD_FOLDER="$OLDWORLD_MODS_PATH/GallicWars"

echo "=== Building CrcFix DLL ==="
"$SCRIPT_DIR/build_dll.sh"

echo ""
echo "=== Deploying GallicWars to mods folder ==="
echo "Target: $MOD_FOLDER"

rm -rf "$MOD_FOLDER"
mkdir -p "$MOD_FOLDER"

cp GallicWars/ModInfo.xml "$MOD_FOLDER/"
cp -r GallicWars/Infos "$MOD_FOLDER/"
cp -r GallicWars/Maps "$MOD_FOLDER/"
cp GallicWars/CrcFix.dll "$MOD_FOLDER/"
cp GallicWars/0Harmony.dll "$MOD_FOLDER/"

echo ""
echo "=== Deployment complete ==="
echo "Deployed files:"
ls -la "$MOD_FOLDER/"
