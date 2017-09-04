#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import termios
import time
import pyte
from select import select
from transfer_keys import TransferKeys
from pathfinding import PathFinding
from screen_catcher import ScreenCatch
from tools import Tools
from game_dictionary import GameDictionary


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


def check_screen_mode_in_standard(map_dic, states_dic):
    if not map_dic or states_dic is None:
        return False
    else:
        return True


def check_fogs(map_dic, game_dict):
    nb_position_list = [(1, 0), (1, 1), (1, -1),
                        (0, 1), (0, -1),
                        (-1, 0), (-1, 1), (-1, -1)]
    # fogs_dic = {}
    fogs_list = []
    for position, data_list in map_dic.items():
        # if data_list[0] == ".":
        if data_list[0] in game_dict.get_can_pass_text_list():
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
                    # fogs_dic[position] = data_list
                    if position not in fogs_list:
                        fogs_list.append(position)
                    break
    return map_dic, fogs_list


def get_fogs_list_with_distance(player_position, fogs_list, tools):
    fogs_with_distance = []
    for fog in fogs_list:
        dis = tools.get_distance(player_position, fog)
        fogs_with_distance.append([dis, fog])

    fogs_with_distance = sorted(fogs_with_distance, key=lambda x: x[0]) # sort by distance
    return fogs_with_distance


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


def check_any_monster_come_and_update_map(map_record, player_states):
    """
    This function will update map_record with monster information.
    :param map_record:
    :param player_states:
    :return:
    """
    any_monster = False
    monsters_dic = player_states['Monsters']
    for monster_line, monster_name_list in monsters_dic.items():
        a_monster_text = monster_name_list[0]
        if a_monster_text != " ":
            any_monster = True
            # To update map_record with monster information.
            for position, data_list in map_record.items():
                if a_monster_text == data_list[0]:
                    data_list[3] = True
    return any_monster


def check_is_door(map_record, player_move_history, move):
    is_door = False
    player_position = get_player_position(player_move_history)
    target_position = (player_position[0] + move[0],
                       player_position[1] + move[1])
    if map_record[target_position][0] == '+':
        is_door = True
    return is_door


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


def get_monster_position(map_record, monster_text):
    """
    If can not find monster, return None
    :param map_record:
    :param monster_text:
    :return:
    """
    monster_position = None
    for position, data_list in map_record.items():
        if data_list[0] == monster_text and monster_text != " ":
            monster_position = position
    return monster_position


