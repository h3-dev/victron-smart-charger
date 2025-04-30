#!/bin/bash

SERVICE_NAME="victron-smart-charger"
SERVICE_LINK="/service/$SERVICE_NAME"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
RCLOCAL="/data/rc.local"

echo "🔧 Deinstalliere $SERVICE_NAME ..."

# Dienst stoppen und Symlink entfernen
if [ -L "$SERVICE_LINK" ]; then
    echo "🛑 Entferne Symlink $SERVICE_LINK"
    svc -d "$SERVICE_LINK"
    rm -f "$SERVICE_LINK"
else
    echo "⚠️  Kein Symlink unter $SERVICE_LINK gefunden."
fi

# Entferne Eintrag aus /data/rc.local
if [ -f "$RCLOCAL" ]; then
    grep -v "$SCRIPT_DIR/start.sh" "$RCLOCAL" > "$RCLOCAL.tmp" && mv "$RCLOCAL.tmp" "$RCLOCAL"
    echo "🧹 Start-Eintrag aus $RCLOCAL entfernt"
fi

echo "✅ $SERVICE_NAME wurde deinstalliert."