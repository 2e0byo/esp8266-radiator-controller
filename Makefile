.PHONY: all setup build deploy clean shell local-deploy

PORT = /dev/ttyUSB0

all: clean setup build

clean:
	find firmware/micropython/ports/esp8266/modules -type l -delete

setup:
	bash ci/setup.sh

build:
	bash ci/build.sh

deploy:
	esptool.py --port ${PORT} --baud 460800 write_flash --flash_size=detect 0 firmware/firmware-combined.bin

shell:
	python -m serial.tools.miniterm --rts 0 --dtr 0 --raw ${PORT} 115200

local-deploy:
	bash ./.local-deploy.sh ${PORT}
