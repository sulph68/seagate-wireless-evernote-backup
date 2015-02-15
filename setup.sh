#!/bin/sh
. /opt/etc/network-ssid

PLUGIN_NAME="evernote"

PLUGIN_MAIN_DIR="/static/Data/1/plugins"
PLUGIN_DIR="$PLUGIN_MAIN_DIR/$PLUGIN_NAME"
PLUGIN_CACHE_DIR="$PLUGIN_DIR/cache"
PLUGIN_FILE_DIR="$PLUGIN_DIR/files"

SCRIPTS_DIR="/static/Data/1/scripts"

if [ ! -e "$PLUGIN_MAIN_DIR" ]; then
  echo "Making plugin directory"
  mkdir "$PLUGIN_MAIN_DIR"
fi

if [ ! -e "$PLUGIN_DIR" ]; then
  echo "Making plugin directory for $PLUGIN_NAME"
  mkdir "$PLUGIN_DIR"
fi

if [ ! -e "$PLUGIN_CACHE_DIR" ]; then
  echo "Making cache directory for $PLUGIN_NAME"
  mkdir "$PLUGIN_CACHE_DIR"
fi

if [ ! -e "$PLUGIN_FILE_DIR" ]; then
  echo "Making file directory for $PLUGIN_NAME"
  mkdir "$PLUGIN_FILE_DIR"
fi

if [ ! -e "$SCRIPTS_DIR" ]; then
  echo "Making custom scripts directory"
  mkdir "$SCRIPTS_DIR"
fi


echo "Directories are ready."
echo "Browse to http://$HOSTNAME.local/plugins/$PLUGIN_NAME/index.py to configure"

echo "Copying custom run script integration"
cp "$PLUGIN_DIR/run_evernote_sync.sh" "$SCRIPTS_DIR/scripts/run_evernote_sync.sh"
