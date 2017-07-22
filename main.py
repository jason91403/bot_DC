import os
import sys
from select import select
import termios
import time
import pyte


def path_finding(player_position, target_position, map_detail_dic):
    target_node_found, open_list, close_list = a_star_search(player_position, target_position, map_detail_dic)
    move_list = []
    if target_node_found:
        track_back_list = track_back_path(close_list, player_position, target_position)
        move_list = transfer_to_move(track_back_list)
    # else:
    #     print "There is no way to the target."
    return move_list


def a_star_search(player_position, target_position, map_detail_dic):
    node_now = (player_position, 0, None)
    open_list = []
    close_list = []
    target_node_found = False
    open_list.append(node_now)
    while open_list:
        node_now = open_list[0]
        if target_position == node_now[0]:
            target_node_found = True
            close_list.append(node_now)
            break
        else:
            close_list.append(node_now)
            open_list.remove(node_now)
            neighbors_list = find_neighbors(node_now[0], map_detail_dic)
            for nb_node in neighbors_list:
                if (not check_if_in_list(nb_node[0], open_list)) and (not check_if_in_list(nb_node[0], close_list)):
                    open_list.append((nb_node[0],
                                      count_cost(nb_node[0], player_position, target_position),
                                      nb_node[1]))
            open_list.sort(key=lambda x: x[1])
    return target_node_found, open_list, close_list


def track_back_path(close_list,node_start, node_target):
    close_list_dic = {}
    for node in close_list:
        # key: position, value: parent
        close_list_dic[node[0]] = node[2]

    track_back_list = [node_target]
    node_parent = close_list_dic[node_target]
    while node_parent != node_start:
        # track_back_list.append(node_parent)
        track_back_list.insert(0, node_parent)
        node_parent = close_list_dic[node_parent]
    return track_back_list


def transfer_to_move(positions_list):
    player_position = (16, 8)
    move = None
    move_list = []
    move_dic = { (1, 0): 'R', (0, 1): 'U', (-1, 0): 'L', (0, -1): 'D',
                 (1, 1): 'RU',(1, -1): 'RD', (-1, 1): 'LU', (-1, -1): 'LD'}
    if positions_list:
        for i in range(len(positions_list)):
            key_position = (positions_list[i][0] - player_position[0],
                            player_position[1] - positions_list[i][1])
            if key_position in move_dic:
                move_list.append(move_dic[key_position])
                player_position = positions_list[i]
            else:
                print "Error: def transfer_to_move: key_position not in move_dic."
                print "  key_position: " + str(key_position)
                break
    else:
        print "Error: def transfer_to_move: positions_list is empty."
    return move_list


    
    

'''
def a_star_search_2(map_detail_dic, target_position):
    # open_list each item: (node_position, f_score, g_score, h_score)
    open_list = []
    # close_list each item: (node_position, f_score, g_score, h_score, parent)
    close_list = []
    target_node_found = False
    player_position = (16, 8)
    node_start_h_score = count_distance(player_position, target_position)
    node_start = (player_position, node_start_h_score, 0, node_start_h_score)
    open_list.append(node_start)
    while open_list:
        node_current = open_list[0]
        if target_position == node_current[0]:
            target_node_found = True
            break
        node_successors_list = find_neighbors(node_current[0], map_detail_dic)
        # node_successors_list = find_successors_with_score(node_current[0], node_start[0],
        #                                                   target_position, map_detail_dic)
        for node_successor in node_successors_list:
            successor_current_cost = (count_distance(node_current[0], node_start[0]) +
                                      count_distance(node_current[0], node_successor))
            g_score_node_successor = count_distance(node_start[0], node_successor)
            # tmp node pop out from close_list
            tmp_node = check_if_in_list(node_successor, close_list)
            if check_if_in_list(node_successor, open_list) is not None:
                if g_score_node_successor <= successor_current_cost:
                    continue
            elif tmp_node is not None:
                if g_score_node_successor <= successor_current_cost:
                    continue
                tmp_node_to_o = (tmp_node[0], tmp_node[1], tmp_node[2], tmp_node[3])
                open_list.append(tmp_node_to_o)
                close_list.remove(tmp_node)
            else:
                open_list.append(node_successor)

        #sort openlist by f_score

    return target_node_found, open_list, close_list
'''


def count_cost(node, start_node, target_node):
    g_score = abs(int(node[0]) - int(start_node[0])) + abs(int(node[1]) - int(start_node[1]))
    h_score = abs(int(node[0]) - int(target_node[0])) + abs(int(node[1]) - int(target_node[1]))
    f_score = g_score + h_score
    return f_score


