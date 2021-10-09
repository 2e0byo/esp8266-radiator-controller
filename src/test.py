from time import sleep

from machine import PWM, Pin

buzzer = PWM(Pin(12))
buzzer.duty(0)

sound = True


def siren():
    buzzer.duty(512)
    while sound:
        buzzer.freq(440)
        sleep(0.5)
        buzzer.freq(600)
        sleep(0.5)
    buzzer.duty(0)


def ring():
    buzzer.freq(600)
    while sound:
        for i in range(2):
            buzzer.duty(512)
            sleep(0.1)
            buzzer.duty(0)
            sleep(0.1)
        sleep(0.4)

    buzzer.duty(0)
