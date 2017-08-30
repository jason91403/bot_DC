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


def check_move_keys(msg):
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

    return move


def send_input_to_game(fd, msg):
    os.write(fd, msg)
    time.sleep(0.05)


def test_record_map_to_file_2(file_name, map_dic):
    test_file = open(file_name, 'w')
    line_dic = {}  # [[y_position, line_detail_list],...]
    line_dic_p = {}
    x_min = 0
    map_dic = collections.OrderedDict(sorted(map_dic.items()))
    for position, data_list in map_dic.items():
        x_position = position[0]
        if x_position < x_min:
            x_min = x_position
        y_position = position[1]
        if y_position not in line_dic:
            line_dic[y_position] = [[x_position, data_list[0]]]
        else:
            line_dic[y_position].append([x_position, data_list[0]])
    # Sort by
    line_dic = collections.OrderedDict(sorted(line_dic.items()))

    for y_position, data_list in line_dic.items():
        data_list = sorted(data_list, key=lambda x: x[0])  # Sort by x_position
        # First x_position from a line
        # print "x_min: " + str(x_min)
        # print "data_list[0][0]: " + str(data_list[0][0])
        while data_list[0][0] > x_min:
            data_list.insert(0, [data_list[0][0] - 1, " "])
        data_list = sorted(data_list, key=lambda x: x[0])  # Sort by x_position
        for position_with_value_list in data_list:
            if y_position not in line_dic_p:
                line_dic_p[y_position] = position_with_value_list[1]
            else:
                line_dic_p[y_position] = line_dic_p[y_position] + position_with_value_list[1]

        line_dic_p = collections.OrderedDict(sorted(line_dic_p.items()))

    for line_num, line in line_dic_p.items():
        test_file.write(line + "\n")

    test_file.close()


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
    """
    Switch the checking key: Enter or z key
    :param switch_button:
    :return:
    """
    if switch_button:
        return chr(13)  # Enter key
    else:
        return chr(122)  # z key


def check_target_is_monster(player_states, target_text):
    """
    It should be more monsters will be showed on screen.
    Now only Monster1 for test.
    :param player_states: 
    :param target_text: 
    :return: 
    """
    is_monster = False
    monsters_dic = player_states['Monsters']
    for monster_line, monster_name_list in monsters_dic.items():
        if monster_name_list[0] == target_text:
            is_monster = True
            break
    return is_monster


def check_any_monster_come(player_states):
    any_monster = False
    monsters_dic = player_states['Monsters']
    for monster_line, monster_name_list in monsters_dic.items():
        if monster_name_list[0] != " ":
            any_monster = True
            break
    return any_monster


