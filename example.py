import os
import sys
from select import select
import termios
import time
import pyte

def main():
    # Fork into two processes
    # pid is the id of the process (zero for the original, non-zero for the other one)
    # file_descriptor is the communication channel between the two processes
    (pid, file_descriptor) = os.forkpty() 


    # Process id 0 will run the game, the other process will be the bot
    if(pid == 0):
            os.environ["TERM"] = "linux"
            os.execl("/usr/bin/env", "/usr/bin/env", "crawl")


    # Set up a 80x24 terminal screen emulation
    screen = pyte.Screen(80, 24)
    stream = pyte.Stream()
    stream.attach(screen)

    
    observed_mode = True
    observed_key = None
    
    while(True):
        # Wait for input from the game or the keyboard
        (read, write, error) = select([file_descriptor, sys.stdin], [], [file_descriptor])

        # Check if the input was from the keyboard
        if(sys.stdin in read):
            # If so, pass it to the game
            message = sys.stdin.read(1)
            
            if observed_mode == True:
                observed_key = ord(message)
            
            
            # Enter presses need to be translated...
            if message == chr(10):
                message = chr(13)
            

            # Send output to the game, and wait a little bit for it to catch up
            os.write(file_descriptor, message)
            time.sleep(0.05)
        
                 
        
        # Check if the game sent any output
        if(file_descriptor in read):
            message = os.read(file_descriptor, 1024)

            # Feed the games output into the terminal emulator
            for i in message:
                # The emulator only likes reading ascii characters
                if ord(i) < 128 and ord(i) > 0:
                    stream.feed(unicode(i))

            if(message == ""):
                break

        # Print the current contents of the screen
        for line in screen.display:
            print line
            
        # to check the input Dec code
        if observed_mode == True:
            print "You enter keyboard Dec: " + str(observed_key)        


# Setup the output terminal (disable canonical mode and echo)
original = termios.tcgetattr(sys.stdin)
settings = termios.tcgetattr(sys.stdin)
settings[3] = settings[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(sys.stdin, termios.TCSANOW, settings)

try:
    main()
finally:
    # Reset terminal settings back to how they were before
    termios.tcsetattr(sys.stdin, termios.TCSANOW, original)