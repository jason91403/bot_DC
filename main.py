import os
import sys
import termios
import time
import pyte
from select import select
from transfer_keys import TransferKeys
from pathfinding import PathFinding


'''
Map:
x range 0~32
y range 0~16

whole screen
x max = 79
(16, 8): @

'''


def analyse_screen(sl):
    map_detail_dic = {}
    states_dic = {}

    for y in range(len(sl)):
        for x in range(len(sl[y])):
            if y < 17 and x < 34:
                #map_dic[(x, y)] = sl[y][x].encode('ascii')
                map_detail_dic = create_map_data((x, y), sl[y][x].encode('ascii'), map_detail_dic)
            elif x > 36:
                states_dic[(x, y)] = sl[y][x].encode('ascii')
    # map_detail_dic = catch_map(map_dic)
    # Only after finishing map data, it can be checked fogs
    map_detail_dic = check_fogs(map_detail_dic)
    player_states_dic = catch_states(states_dic)

    return map_detail_dic, player_states_dic


def create_map_data(position, value, map_dic):
    """
    Analyse map information here.
    :param map_dic:
    :param position: ex. (x, y)
    :param value: symbol, ex. #, ., ) etc.
    :return:the map data, dict type
    """
    can_pass_list = [".", "'", ")"]
    can_it_pass = False
    if value in can_pass_list:
        can_it_pass = True
    # map_dic[position] = [symbol, can pass?, fogs?]
    map_dic[position] = [value, can_it_pass, False]
    # fogs value will be checked later, this is a default value
    return map_dic


def check_fogs(map_dic):
    nb_position_list = [(1, 0), (1, 1), (1, -1),
                        (0, 1), (0, -1),
                        (-1, 0), (-1, 1), (-1, -1)]
    for position, data_list in map_dic.items():
        if data_list[0] == ".":
            for nb_p in nb_position_list:
                nb_position = (int(position[0]) + nb_p[0], int(position[1]) + nb_p[1])
                if 0 <= nb_position[0] <= 32 and 0 <= nb_position[1] <= 16:
                    nb_data_list = map_dic[nb_position]
                    # nb_data_list[0] = symbol
                    if nb_data_list[0] == " ":
                        data_list = map_dic[position]
                        data_list[2] = True
                        map_dic[position] = data_list
                        break
    return map_dic

# def catch_map(map_dic):
#     map_detail_dic = {}
#     """
#     map_detail_dic = [symbol, can pass?, ]
#     """
#     for key, value in map_dic.items():
#         map_detail_dic[key] = [value, can_pass(unicode(value))]
#     return map_detail_dic

#def check_fogs(position, map_dic):



# def can_pass(symbol):
#     symbol_can_pass = False
#     '''
#     can_pass_list need to be study more!!
#     ) is a club
#     '''
#     can_pass_list = [".", "'", ")"]
#     if symbol in can_pass_list:
#         symbol_can_pass = True
#     return symbol_can_pass


'''
    (x, y)
    Career: (37-78, 1)
    Health: (44-55, 2)
    Magic: (43-55, 3)
    AC: (40-55, 4)
    Str: (59-80, 4)
    EV: (40-55, 5)
    Int: (59-80, 5)
    SH: (40-55, 6)
    DEX: (59-80, 6)
    XL: (40-55, 7)
    Place: (61-80, 7)
    Glod: (42-55, 8)
    Time: (60-80, 8)
'''


