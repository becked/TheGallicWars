#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CSPROJ="$PROJECT_ROOT/src/GallicWarsMod/GallicWarsMod.csproj"
MOD_DIR="$PROJECT_ROOT/GallicWars"

echo "Building GallicWarsMod..."
dotnet build "$CSPROJ" -c Release

BUILD_OUT="$PROJECT_ROOT/src/GallicWarsMod/bin/Release/net472"

cp "$BUILD_OUT/GallicWarsMod.dll" "$MOD_DIR/"
cp "$BUILD_OUT/0Harmony.dll" "$MOD_DIR/"

echo "Copied GallicWarsMod.dll and 0Harmony.dll to $MOD_DIR/"
