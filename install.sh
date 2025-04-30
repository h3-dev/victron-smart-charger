#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

chmod +x $SCRIPT_DIR/start.sh
chmod +x $SCRIPT_DIR/stop.sh
chmod +x $SCRIPT_DIR/uninstall.sh
chmod +x $SCRIPT_DIR/service/run
chmod +x $SCRIPT_DIR/service/log/run

# Startskript in rc.local eintragen (überlebt Reboot)
RCLOCAL=/data/rc.local
if [ ! -f $RCLOCAL ]; then
  echo "#!/bin/bash" > $RCLOCAL
  chmod 755 $RCLOCAL
fi
grep -qxF "$SCRIPT_DIR/start.sh" $RCLOCAL || echo "$SCRIPT_DIR/start.sh" >> $RCLOCAL

# Startservice
$SCRIPT_DIR/start.sh