def catch_states(sd):
    psd = {'Career': catch_keywords_by_range_x(sd, 37, 78, 1),
           'Health': catch_keywords_by_range_x(sd, 44, 55, 2),
           'Magic': catch_keywords_by_range_x(sd, 43, 55, 3),
           'AC': catch_keywords_by_range_x(sd, 40, 55, 4),
           'Str': catch_keywords_by_range_x(sd, 59, 80, 4),
           'EV': catch_keywords_by_range_x(sd, 40, 55, 5),
           'Int': catch_keywords_by_range_x(sd, 59, 80, 5),
           'SH': catch_keywords_by_range_x(sd, 40, 55, 6),
           'DEX': catch_keywords_by_range_x(sd, 59, 80, 6),
           'XL': catch_keywords_by_range_x(sd, 40, 55, 7),
           'Place': catch_keywords_by_range_x(sd, 61, 80, 7),
           'Glod': catch_keywords_by_range_x(sd, 42, 55, 8),
           'Time': catch_keywords_by_range_x(sd, 60, 80, 8)}
    return psd


def catch_keywords_by_range_x(dic, range_x1, range_x2, y):
    keyword = ""
    for x in range(range_x1, range_x2):
        keyword = keyword + dic[(x, y)]
    keyword = keyword.replace(' ', '')
    return keyword


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
    # stream = pyte.ByteStream()
    stream.attach(screen)

    # test area ##############################################################
    observed_mode = True
    observed_key = None
    button_path_finding = False
    button_path_go = False
    path_finding_list = []
    # test area ##############################################################

    # Tool classes ###########################################################
    transfer_key_tool = TransferKeys()
    # Tool classes ###########################################################

    while True:
        # Wait for input from the game or the keyboard
        (read, write, error) = select([file_descriptor, sys.stdin], [], [file_descriptor])

        # Check if the input was from the keyboard
        if sys.stdin in read:
            # If so, pass it to the game
            message = sys.stdin.read(1)

            # Enter presses need to be translated...
            message = transfer_key_tool.transfer(message)

            # test area ##############################################################
            if message == chr(111): # o key
                button_path_finding = not button_path_finding
            elif message == chr(112): # p key
                button_path_go = not button_path_go
            # test area ##############################################################
            else:
                # Send output to the game, and wait a little bit for it to catch up
                os.write(file_descriptor, message)
                time.sleep(0.05)

        # if press p, start move by path_finding_list
        if button_path_go:
            if path_finding_list:
                m = path_finding_list.pop(0)
                os.write(file_descriptor, m)
                time.sleep(0.05)
            else:
                button_path_go = not button_path_go

        # Check if the game sent any output
        if file_descriptor in read:
            message = os.read(file_descriptor, 1024)

            # Feed the games output into the terminal emulator
            for i in message:
                # The emulator only likes reading ascii characters
                if 0 < ord(i) < 128:
                    stream.feed(unicode(i))
                elif ord(i) == 226:
                    stream.feed(unicode("~"))
                '''
                ISSUE:
                Some output of game are not ascii. ex: BLACK CLUB SUIT (tree), 
                is a obstacle, byte(utf-8, dec): 226 153 163
                There are three items for one obstacle, so I just replace 226 with "~" temporarily.
                But it may occur more issues!!!
                '''

            if message == "":
                break

        screen_line = []
        # Print the current contents of the screen
        for line in screen.display:
            print line
            screen_line.append(line)

        map_dic = {}
        states = {}
        map_dic, player_states = analyse_screen(screen_line)

        # test area ##############################################################
        tmp_boolean = False
        tmp_fogs_list = []
        for position, data_list in map_dic.items():
            if data_list[2]:
                tmp_fogs_list.append(position)
                tmp_boolean = True
        print "Any fogs? " + str(tmp_boolean)
        if tmp_boolean:
            print tmp_fogs_list

        if button_path_finding :
            button_path_finding = not button_path_finding
            player_position = (16, 8)
            target_position = (21, 8)
            p = PathFinding()
            path_finding_list = p.path_finding(player_position, target_position, map_dic)
            # path_finding_list = path_finding(player_position, target_position, map_dic)
            # if path_finding_list:
            #     print "To target: " + str(target_position)
            #     print "Move: " + str(path_finding_list)

        # print "path_finding_list: " + str(path_finding_list)
        # test area ##############################################################



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