def check_if_player_dead(game_input_dic):
    is_dead = False
    for input_line, input_content in game_input_dic.items():
        if input_content == "Youdie...":
            is_dead = True
    return is_dead


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
    button_bot_start = False
    test_text = None
    # test area ##############################################################

    # Main objects ###########################################################
    map_dic = {}  # Current map screen
    map_record_backup = {}
    map_record = {}  # Record map
    player_states = {}
    game_input_dic = {}
    path_finding_list = []
    player_move_history = (0, 0)
    transfer_key_tool = TransferKeys()
    screen_catch = ScreenCatch()
    path_finding_tool = PathFinding()
    tools = Tools()
    game_dictionary = GameDictionary()
    monster_position = None

    # Screen update objects ##################################################
    screen_update_counter = 0  # for test
    need_to_update_screen = False
    screen_update_switch_button = True
    screen_update_first = True

    # States machine objects #################################################
    """
        0: Exploration, 1: Fighting, 2: Decision, 3: Dead
        Default: 0
    """
    player_state_mode = 0

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
            elif message == chr(47):  # / key
                button_bot_start = True
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

                    if check_is_door(map_record, player_move_history,move):
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

            message = ""
            try:
                # message = os.read(file_descriptor, 1024)
                """
                    To solve ascii problem, .decode("utf-8") and directly stream.feed(unicode(i))
                """
                message = os.read(file_descriptor, 1024).decode("utf-8")

                # Feed the games output into the terminal emulator
                for i in message:
                    stream.feed(unicode(i))

                    # The emulator only likes reading ascii characters
                    # if 0 < ord(i) < 128:
                    #     stream.feed(unicode(i))
                    # elif ord(i) == 226:
                    #     stream.feed(unicode("~"))
                    # elif ord(i) == 195:
                    #     stream.feed(unicode("~"))
            except UnicodeDecodeError, e:
                """
                    Sometime it will happen, not sure the reason.
                """
                # print "UnicodeDecodeError"
                # print e
                pass

            '''
                            ISSUE:
                            Some output of game are not ascii. ex: BLACK CLUB SUIT (tree), 
                            is a obstacle, byte(utf-8, dec): 226 153 163
                            There are three items for one obstacle, so I just replace 226 with "~" temporarily.
                            But it may occur more issues!!!

                            https://unicode-table.com/en/00F7/
                            226 153 163: BLACK CLUB SUIT
                            195 183: Division Sign
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
        # test_record_map_to_file_2("map_now.txt", map_dic)
        tools.record_map_to_local_file("map_now.txt", map_dic)

        if game_input_dic:
            if check_if_player_dead(game_input_dic):
                player_state_mode = 3

        # Screen update start #####################################################
        if game_input_dic and player_state_mode != 3:
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
                screen_update_counter += 1
                # Merge map_record_backup(record it before move) and map_dic(current map)
                map_record = dict(map_record_backup.items() + map_dic.items())
                need_to_update_screen = False

            # print "game_input_line_6: " + str(game_input_line_6)
        # Screen update end #####################################################

        # test_record_map_to_file("map_record_after.txt", map_record)
        # test_record_map_to_file_2("map_record_after.txt", map_record)
        tools.record_map_to_local_file("map_record_after.txt", map_record)

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

        """
            If any move has been pressed, then press Enter or z key. After that, game will output
            some messages which we can catch to know the screen has been completely updated.
            Enter: _Unknowncommand.
            z key: _Youdon'tknowanyspells.
            Can been changed those keys.
        """
        if need_to_update_screen and player_state_mode != 3:
            os.write(file_descriptor, get_update_screen_key(screen_update_switch_button))
            time.sleep(0.05)

        # Check any monster has showed, than switch player_state.
        if not need_to_update_screen and player_states is not None and player_state_mode != 3:
            if check_any_monster_come_and_update_map(map_record, player_states):
                player_state_mode = 1
            else:
                player_state_mode = 0

        # Fighting Mode Start ##################################################################
        if player_state_mode == 1:
            if not need_to_update_screen:
                if player_states is not None:
                    monsters_dic = player_states['Monsters']
                    for monster_num, monster_name_list in monsters_dic.items():
                        monster_position = get_monster_position(map_record, monster_name_list[0])
                        if monster_position is not None:
                            break
                    # print "monster_position: "+str(monster_position)
                    if monster_position is not None:
                        player_position = get_player_position(player_move_history)
                        # print "player_position: " + str(player_position)
                        attack_moves_list = path_finding_tool.path_finding(player_position, monster_position, map_record)
                        # print "attack_moves_list: " + str(attack_moves_list)
                        if attack_moves_list:
                            message = attack_moves_list[0]
                            move = check_move_keys(message)
                            can_pass = True
                            if move != (0, 0):
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
                        # else:
                        #     print "This target can't pass."
        # Fighting Mode End ####################################################################

        if button_bot_start and not button_path_go:
            button_path_finding = True

        # Check any fogs
        map_record, fogs_list = check_fogs(map_record, game_dictionary)
        # fogs_list = fogs_dic.keys()
        if button_path_finding and player_state_mode != 3:
            button_path_finding = not button_path_finding
            if fogs_list:
                player_state_mode = 1
                a_fog_can_pass = False
                player_position = get_player_position(player_move_history)
                fogs_list_with_dis = get_fogs_list_with_distance(player_position, fogs_list, tools)
                for fog_position_with_dis in fogs_list_with_dis:
                    print "Target position: " + str(fog_position_with_dis[1])
                    path_finding_list = path_finding_tool.path_finding(player_position,
                                                                       fog_position_with_dis[1],
                                                                       map_record)
                    if path_finding_list:
                        print "Moves: " + str(path_finding_list)
                        a_fog_can_pass = True
                        break
                    else:
                        print "This target can't pass."
                if not a_fog_can_pass:
                    print "No fog can pass."
                    player_state_mode = 2   # Switch to decision mode
            else:
                # Switch to decision mode
                player_state_mode = 2

            if player_state_mode == 2:
                door_position = None
                for position, data_list in map_record.items():
                    if data_list[0] == '+':
                        door_position = position
                        # To update the map_record, then path_finding can get there
                        data_list[4] = True
                        break
                if door_position is not None:
                    player_position = get_player_position(player_move_history)
                    path_finding_list = path_finding_tool.path_finding(player_position,
                                                                       door_position,
                                                                       map_record)
                    print "Move to the door: " + str(door_position)
                    if path_finding_list:
                        print "Moves: " + str(path_finding_list)
                    else:
                        print "This target can't pass."





        # if button_bot_start and path_finding_list:
        #     button_path_go = True
        # else:
        #     button_path_go = False

        # if press p, start move by path_finding_list
        if button_path_go and player_state_mode != 3:
            # If any monster come, stop moving and try to attack the monster.
            if player_state_mode == 1:
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
                            if check_is_door(map_record, player_move_history, move):
                                can_pass = True

                            map_record_backup = map_record
                        if can_pass:
                            send_input_to_game(file_descriptor, message)
                            # time.sleep(0.05)
                        else:
                            print " "
                            print "Something wrong. Stop moving and clear path_finding_list"
                            player_position = get_player_position(player_move_history)
                            target_position = (player_position[0] + move[0],
                                               player_position[1] + move[1])
                            print "Player position: " + str(player_position)
                            print "move: " + str(move)
                            print "map_record[target_position]: " + str(map_record[target_position])
                            button_path_go = False
                            path_finding_list[:] = []
                        # time.sleep(0.05)
                    else:
                        # Finish all moves
                        button_path_go = False

        # Some msgs area
        print "Testing Message:"
        print "Screen update times: " + str(screen_update_counter)
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
    print "Stop..."
finally:
    # Reset terminal settings back to how they were before
    termios.tcsetattr(sys.stdin, termios.TCSANOW, original)
