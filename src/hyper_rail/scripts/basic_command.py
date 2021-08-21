"""Basic Command Interpeter for driving the ESP 32 over serial"""

import serial
from time import sleep

# Baud Rate to communicate to the ESP 32 over
BAUD_RATE = 115200

# Set to whatever device the ESP 32 controller is opperating on
DEVICE_PATH = "/dev/tty.usbmodem1811"

def initiateSerialConnection(s: serial.Serial):
    """Initate communication with ESP32"""

    # Send wake-up signal to the ESP 32
    print("Sending Wake-up packet to the controller...")
    s.write("\r\n\r\n")

    # Wait a few seconds for it to initialize
    sleep(3)
    print("Controller Initialized!")

    # Flush the serial input to prepare for the next set of data
    s.flushInput()

def goToXY(s: serial.Serial):
    x = input("Input the X Coordinate (mm): ")
    y = input("Input the Y Coordinate (mm): ")
    speed = input("Input the feed rate (mm/min): ")
    """Go to a specified X Y Coordinate"""   
    s.write(f"$J=X{x} Y{y} F{speed}\n")
    print("GRBL Response: " + s.readline().strip())

def sendGCode(s: serial.Serial):
    """Send a single line of GCode to the driver"""
    line = input("G-code to send: ").strip()
    s.write(line + "\n")
    print("GRBL Response: " + s.readline().strip())

def homeMachine(s: serial.Serial):
    """Home machine's axis"""
    s.write("$H\n")
    print("GRBL Response: " + s.readline().strip())

def feedGCodeFile(s: serial.Serial):
    """Feed a given G-code file into the controller"""
    file_path = input("Path to g-code: ")

    # Open the G code file
    with open(file_path) as f:

        # Loop through every line in the g-code file and send it to the controller
        for line in f:
            l = line.strip()
            print("Sending: " + l)
            s.write(l + "\n")
            print("GRBL Response: " + s.readline().strip())

def listCommands(s: serial.Serial):
    """List all available commands that can be used on the driver"""
    s.write("$cmd\n")
    print("Commands: ")
    for line in s.readlines():
        print(line)

def genericCommand(s: serial.Serial):
    """Send another command that is not listed in the options"""
    user_input = input("Input the command to send to the driver (settings must start with a $): ").strip()
    s.write(user_input)
    print("GRBL Response: ")
    for line in s.readlines():
        print(line)

def get_status_report(s: serial.Serial):
        """Request and read a status report from the GRBL driver"""
        """Format: <Idle,MPos:X,Y,Z,WPos:X,Y,Z>"""
        s.write("?\n")

        # Remove line endings from response
        return s.readline().strip()
    
def get_position(s: serial.Serial):
    """Gets the machines current position with configured offsets"""
    """Format: <Idle,MPos:X,Y,Z,WPos:X,Y,Z>"""

    state = get_status_report(s)
    # Pulls the X,Y,Z coordinates out of the work position, and converts the values to floats
    return list(map(float, state.split("WPos:")[1].replace(">", "").split(",")))

def get_machine_state(s: serial.Serial):
    """Gets the machines current running state"""
    """Format: <Idle,MPos:X,Y,Z,WPos:X,Y,Z>"""
    state = get_status_report(s)

    # Get the current running state of the machine and return it
    return state.split(",")[0].replace("<", "")

def continousJog(s: serial.Serial):
    """Cycle between 2 points with the second designated by an offset from the first. Loop indefinitely as a new command is issued whenever the machine is in an Idle state"""

    # Get the current machine position
    initalPosition = get_position(s)

    newX = initalPosition[0] + float(input("X Offset (mm): ").strip()) 
    newY = initalPosition[1] + float(input("Y Offset (mm): ").strip())
    speed = input("Feed rate (mm/min): ").strip()
    
    # Loop until the loop is interupted
    try:
        while True:

            # Issue a new G-code command whenever the machine enters an idle state
            if "Idle" in get_machine_state(s):
                s.write(f"G1 X{newX} Y{newY} F{speed}\nG1 X{initalPosition[0]} Y{initalPosition[1]} F{speed}\n")
            sleep(0.01)
    except KeyboardInterrupt:
        print("Halting due to ctrl+c.....")

def menu(s: serial.Serial):
    """Display a menu with options to control the driver board"""
    print("Welcome to a very basic driver interface for commanding an ESP 32 controller!\n")
    print("1) Go To X-Y")
    print("2) Feed G-Code file")
    print("3) Send G-Code")
    print("4) Home Machine")
    print("5) List All Commands")
    print("6) Send Other Commands")
    print("7) Continuous Jog (Drive between 2 points until stopped)")
    print("8) Print Current Machine Position\n")
    user_input = input("Current Selection: ").strip()

    # Convert the input into actual function mappings
    if user_input == "1":
        goToXY(s)
    elif user_input == "2":
        feedGCodeFile(s)
    elif user_input == "3":
        sendGCode(s)
    elif user_input == "4":
        homeMachine(s)
    elif user_input == "5":
        listCommands(s)
    elif user_input == "6":
        genericCommand(s)
    elif user_input == "7":
        continousJog(s)
    elif user_input == "8":
        pos = get_position(s)
        print(f"X: {pos[0]}, Y: {pos[1]}, Z: {pos[2]}\n")

if __name__ == "__main__":
    # Create the serial device to communicate over
    deviceSerial = serial.Serial(DEVICE_PATH, BAUD_RATE)

    initiateSerialConnection(deviceSerial)

    try:
        while True:
            menu(deviceSerial)
    except KeyboardInterrupt:
        # Inform the user that a KeyboardInterrupt has occurred and close the serial communication
        print("\nCtrl-C terminated the program")
        deviceSerial.close()
        pass