def count_distance(node_1, node_2):
    dis = abs(int(node_1[0]) - int(node_2[0])) + abs(int(node_1[1]) - int(node_2[1]))
    return dis


def check_if_in_list(node_position, mlist):
    in_list = False
    for n in mlist:
        if node_position == n[0]:
            in_list = True
    return in_list


def find_neighbors(node_position, map_detail_dic):
    nb_list = []
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == 0 and y == 0:
                continue
            nb_position_x = int(node_position[0]) + x
            nb_position_y = int(node_position[1]) + y
            if 0 <= nb_position_x <= 32 and 0 <= nb_position_y <= 16:
                nb = map_detail_dic[nb_position_x, nb_position_y]
                if nb[1]:
                    nb_list.append(((nb_position_x, nb_position_y), node_position))
                    # (node_position, parent)
    return nb_list


def find_successors_with_score(node_position, node_start, node_target, map_detail_dic):
    successors_list = []
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == 0 and y == 0:
                continue
            s_position_x = int(node_position[0]) + x
            s_position_y = int(node_position[1]) + y
            if 0 <= s_position_x <= 32 and 0 <= s_position_y <= 16:
                node = map_detail_dic[s_position_x, s_position_y]
                # node[1] = can pass?
                if node[1]:
                    successor = (s_position_x, s_position_y)
                    g_score = count_distance(successor, node_start)
                    h_score = count_distance(successor, node_target)
                    f_score = g_score + h_score
                    successors_list.append(successor, f_score, g_score, h_score)
    return successors_list


'''
Map:
x range 0~32
y range 0~16

whole screen
x max = 79
(16, 8): @

'''


def analyse_screen(sl):
    map_dic = {}
    states_dic = {}

    for y in range(len(sl)):
        for x in range(len(sl[y])):
            if y < 17 and x < 34:
                map_dic[(x, y)] = sl[y][x].encode('ascii')
            elif x > 36:
                states_dic[(x, y)] = sl[y][x].encode('ascii')

    map_detail_dic = catch_map(map_dic)
    player_states_dic = catch_states(states_dic)

    return map_detail_dic, player_states_dic


def catch_map(map_dic):
    map_detail_dic = {}
    '''
    map_detail_dic = [symbol, can pass?, ]
    '''
    for key, value in map_dic.items():
        map_detail_dic[key] = [value, can_pass(unicode(value))]
    return map_detail_dic


def can_pass(symbol):
    symbol_can_pass = False
    can_pass_list = [".", "'", "+"]
    if symbol in can_pass_list:
        symbol_can_pass = True
    return symbol_can_pass


# def analyse_screen_by_screen_dic(sl_dic):
#     map_dic = {}
#     states_dic = {}
#
#     states_dic = {'Career': sl_dic[1][37:78],
#                   'Health': sl_dic[2][44:55],
#                   'Magic': sl_dic[3][43:55],
#                   'AC': sl_dic[4][40:55],
#                   'Str': sl_dic[4][59:80],
#                   'EV': sl_dic[5][40:55],
#                   'Int': sl_dic[5][59:80],
#                   'SH': sl_dic[6][40:55],
#                   'DEX': sl_dic[6][59:80],
#                   'XL': sl_dic[7][40:55],
#                   'Place': sl_dic[7][61:80],
#                   'Glod': sl_dic[8][42:55],
#                   'Time': sl_dic[8][60:80]}
#     return map_dic, states_dic

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


'''
After translation:
up    => i
down  => k
left  => j
right => l
i     => h

original:
right up    => u
right down  => n
left up     => y
left down   => b
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
    # stream = pyte.ByteStream()
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
        # to check the input Dec code
        if observed_mode:
            player_position = (16, 8)
            target_position = (21, 8)
            path_finding_list = path_finding(player_position, target_position, map_dic)
            if path_finding_list:
                print "To target: " + str(target_position)
                print "Move: " + str(path_finding_list)

            # print "You enter keyboard Dec: " + str(observed_key)
            # print map_dic[(16, 8)]

            # testword = player_states['Health']

            # print map_dic[(16, 9)]

            # target_node_found, op_list, cl_list = a_star_search(map_dic, (21, 8))
            # print target_node_found
            # print "op_list: " + str(op_list)
            # print "cl_list: " + str(cl_list)
            # if target_node_found:
            #     track_back_list = track_back_path(cl_list, (16, 8), (21, 8))
            #     transfer_to_move_list = transfer_to_move(track_back_list)
            #     print track_back_list
            #     print transfer_to_move_list







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
