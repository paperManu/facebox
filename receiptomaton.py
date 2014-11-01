#!/bin/bash python

import io, time
import RPi.GPIO as GPIO
import picamera
import subprocess
#import aalib
from PIL import Image
from Adafruit_Thermal import *

printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

def capture():
    stream = io.BytesIO()
    #camera.capture("image.jpg")
    camera.capture(stream, format='jpeg')
    stream.seek(0)
    image = Image.open(stream)
    image = image.convert("L")
    image = image.resize((384, 384 * image.size[1] / image.size[0]))
    
    printer.printImage(image, False)

def blink():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    state = 0

    while True:
        inputState = GPIO.input(23)
        print(inputState)
        time.sleep(0.5)
        if state == 0:
            state = 1
            GPIO.output(18, GPIO.HIGH)
        else:
            state = 0
            GPIO.output(18, GPIO.LOW)

def cameraMode():
    printer.upsideDownOn()
    printer.boldOn()
    printer.println("Facebox")
    printer.boldOff()
    printer.feed(6)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.output(18, GPIO.HIGH)

    stream = io.BytesIO()

    while True: 
        inputState = GPIO.input(23)
        # If the button has been pressed
        if inputState == 0:
            pressTime = time.time()
            # Check if the button is held
            while GPIO.input(23) == 0:
                time.sleep(0.5)
                pressedTime = time.time() - pressTime
                if pressedTime > 5:
                    GPIO.output(18, GPIO.LOW)
                    command = "/usr/bin/sudo /sbin/shutdown -h now"
                    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                    output = process.communicate()[0]
                    print output
                    
            # Activate the camera
            camera = picamera.PiCamera()
            waitTime = 0
            ledState = 0
            # Make the led blink before the photo
            while waitTime < 6:
                waitTime += 1
                if ledState == 0:
                    GPIO.output(18, GPIO.HIGH)
                    ledState = 1
                else:
                    GPIO.output(18, GPIO.LOW)
                    ledState = 0
                time.sleep(0.5)

            camera.capture(stream, format='jpeg')
            stream.seek(0)
            image = Image.open(stream)
            image = image.convert("L")
            image = image.crop((80, 0, 560, 480))
            image = image.resize((384, 384))
            image = image.rotate(180)

            # This is for printing ascii art.
            # Not really enough resolution though...
            #screen = aalib.AsciiScreen(width=30, height=15)
            #screen.put_image((0, 0), image)
            #printer.println(screen.render())
            #printer.feed(6)

            printer.printImage(image, False)

            printer.feed(4)
            printer.upsideDownOn()
            printer.println("#museomixmtl")
            printer.feed(1)

            stream = io.BytesIO()

            # Reset the LED to HIGH
            GPIO.output(18, GPIO.HIGH)

            # Close the camera
            camera.close()

        time.sleep(0.016)

cameraMode()
