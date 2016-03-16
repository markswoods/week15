# I'm not cheating, Python's ability to manipulate low level datatypes is poor
from __future__ import division
from bitstring import BitArray 
from collections import Counter
import nltk

encoded_msg = '1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736'
etaoin = ['e', 't', 'a', 'o', 'i', 'n']
shrdlu = ['s', 'h', 'r', 'd', 'l', 'u']

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
        
def score(msg):
    # See if this looks like an English phrase
    msg = msg.lower()
    counts = Counter(msg).most_common(5)   # Count up character frequencies
    score = 0
    for i in range(0, 5):   
        if counts[i][0] in etaoin: 
            score += 1
        if counts[i][0] in shrdlu: 
            score -= 1   
            
    #words = nltk.word_tokenize(msg)         
    return score
        
# Let's get a count of 2-character substrings in the encoded_msg
msg2 = ''
for i in range(0, len(encoded_msg), 2):     # Proceeding one hex character at a time
     msg2 += encoded_msg[i:i+2] + " "    
list = msg2.split(' ')    
counts = Counter(list)                      # Now I have a sorted list of the characters and their counts

# I'm going to guess one of the most frequen characters is in ETAOIN, let's see
candidates = {}
keylist = []
for char, _ in counts.most_common(6):       # Use most commonly occuring encoded_msg characters
    char_in_hex = '0x' + char
    for common_char in etaoin:
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
            msg += chr(char.int)        
        s = score(msg)
        candidates[key.hex] = {"score": s, "msg": msg}    # I should include the score

# Find the key with the max score 
key = ''
max_score = 0
for k in candidates.keys():
    if candidates[k]['score'] > max_score:
        max_score = candidates[k]['score']
        key = k
    
print "key: %s, score: %d, msg: %s" % (key, max_score, candidates[key]["msg"])
 

