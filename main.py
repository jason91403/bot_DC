import os
import sys
import termios
import time
import pyte
from select import select
from transfer_keys import TransferKeys
from pathfinding import PathFinding
from screen_catcher import ScreenCatch
import collections
import random


def output_control(fd, msg):
    move = (0, 0)
    if msg == chr(27) + chr(91) + chr(67):  # Right
        # position = (position[0] + 1, position[1])
        move = (1, 0)
    elif msg == chr(27) + chr(91) + chr(65):  # UP
        # position = (position[0], position[1] + 1)
        move = (0, -1)
    elif msg == chr(27) + chr(91) + chr(68):  # Left
        # position = (position[0] - 1, position[1])
        move = (-1, 0)
    elif msg == chr(27) + chr(91) + chr(66):  # Down
        # position = (position[0], position[1] - 1)
        move = (0, 1)
    elif msg == chr(117):  # Right Up
        # position = (position[0] + 1, position[1] + 1)
        move = (1, -1)
    elif msg == chr(110):  # Right Down
        # position = (position[0] + 1, position[1] - 1)
        move = (1, 1)
    elif msg == chr(121):  # Left Up
        # position = (position[0] - 1, position[1] + 1)
        move = (-1, -1)
    elif msg == chr(98):  # Left Down
        # position = (position[0] - 1, position[1] - 1)
        move = (-1, 1)

    os.write(fd, msg)
    time.sleep(0.05)

    return move


def test_record_map_to_file(file_name, map_dic):
    test_file = open(file_name, 'w')
    line_dic = {}
    line_dic_with_position = {}
    map_dic = collections.OrderedDict(sorted(map_dic.items()))
    for position, data_list in map_dic.items():
        y = position[1]
        if y not in line_dic:
            line_dic[y] = data_list[0]
            line_dic_with_position[y] = str(position) + ", " + data_list[0]
        else:
            line_dic[y] = line_dic[y] + data_list[0]
            line_dic_with_position[y] = line_dic_with_position[y] + " " + str(position) + ", " + data_list[0]

    line_dic = collections.OrderedDict(sorted(line_dic.items()))
    line_dic_with_position = collections.OrderedDict(sorted(line_dic_with_position.items()))

    for line_num, line in line_dic.items():
        test_file.write(line + "\n")

    test_file.write("\n\n")

    for line_num, line in line_dic_with_position.items():
        test_file.write(line + "\n")

    test_file.close()


def check_screen_mode_in_standard(map_dic, states_dic):
    if not map_dic or states_dic is None:
        return False
    else:
        return True


def check_fogs(map_dic):
    nb_position_list = [(1, 0), (1, 1), (1, -1),
                        (0, 1), (0, -1),
                        (-1, 0), (-1, 1), (-1, -1)]
    fogs_dic = {}
    for position, data_list in map_dic.items():
        if data_list[0] == ".":
            for nb_p in nb_position_list:
                nb_position = (int(position[0]) + nb_p[0], int(position[1]) + nb_p[1])
                is_fog = False
                try:
                    nb_data_list = map_dic[nb_position]
                    if nb_data_list[0] == " ":
                        is_fog = True
                except KeyError:
                    # If the nb_position(Key) is not in map_dic, it is a edge.
                    is_fog = True

                if is_fog:
                    data_list = map_dic[position]
                    data_list[2] = True
                    map_dic[position] = data_list
                    fogs_dic[position] = data_list
                    break
    return map_dic, fogs_dic


def get_player_position(move_history):
    position = (16 + move_history[0], 8 + move_history[1])
    return position

