#!/bin/sh

PLUGIN_NAME="evernote"

PLUGIN_MAIN_DIR="/static/Data/1/plugins"
PLUGIN_DIR="$PLUGIN_MAIN_DIR/$PLUGIN_NAME"
PLUGIN_CACHE_DIR="$PLUGIN_DIR/cache"
PLUGIN_FILE_DIR="$PLUGIN_DIR/files"

SCRIPT="evernote-sync.py"

cd "$PLUGIN_DIR"
echo "Executing script $PLUGIN_DIR/$SCRIPT"
echo "Log available in $PLUGIN_DIR/evernote-sync.log"

$PLUGIN_DIR/$SCRIPT > $PLUGIN_DIR/evernote-sync.log 2>&1

