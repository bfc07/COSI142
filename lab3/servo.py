from machine import ADC,Pin
from time import sleep
from servo import SERVO

ROTARY_ANGLE_SENSOR = ADC(0)
servo = SERVO(Pin(16))



def set_servo_angle(angle):
    # Convert angle (0 to 180) to duty cycle (40 to 115 for typical servos)
    duty = int((angle / 180 * 75) + 40)
    servo.turn(duty)

try:
    while True:
        # Read the potentiometer value (0 to 65535)
        value = ROTARY_ANGLE_SENSOR.read_u16()
        # Map pot_value (0 to 65535) to angle (0 to 180)
        angle = int(value / 65535 * 180)
        set_servo_angle(angle)
        

except KeyboardInterrupt:
    # Clean up on exit
    servo.duty(0)  # Stop the servo
    servo.deinit()
    print("Program stopped")