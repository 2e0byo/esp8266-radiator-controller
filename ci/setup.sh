#!/bin/sh
set -e
set +x

cd firmware
# setup external dependencies
MODULES=micropython/ports/esp8266/modules/
ln -rs micropython-lib/python-stdlib/logging/logging.py $MODULES
ln -rs tinyweb/tinyweb $MODULES
ln -rs micropython-async/v3/primitives $MODULES

# setup internal dependencies
find ../src -type f -name '*.py' -maxdepth 1 -exec ln -rs {} $MODULES \;
find ../src -type d -maxdepth 1 -exec ln -rs {} $MODULES \;
cd ../

echo "Done setting up"
