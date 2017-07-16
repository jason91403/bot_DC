import os
import sys
from select import select
import termios
import time
import pyte

'''
Map:
x range 0~32
y range 0~16

(16, 8): @

'''


def analyse_screen(sl):
    md = {}

    for y in range(len(sl)):
        for x in range(len(sl[y])):

            if y < 17 and x < 17:
                md[(x, y)] = sl[y][x]
    return md


'''
After translation:
up    => i
down  => k
left  => j
right => l
i     => h

'''


def translate_key(msg):
    '''
    "Enter" = chr(10)
    "k" = move up = chr(107)
    "j" = move down = chr(106)
    "h" = move left = chr(104)
    "l" = move right = chr(108)
    '''

    if msg == chr(10):
        msg = chr(13)
    elif msg == chr(105):
        msg = chr(107)
    elif msg == chr(106):
        msg = chr(104)
    elif msg == chr(107):
        msg = chr(106)
    elif msg == chr(104):
        msg = chr(105)
    return msg


def main():
    # Fork into two processes
    # pid is the id of the process (zero for the original, non-zero for the other one)
    # file_descriptor is the communication channel between the two processes
    (pid, file_descriptor) = os.forkpty()

    # Process id 0 will run the game, the other process will be the bot
    if (pid == 0):
        os.environ["TERM"] = "linux"
        os.execl("/usr/bin/env", "/usr/bin/env", "crawl")

    # Set up a 80x24 terminal screen emulation
    screen = pyte.Screen(80, 24)
    stream = pyte.Stream()
    stream.attach(screen)

    observed_mode = True
    observed_key = None

    while (True):
        # Wait for input from the game or the keyboard
        (read, write, error) = select([file_descriptor, sys.stdin], [], [file_descriptor])

        # Check if the input was from the keyboard
        if (sys.stdin in read):
            # If so, pass it to the game
            message = sys.stdin.read(1)

            if observed_mode == True:
                observed_key = ord(message)

            # Enter presses need to be translated...
            message = translate_key(message)

            # Send output to the game, and wait a little bit for it to catch up
            os.write(file_descriptor, message)
            time.sleep(0.05)

        # Check if the game sent any output
        if (file_descriptor in read):
            message = os.read(file_descriptor, 1024)

            # Feed the games output into the terminal emulator
            for i in message:
                # The emulator only likes reading ascii characters
                if ord(i) < 128 and ord(i) > 0:
                    stream.feed(unicode(i))

            if (message == ""):
                break

        screen_line = []
        # Print the current contents of the screen
        for line in screen.display:
            print line
            screen_line.append(line)

        map_dic = {}
        map_dic = analyse_screen(screen_line)

        # to check the input Dec code
        if observed_mode == True:
            # print "You enter keyboard Dec: " + str(observed_key)
            print map_dic[(16, 8)]


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