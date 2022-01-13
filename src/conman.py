def connect():
    import secrets
    import network

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("connecting to network")
        sta_if.active(True)
        sta_if.connect(secrets.wifi_SSID, secrets.wifi_PSK)
        while not sta_if.isconnected():
            pass
    print("network config:", sta_if.ifconfig())
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Connected to network.")
