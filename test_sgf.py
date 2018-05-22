# test out the sgf module by reading the main variation from an SGF

import sgf
import sys

def decode_sgf_coordinate(s):
    # convert from an SGF coordinate string like "bc" to integer coordinates like 2,3
    y, x = map(lambda x: ord(x) - ord('a'), s)
    return x, y

filename = sys.argv[1]
with open(filename) as f:
    # note: we assume the SGF file is UTF-8 encoded
    collection = sgf.parse(f.read().decode('utf-8'))

    # for each game in the SGF file...
    for i, gametree in enumerate(collection.children):
        print 'GAME NUMBER', i+1
        # for each node in the game...
        # (note: we only look at the main variation)
        result = None
        for j, node in enumerate(gametree):
            p = node.properties
            if 'SZ' in p:
                board_size = int(p['SZ'][0])
                print 'Board size is',  board_size
            if 'PW' in p:
                white_player_name = p['PW'][0]
                print 'White player is', white_player_name
            if 'PB' in p:
                black_player_name = p['PB'][0]
                print 'Black player is', black_player_name
            if 'RU' in p:
                rule_set = p['RU'][0]
                print 'Rule set is', rule_set
            if 'RE' in p:
                result = p['RE'][0]

            if 'B' in p:
                print 'Black plays at', decode_sgf_coordinate(p['B'][0])
            if 'W' in p:
                print 'White plays at', decode_sgf_coordinate(p['W'][0])
        if result:
            print 'Result of the game is', result
