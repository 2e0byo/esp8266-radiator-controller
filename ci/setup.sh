#!/bin/sh
set -e
set +x

cd firmware
MODULES=micropython/ports/esp8266/modules/

# setup external dependencies
find lib -maxdepth 1 -mindepth 1 -exec ln -rs {} $MODULES \;

# setup internal dependencies
find ../src -maxdepth 1 -mindepth 1 -type f -name '*.py' -exec ln -rs {} $MODULES \;
find ../src/ -maxdepth 1 -mindepth 1 -type d -exec ln -rs {} $MODULES \;
cd ../

echo "Done setting up"
