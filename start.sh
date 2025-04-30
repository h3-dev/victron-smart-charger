#!/bin/bash
# start.sh - Startet den Victron Smart Charger Daemon

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
chmod +x $SCRIPT_DIR/service/run
chmod +x $SCRIPT_DIR/service/log/run

# Symlink setzen (wenn noch nicht vorhanden)
ln -sfn $SCRIPT_DIR/service /service/victron-smart-charger

echo "✅ Service gestartet (bzw. symbolisch verlinkt in /service)"