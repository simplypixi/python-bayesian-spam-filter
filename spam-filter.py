from __future__ import print_function
import re, string
from bayesian import classify

def readMailsFromFile(fname):
    f = open(fname, "r")
    messages = []
    for line in f:
        line = re.sub('\s+',' ',line)
        line = re.sub('\n',' ',line)
        """ Delete punctuation """
        exclude = set(string.punctuation)
        line = ''.join(ch for ch in line if ch not in exclude)
        line = re.sub('^MESSAGE ', '', line)
        line = re.sub('\t', '', line)
        if line.strip():
           messages.append(line)
    
    return messages
 
def readTestMailsFromFile(fname):
    f = open(fname, "r")
    messages = []
    numberOfSpam = 0
    numberOfHam = 0
    for line in f:
        line = re.sub('\s+',' ',line)
        line = re.sub('\n',' ',line)
        """ Delete punctuation """
        exclude = set(string.punctuation)
        line = ''.join(ch for ch in line if ch not in exclude)
        line = re.sub('^MESSAGE ', '', line)

        if line[4:].strip():
           if line[:3] == "TAK":
              numberOfSpam = numberOfSpam + 1
           else:
              numberOfHam = numberOfHam + 1
           line = re.sub('\t', '', line)
           messages.append(line)
    
    return {
             "messages" : messages,
             "spam" : numberOfSpam,
             "ham" : numberOfHam
           }

ham = readMailsFromFile("./corpus/nospam2.txt")
spam = readMailsFromFile("./corpus/spam2.txt")
tests = readTestMailsFromFile("./corpus/test-final.txt")

print("Messages to filter: %d" % len(tests["messages"]))
hamCount = 0
spamCount= 0
goodHam = 0
goodSpam = 0

for index, test in enumerate(tests["messages"]):
     classif = classify(test, {'spam': spam, 'ham': ham})
     if test[:3] == "TAK" and classif == 'spam':
        goodSpam = goodSpam + 1
     if test[:3] == "NIE" and classif == 'ham':
        goodHam = goodHam + 1
     if classif == 'ham':
        hamCount = hamCount + 1
     else:
        spamCount = spamCount + 1
     test = test[4:]
     print("%d. \"%s...\" is" % (index,test[:50]), classif)

print("SPAM: %d" % spamCount)
print("HAM: %d" % hamCount)
print("Accuracy: ", ((goodSpam+goodHam)/float(len(tests["messages"])))*100, "%")

