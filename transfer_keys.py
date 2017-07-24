
class TransferKeys(object):
    def __init__(self):
        self.__keys_dic = {chr(10): chr(13),                        # Enter
                           chr(105): chr(27) + chr(91) + chr(65),   # Up: i => up arrow
                           chr(107): chr(27) + chr(91) + chr(66),   # Down: k down arrow
                           chr(106): chr(27) + chr(91) + chr(68),   # Left: j => left arrow
                           chr(108): chr(27) + chr(91) + chr(67)   # Right: l => right arrow
                           }

    def transfer(self, key_msg):
        try:
            return self.__keys_dic[key_msg]
        except KeyError:
            return key_msg



'''
Note:
X => display map
- => scroll up map
+ => scroll down map
'''