def update_player_move_history(map_record, player_move_history, move):
    """
    Check if the target can pass by certain move, and update player_move_history.
    :param map_record:
    :param player_move_history:
    :param move:
    :return: player_move_history will be updated. target_text is for checking if it's a monster.
    """
    player_position = get_player_position(player_move_history)
    target_position = (player_position[0] + move[0],
                       player_position[1] + move[1])
    can_pass = map_record[target_position][1]
    target_text = map_record[target_position][0]
    if can_pass:
        player_move_history = (player_move_history[0] + move[0],
                               player_move_history[1] + move[1])
        # print "player_move_history update: " + str(player_move_history)
    # else:
        # print "target: " + str(target_position) + "can not pass..."
    return can_pass, target_text, player_move_history


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

    # test area ##############################################################
    button_path_finding = False
    button_path_go = False
    player_move_history = (0, 0)
    # test area ##############################################################

    # Main objects ###########################################################
    map_dic = {}  # Current map screen
    map_record_backup = {}
    map_record = {}  # Record map
    player_states = {}
    game_input_dic = {}
    path_finding_list = []
    transfer_key_tool = TransferKeys()
    screen_catch = ScreenCatch()
    path_finding_tool = PathFinding()

    # Screen update objects ##################################################
    screen_udate_counter = 0  # for test
    need_to_update_screen = False
    screen_update_switch_button = True
    screen_update_first = True

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
                move = check_move_keys(message)
                can_pass = True
                # move != (0, 0) means control is move. Then, record some data.
                if move != (0, 0):
                    # If any move key has been pressed, then screen need to be updated.
                    need_to_update_screen = True
                    can_pass, target_text, player_move_history = update_player_move_history(
                                                                                map_record,
                                                                                player_move_history,
                                                                                move)
                    """
                        Check if target_text is a monster, move still works but player_move_history 
                        do not update.
                    """
                    if check_target_is_monster(player_states, target_text):
                        can_pass = True

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
                    map_record_backup = map_record

                """
                    Send any key except move keys. If input is a move key, than check the 
                    target can pass. If not, than don't send any input.
                """
                if can_pass:
                    send_input_to_game(file_descriptor, message)
                    time.sleep(0.05)

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

        # test_record_map_to_file("map_now.txt", map_dic)
        test_record_map_to_file_2("map_now.txt", map_dic)

        # Screen update start #####################################################
        if game_input_dic:
            update_flag = False
            game_input_line_6 = game_input_dic['Ginput6']
            # print "screen_update_switch_button : " + str(screen_update_switch_button)
            if screen_update_switch_button and game_input_line_6 == "_Unknowncommand.":
                # Enter key
                update_flag = True
                screen_update_switch_button = False
            elif not screen_update_switch_button and game_input_line_6 == "_Youdon'tknowanyspells.":
                # z key
                update_flag = True
                screen_update_switch_button = True
                # print "_Youdon'tknowanyspells. update"
            elif screen_update_first and game_input_line_6 == "_Press?foralistofcommandsandotherinformation.":
                # First time in the game
                # print "_Press?foralistofcommandsandotherinformation. update"
                screen_update_first = False
                update_flag = True
            if update_flag:
                screen_udate_counter += 1
                # Merge map_record_backup(record it before move) and map_dic(current map)
                map_record = dict(map_record_backup.items() + map_dic.items())
                need_to_update_screen = False
        # Screen update end #####################################################

        # test_record_map_to_file("map_record_after.txt", map_record)
        test_record_map_to_file_2("map_record_after.txt", map_record)

        # Output area end ###################################################################################

        # Other control area start ##########################################################################

        # For Test ###################################################################
        # if button_path_finding:
        #     button_path_finding = not button_path_finding
        #     p = PathFinding()
        #     player_position = get_player_position(player_move_history)
        #     print "Player position: " + str(player_position)
        #     path_finding_list = p.path_finding(player_position, (25, 8), map_record)
        #     if path_finding_list:
        #         print "Moves: " + str(path_finding_list)
        #     else:
        #         print "This target can't pass."

        # Check any fogs
        map_record, fogs_dic = check_fogs(map_record)

        fogs_list = fogs_dic.keys()
        if button_path_finding:
            button_path_finding = not button_path_finding
            if fogs_list:
                a_fog_can_pass = False
                player_position = get_player_position(player_move_history)
                for fog_position in fogs_list:
                    print "Target position: " + str(fog_position)
                    path_finding_list = path_finding_tool.path_finding(player_position, fog_position, map_record)
                    if path_finding_list:
                        print "Moves: " + str(path_finding_list)
                        a_fog_can_pass = True
                        break
                    else:
                        print "This target can't pass."
                if not a_fog_can_pass:
                    print "No fog can pass."

        """
            If any move has been pressed, then press Enter or z key. After that, game will output
            some messages which we can catch to know the screen has been completely updated.
            Enter: _Unknowncommand.
            z key: _Youdon'tknowanyspells.            
            Can been changed those keys.
        """
        if need_to_update_screen:
            os.write(file_descriptor, get_update_screen_key(screen_update_switch_button))
            time.sleep(0.05)

        # if press p, start move by path_finding_list
        if button_path_go:

            # If any monster come, stop moving and try to attack the monster.
            if check_any_monster_come(player_states):
                button_path_go = False
                path_finding_list = path_finding_list[:] = []
            else:
                if not need_to_update_screen:
                    if path_finding_list:
                        message = path_finding_list.pop(0)
                        move = check_move_keys(message)
                        can_pass = True
                        if move != (0, 0):
                            # If any move key has been pressed, then screen need to be updated.
                            need_to_update_screen = True
                            can_pass, target_text, player_move_history = update_player_move_history(
                                                                                            map_record,
                                                                                            player_move_history,
                                                                                            move)
                            if check_target_is_monster(player_states, target_text):
                                can_pass = True
                            map_record_backup = map_record
                        if can_pass:
                            send_input_to_game(file_descriptor, message)
                            time.sleep(0.05)
                        else:
                            print "Something wrong. Stop moving and clear path_finding_list"
                            button_path_go = False
                            path_finding_list[:] = []

                        time.sleep(0.05)
                    else:
                        # Finish all moves
                        button_path_go = False

        # Some msgs area
        print "Screen update times: " + str(screen_udate_counter)
        print "player_move_history: " + str(player_move_history)
        print "player_position" + str(get_player_position(player_move_history))
        # if player_states is not None:
        #     print "Monsters: " + str(player_states['Monsters'])

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
