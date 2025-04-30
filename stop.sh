#!/bin/bash
# stop.sh - Stoppt den Service sauber

rm -f /service/victron-smart-charger
svc -d /service/victron-smart-charger
echo "🛑 Service wurde gestoppt und deaktiviert."