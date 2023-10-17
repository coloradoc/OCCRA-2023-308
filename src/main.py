
# Documentation/Vex Code link: https://www.robotmesh.com/studio/content/docs/vexv5-python/html/annotated.html

# ---------------------------------------------------------------------------- #
# 	Module:       main.py                                                      #
# 	Author:       Noah Nicolas Gabe Jerry Sofie                                #
# 	Created:      9/13/2023, 1:06:06 PM                                        #
# 	Description:  V5 project                                                   #                                                         
# ---------------------------------------------------------------------------- #


# Library imports----
from vex import *
import math


# Top of Vexcode Configures Devices KEY------------
# frontLeftMotor      motor29       A
# frontRightMotor     motor29       B
# backLeftMotor       motor29       D
# backRightMotor      motor29       E
# Bottom of Vexcode Configures Devices KEY---------


# CONFIGURE DEVICES-------------------------------------------
# Brain should be defined by default
brain=Brain()

frontLeftMotor = Motor29(brain.three_wire_port.a, False)
frontRightMotor = Motor29(brain.three_wire_port.b, True)
backLeftMotor = Motor29(brain.three_wire_port.d, False)
backRightMotor = Motor29(brain.three_wire_port.c, True)

triport = Triport(Ports.PORT1)
flywheelMotor1 = Motor29(triport.d, True)
flywheelMotor2 = Motor29(triport.f, False)
inakeMotor = Motor29(triport.a, False)
conveyorMotor = Motor29(triport.c, False)

controller_1 = Controller(PRIMARY)
controller_2 = Controller(PARTNER)

# Constants
FORWARD_SPEED_MULTIPLIER = 1
STRAFE_SPEED_MULTIPLIER = 1
ROTATION_SPEED_MULTIPLIER = 0.5
CRABCRAWLALIGN = 2
global offset
offset = 1
direction = FORWARD #maybe set to global?
#================================================================= wait for stuff to configure =================================================================#
wait(25, MSEC)
#================================================================= wait for stuff to configure =================================================================#


# Main programming loop---------------------------------------------------------------------------
def main():
    #flywheelMotor2.spin(direction, 30)
    #conveyorMotor.spin(direction, 30)
    global offset
    # left joystick y axis (3)
    y = controller_1.axis3.position() * FORWARD_SPEED_MULTIPLIER
    # left joystick x axis (4)
    x = controller_1.axis4.position() * STRAFE_SPEED_MULTIPLIER
    # right joystick x axis (1)
    turn = controller_1.axis1.position() * ROTATION_SPEED_MULTIPLIER
    
    # deadband for joystick drift
    if abs(x) < 2:
       x = 0
    if abs(y) < 2:
       y = 0
    if abs(turn) < 2:
       turn = 0
    
    # Convert cartesian values (x and y) into polar values (angle and magnitude)
    theta = math.atan2(y, x) 
    power = math.sqrt(float(x**2) + float(y**2))

    direction = reverse()
    intake(direction)
    conveyor(direction)
    shoot(direction)

    # move drive wheels
    if(controller_1.buttonLeft.pressing()):
        drive(50, 0, math.radians(-90), x)
    elif(controller_1.buttonRight.pressing()):
        drive(50, 0, math.radians(90), x)
    elif(controller_1.buttonDown.pressing()):
        drive(50, 0, math.radians(-180), x)
    elif(controller_1.buttonUp.pressing()):
        drive(50, 0, math.radians(0), x)
    else:
        drive(power, turn, theta, x)

# Controls Robot drive-------------------------------------------------------------------------------------------
# Forward & Turn control speed of chassiss wheels
# Values Span -100 to 100. 
def drive(power: float, turn: float, theta: float, strafeAxis: float):
    sin = math.sin(theta - math.pi/4)
    cos = math.cos(theta - math.pi/4)
    maxValue = max(abs(sin), abs(cos))
    
    leftFront = (power * cos/maxValue + turn) * offset
    rightFront = (power * sin/maxValue - turn) * offset
    leftRear = power * sin/maxValue + turn
    rightRear = power * cos/maxValue - turn

    # drive left side
    #if strafeAxis > 0 or strafeAxis < 0:
     #   rightFront = rightFront * CRABCRAWLALIGN
      #  leftFront = leftFront * CRABCRAWLALIGN

    # if one motor needs to move faster than the max, all of the motor speeds are reduced
    if ((power + abs(turn)) > 100):
        leftFront /= power + abs(turn) 
        rightFront /= power + abs(turn) 
        leftRear /= power + abs(turn)
        rightRear /= power + abs(turn) 
        leftFront *= 100
        rightFront *= 100
        leftRear *= 100
        rightRear *= 100

    

    frontLeftMotor.spin(FORWARD, leftFront)
    backLeftMotor.spin(FORWARD, leftRear)

    # drive right side
    frontRightMotor.spin(FORWARD, rightFront)
    backRightMotor.spin(FORWARD, rightRear)


    # Print motor vaules out for debugging

    #brain.screen.print("LR: ", leftRear)
    # brain.screen.new_line()
    # brain.screen.print("RF: ", rightFront)
    # brain.screen.new_line()
    # brain.screen.print("RR: ", rightRear)
    # brain.screen.new_line()
    # brain.screen.print("Theta ", theta*57.29)
    # brain.screen.new_line()
    # brain.screen.print("Power ", power)
    # brain.screen.new_line()
    # brain.screen.print("Turn ", turn)

#Shooting & Intake Mechanism----------------------------------------------------
def intake(direction): 
    if controller_1.buttonL1.pressing():     
        inakeMotor.spin(direction, 30)
    else:
        inakeMotor.stop()

# Conveyor Mechanism----------------------------------------------------
def conveyor(direction):
    if controller_1.buttonR1.pressing():     
        conveyorMotor.spin(direction, 60)
        controller_1.screen.clear_screen()
        controller_1.screen.set_cursor(1,1)
        controller_1.screen.print("print test ", direction)
    else:
        controller_1.screen.clear_screen()
        controller_1.screen.set_cursor(1,1)
        controller_1.screen.print("not run ", direction)
        conveyorMotor.stop()

is_flywheel_on = False
# Shooting Mechanism----------------------------------------------------
def shoot(direction):
    global is_flywheel_on

    if controller_1.buttonR2.pressing():
        # Toggle the state when the button is pressed
        is_flywheel_on = not is_flywheel_on

    if is_flywheel_on:
        # If the motor state is on, spin the motors
        flywheelMotor1.spin(direction, 70)
        flywheelMotor2.spin(direction, 70)
    else:
        # If the motor state is off, stop the motors
        flywheelMotor1.stop()
        flywheelMotor2.stop()

#reverses all motors that are controlled by the object 'direction'
#for intake and shooter
def reverse():
    if controller_1.buttonX.pressing():     
        direction = REVERSE
    else:
        direction = FORWARD
    return direction
    
     


    
def directMovement():
    if controller_1.buttonUp.pressing():     
        frontLeftMotor.spin(FORWARD, 50)
        backLeftMotor.spin(FORWARD, 50)

# ---- START EXECUTING CODE ---- 
while 1:
    main()
    wait(1, MSEC)


