.PHONY: all setup build deploy

PORT = /dev/ttyUSB0

all: setup build

setup:
	bash ci/setup.sh

build:
	bash ci/build.sh

deploy:
	esptool.py --port ${PORT} --baud 460800 write_flash --flash_size=detect 0 firmware/firmware-combined.bin

