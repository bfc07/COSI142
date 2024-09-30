import network
import socket
import binascii
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
from machine import Pin, PWM

ssid = 'buddyfanclub'
password = '123456789'

def connect():
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print(wlan.status())
    
    while wlan.isconnected() == False:
        print('Waiting for connection...', wlan.status())
        sleep(3)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage(temperature, state, brightness):
    # Template HTML with form to set brightness
    html = f"""
            <!DOCTYPE html>
            <html>
            <form action="./lighton">
            <input type="submit" value="Light on" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />
            </form>
            <p>LED is {state}</p>
            <p>Temperature is {temperature}</p>
            <form action="/setbrightness" method="GET">
                <label for="brightness">Set Brightness (0-65535):</label><br>
                <input type="number" id="brightness" name="brightness" min="0" max="65535" value="{brightness}">
                <input type="submit" value="Set Brightness">
            </form>
            </body>
            </html>
            """
    return str(html)

def serve(connection):
    # Start a web server
    state = 'OFF'
    pico_led.off()
    temperature = 0
    LED = machine.Pin(16, machine.Pin.OUT)
    pwm16 = PWM(Pin(16))
    pwm16.freq(2000)
    brightness = 32768  # Default brightness (50%)
    pwm16.duty_u16(brightness)

    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        print(request)
        
        try:
            request_path = request.split()[1]
        except IndexError:
            continue

        if request_path == '/lighton?':
            state = 'ON'
            pico_led.on()
            LED.value(1)
        elif request_path == '/lightoff?':
            pico_led.off()
            state = 'OFF'
            LED.value(0)
        elif '/setbrightness' in request_path:
            # Extract brightness value from the URL query string
            try:
                brightness_value = request_path.split('brightness=')[1]
                brightness = int(brightness_value.split('&')[0])
                if 0 <= brightness <= 65535:
                    pwm16.duty_u16(brightness)  # Update PWM duty cycle
            except (IndexError, ValueError):
                pass  # Handle invalid brightness values gracefully

        temperature = pico_temp_sensor.temp
        html = webpage(temperature, state, brightness)
        client.send(html)
        client.close()

try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
