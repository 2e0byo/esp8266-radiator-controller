def connect():
    import secrets
    import network
    import clock

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("connecting to network")
        sta_if.active(True)
        sta_if.connect(secrets.wifi_SSID, secrets.wifi_PSK)
        while not sta_if.isconnected():
            pass
    print("network config:", sta_if.ifconfig())
    try:
        clock.set_offset()
        print("offset set.")
    except Exception:
        pass
    clock.clock_syncing = True
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Connected to network.")