def get_update_screen_key(switch_button):
    if switch_button:
        return chr(13)  # Enter key
    else:
        return chr(122)  # z key


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
    button_path_finding = False
    button_path_go = False
    path_finding_list = []
    player_move_history = (0, 0)
    # test area ##############################################################

    # Tool classes ###########################################################
    map_dic = {}  # Current map screen
    map_record_backup = {}
    map_record = {}  # Record map
    player_states = {}
    game_input_dic = {}
    transfer_key_tool = TransferKeys()
    screen_catch = ScreenCatch()
    time_before_move = None
    move_prepare = (0, 0)
    tmp_counter = 0
    need_to_update_screen = False
    screen_update_switch_button = True
    screen_update_first = True
    # Tool classes ###########################################################

    while True:
        # Wait for input from the game or the keyboard
        (read, write, error) = select([file_descriptor, sys.stdin], [], [file_descriptor])

    # Input area start #################################################################################

        # Check if the input was from the keyboard
        if sys.stdin in read:

            # If so, pass it to the game
            message = sys.stdin.read(1)

            # Enter presses need to be translated...
            message = transfer_key_tool.transfer(message)

            # test area ##############################################################
            if message == chr(111):  # o key
                button_path_finding = not button_path_finding
            elif message == chr(112):  # p key
                button_path_go = not button_path_go
            # test area ##############################################################
            else:
                # Send output to the game, and wait a little bit for it to catch up
                # os.write(file_descriptor, message)
                """
                    Record current map before any control.
                    Because it can not sure how many times the input will come,
                    map_dic will keep update and I'm not sure while it is the final time.
                    So if map_dic has not updated to the final than record to map_record,
                    map_record will be wrong.
                    Therefore, backup map_record and map_dic when player move. Then keep
                    updating map_record_backup + map_previous + map_dic. map_record_backup
                    and map_previous would be changed when screen update. map_record will be
                    update until map_dic stop updating.
                """

                if player_states is not None:
                    time_before_move = player_states['Time']
                # move_prepare = (0, 0)
                # player_move_history = output_control(file_descriptor, message, player_move_history)
                move_prepare = output_control(file_descriptor, message)
                # move_prepare != (0, 0) means control is move. Then, record some data.
                if move_prepare != (0, 0) and player_states is not None:

                    need_to_update_screen = True

                    player_position = get_player_position(player_move_history)
                    move_target_position = (player_position[0] + move_prepare[0],
                                            player_position[1] + move_prepare[1])
                    if map_record[move_target_position][1]:
                        player_move_history = (player_move_history[0] + move_prepare[0],
                                               player_move_history[1] + move_prepare[1])
                        print "player_move_history update: " + str(player_move_history)
                    else:
                        print "target: " + str(move_target_position) + "can not pass..."


                    # player_move_history_backup = player_move_history
                    # player_move_history_back_list.append(player_move_history_backup)
                    map_record_backup = map_record

                time.sleep(0.05)

                # is_move, ph = output_control(file_descriptor, message, player_move_history)
                # if is_move:
                #     if check_screen_mode_in_standard(map_dic, player_states):
                #         player_move_history = ph
                #         """
                #             IMPORTANT!!!!!!
                #             Remember to change the time to backup map_dic and map_record!!
                #
                #         """
                #         # time_previous =
                #         map_record_backup = map_record
                #
                # time.sleep(0.05)

        # Input area end ####################################################################################

        # Output area start #################################################################################

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

        map_dic, player_states, game_input_dic = screen_catch.analyse_screen(screen_line, player_move_history)

        test_record_map_to_file("map_now.txt", map_dic)

        """
            Merge map_record_backup(record it before move) and map_dic(current map)
        """
        # if check_screen_mode_in_standard(map_dic, player_states):
        #     if time_before_move != player_states['Time']:
        #         map_record = dict(map_record_backup.items() + map_dic.items())

        if game_input_dic:
            need_to_update = False
            game_input_line_6 = game_input_dic['Ginput6']
            # print "screen_update_switch_button : " + str(screen_update_switch_button)
            if screen_update_switch_button and game_input_line_6 == "_Unknowncommand.":
                # Enter key
                need_to_update = True
                screen_update_switch_button = False
            elif not screen_update_switch_button and game_input_line_6 == "_Youdon'tknowanyspells.":
                # z key
                need_to_update = True
                screen_update_switch_button = True
                # print "_Youdon'tknowanyspells. update"
            elif screen_update_first and game_input_line_6 == "_Press?foralistofcommandsandotherinformation.":
                # First time in the game
                # print "_Press?foralistofcommandsandotherinformation. update"
                screen_update_first = False
                need_to_update = True
            if need_to_update:
                tmp_counter += 1
                map_record = dict(map_record_backup.items() + map_dic.items())
                need_to_update_screen = False

        map_record, fogs_dic = check_fogs(map_record)

        test_record_map_to_file("map_record_after.txt", map_record)

        print "screen update times: " + str(tmp_counter)
        # Output area end ###################################################################################

        # Other control area start ##########################################################################

        if button_path_finding:
            button_path_finding = not button_path_finding
            p = PathFinding()
            player_position = get_player_position(player_move_history)
            print "Player position: " + str(player_position)
            path_finding_list = p.path_finding(player_position, (25, 8), map_record)
            if path_finding_list:
                print "Moves: " + str(path_finding_list)
            else:
                print "This target can't pass."

        # fogs_list = fogs_dic.keys()
        # print "\nFinal player position: " + str(get_player_position(player_move_history))
        # if button_path_finding:
        #     button_path_finding = not button_path_finding
        #     if fogs_list:
        #         p = PathFinding()
        #         a_fog_can_pass = False
        #         player_position = get_player_position(player_move_history)
        #         print "Player position: " + str(player_position)
        #         for fog_position in fogs_list:
        #             print "Target position: " + str(fog_position)
        #             path_finding_list = p.path_finding(player_position, fog_position, map_record)
        #             if path_finding_list:
        #                 print "Moves: " + str(path_finding_list)
        #                 a_fog_can_pass = True
        #                 break
        #             else:
        #                 print "This target can't pass."
        #         if not a_fog_can_pass:
        #             print "No fog can pass."

        if need_to_update_screen:

            # screen_update_switch_button = not screen_update_switch_button
            os.write(file_descriptor, get_update_screen_key(screen_update_switch_button))
            time.sleep(0.05)

        # if press p, start move by path_finding_list
        if button_path_go:
            if not need_to_update_screen:
                if path_finding_list:
                    need_to_update_screen = True
                    m = path_finding_list.pop(0)
                    move_prepare = output_control(file_descriptor, m)
                    time_before_move = player_states['Time']
                    map_record_backup = map_record
                    player_move_history = (player_move_history[0] + move_prepare[0],
                                           player_move_history[1] + move_prepare[1])
                    """
                        Temporarily, do not check whether the move is available. If path_finding_list
                        is created A*, all moves should be available. Therefore, update player_move_history
                        immediately. 
                    """
                    # if move_prepare != (0, 0) and player_states is not None:
                    #     print "player_move_history: " + str(player_move_history)
                    #     player_position = get_player_position(player_move_history)
                    #     print "player_position: " + str(player_position)
                    #     print "move_prepare: " + str(move_prepare)
                    #     move_target_position = (player_position[0] + move_prepare[0],
                    #                             player_position[1] + move_prepare[1])
                    #     print "move_target_position: " + str(move_target_position)
                    #     if map_record[move_target_position][1]:
                    #         print "move_target_position can pass!!"
                    #         player_move_history = (player_move_history[0] + move_prepare[0],
                    #                                player_move_history[1] + move_prepare[1])
                    #         print "player_move_history update: " + str(player_move_history)
                    #     else:
                    #         print "target: " + str(move_target_position) + "can not pass..."

                    time.sleep(0.05)
                else:
                    button_path_go = not button_path_go

        # Other control area end ##########################################################################


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
