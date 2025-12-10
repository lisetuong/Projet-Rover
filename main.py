from machine import Pin
from time import sleep

def delay_ms(ms):
    sleep(ms/1000)

def delay_s(s):
    sleep(s)

led = Pin("LED", Pin.OUT)

while True:
    led.value(1)
    delay_ms(100)
    led.value(0)
    delay_s(1)