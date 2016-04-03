# I'm not cheating, Python's ability to manipulate low level datatypes is poor
from __future__ import division
import sys
from bitstring import BitArray 
from collections import Counter

# With this problem we have a file to read. Each line in the file could be either obfuscated
# text, or it could contain an english passphrase that has been xor'd. Fun!
etaoin = ['e', 't', 'a', 'o', 'i', 'n', 'E', 'T', 'A', 'O', 'I', 'N']
shrdlu = ['s', 'h', 'r', 'd', 'l', 'u', 'S', 'H', 'R', 'D', 'L', 'U']

def xor(x1, x2):
# pass in single characters
    b1, b2, res = BitArray(x1), BitArray(x2), BitArray('0b00000000')
    for j in range(0, 8):
        if b1[j:j+1] == '0b1' and b2[j:j+1] == '0b1':
            res[j:j+1] = '0b0'
        else:
            if b1[j:j+1] == '0b1' or b2[j:j+1] == '0b1':
                res[j:j+1] = '0b1'
    return res
    
def unxor(char, result):
    # If result = key xor char, then what is key?
    charb, resultb, key = BitArray(char), BitArray(result), BitArray('0b00000000')
    for j in range(0, 8):
        if charb[j:j+1] == '0b1' and resultb[j:j+1] == '0b1':
            key[j:j+1] = '0b0'
        else:
            if charb[j:j+1] == '0b0' and resultb[j:j+1] == '0b0':
                key[j:j+1] = '0b0'
            else:
                if charb[j:j+1] == '0b0' and resultb[j:j+1] == '0b1':
                    key[j:j+1] = '0b1'
                else:
                    if charb[j:j+1] == '0b1' and resultb[j:j+1] == '0b0':
                        key[j:j+1] = '0b1'                
    return key

def avg_word_length(msg):
    # Consider average word length in the phrase
    words = msg.split(' ')
    word_length = 0
    for w in words:
        word_length += len(w)
    return word_length/len(words)
        
def score(msg):
    # See if this looks like an English phrase
    msg = msg.lower()
    counts = Counter(msg).most_common(5)   # Count up character frequencies
    score = 0
    for i in range(0, len(counts)):   
        if counts[i][0] in etaoin: 
            score += 1
        if counts[i][0] in shrdlu: 
            score -= 1
    # Some other differentiators
    if score > 0 and ' ' in msg:
        score += 1
    if '...' in msg:
        score -= 1
        
    if avg_word_length(msg) <= 5:
        score += len(msg.split(' '))
    else:
        score -= 1
                           
    return score

def decrypt_line(lineno, encoded_msg):
    # Let's get a count of 2-character substrings in the encoded_msg
    msg2 = ''
    for i in range(0, len(encoded_msg), 2):     # Proceeding one hex character at a time
        msg2 += encoded_msg[i:i+2] + " "    
    list = msg2.split(' ')   
    counts = Counter(list)                  # Now I have a sorted list of the characters and their counts

    """The average word length should be around 5 characters. One of my most common
    characters should probably be a ' ' - a word separator. Maybe even the most
    common. Using that separator, if average word length is too high, just skip the line!
    Remember to divide length by two since each 'letter' in word is a two digit hex character
    """
    if counts.most_common(1)[0][0] != '':
        word_length = 0
        word_list = encoded_msg.split(counts.most_common(1)[0][0])
        for w in word_list:
            word_length += len(w)/2
    
        if  word_length/len(word_list) > 7:
            print "skipping line: %d" % lineno
            return
    print "trying line: %d" % lineno
    # I'm going to guess one of the most frequent characters is in ETAOIN, let's see
    candidates = {}
    keylist = []
    for char, _ in counts.most_common(6):       # Use most commonly occuring encoded_msg characters
        if char == '':                          # Not sure how this can happen, but it does...
            continue
        char_in_hex = '0x' + char
        for common_char in etaoin[0:6]:
            # Now, what code when XOR'd with above would yield an e=0x65, E=0x45, T=0x54, t=0x74, a=0x61
            key = unxor(hex(ord(common_char)), char_in_hex)
            # Let's try using this key in unxor, now I'm asking char = key XOR code, what is char?
            if key.hex in keylist:              # If this key was already generated, then skip to next
                continue    
            else:
                keylist.append(key.hex)
                msg = ''
                for i in range(0, len(encoded_msg), 2):
                    encoded_char = '0x' + encoded_msg[i:i+2]
                    char = unxor(key, encoded_char)     # returned as a BitArray
                    # A printable character must be in the range of 32 - 126 (20 - 7E)
                    if char.int >= 32 and char.int <= 126:
                        msg += chr(char.int) 
                    else:
                        msg += '.'       
                
                s = score(msg)
                candidates[key.hex] = {"score": s, "msg": msg}    
                
    # Find the key with the max score 
    key = ''
    max_score = 0
    for k in candidates.keys():
        if candidates[k]['score'] > max_score:
            max_score = candidates[k]['score']
            key = k
    
    if key != '' and max_score > 3:
        # Grab all keys with the same score
        for k in candidates.keys():
            if candidates[k]['score'] == max_score:
                print "line: %d, key: %s, score: %d, msg: %s" % (lineno, k, max_score, candidates[k]["msg"])
   
# Main
fname = sys.argv[1]
if fname == "":
  fname = "pass_file.txt"

lines = []
file = open(fname, 'r')
for line in file:
    lines.append(line.strip())
file.close()


for i in range(0, len(lines)):
    decrypt_line(i+1, lines[i])