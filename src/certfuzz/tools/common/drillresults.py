'''
Created on Jun 30, 2014

@organization: cert.org
'''


def readfile(textfile):
    '''
    Read text file
    '''
    with open(textfile, 'r') as f:
        return f.read()


def carve(string, token1, token2):
    startindex = string.find(token1)
    if startindex == -1:
        # can't find token1
        return ""
    startindex = startindex + len(token1)
    endindex = string.find(token2, startindex)
    if endindex == -1:
        # can't find token2
        return ""
    return string[startindex:endindex]


# Todo: fix this up.  Was added to bring gdb support
def carve2(string):
    delims = [("Exception Faulting Address: ", "\n"),
              ("si_addr:$2 = (void *)", "\n")]
    for token1, token2 in delims:
        startindex = string.find(token1)
        if startindex == -1:
            # can't find token1
            continue
        startindex = startindex + len(token1)
        endindex = string.find(token2, startindex)
        return string[startindex:endindex]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def score_crasher(crasher, details, ignorejit=False):
    scores = [100]
    if details['reallyexploitable'] == True:
    # The crash summary is a very interesting one
        for exception in details['exceptions']:
            module = details['exceptions'][exception]['pcmodule']
            if module == 'unloaded' and not ignorejit:
                # EIP is not in a loaded module
                scores.append(20)
            if details['exceptions'][exception]['shortdesc'] in re_set:
                efa = '0x' + details['exceptions'][exception]['efa']
                if details['exceptions'][exception]['EIF']:
                # The faulting address pattern is in the fuzzed file
                    if '0x000000' in efa:
                        # Faulting address is near null
                        scores.append(30)
                    elif '0x0000' in efa:
                        # Faulting address is somewhat near null
                        scores.append(20)
                    elif '0xffff' in efa:
                        # Faulting address is likely a negative number
                        scores.append(20)
                    else:
                        # Faulting address has high entropy.  Most exploitable.
                        scores.append(10)
                else:
                    # The faulting address pattern is not in the fuzzed file
                    scores.append(40)

    else:
        # The crash summary isn't necessarily interesting
        for exception in details['exceptions']:
            efa = '0x' + details['exceptions'][exception]['efa']
            module = details['exceptions'][exception]['pcmodule']
            if module == 'unloaded' and not ignorejit:
                scores.append(20)
            elif module.lower() == 'ntdll.dll' or 'msvcr' in module.lower():
                # likely heap corruption.  Exploitable, but difficult
                scores.append(45)
            elif '0x00120000' in efa or '0x00130000' in efa or '0x00140000' in efa:
                # non-continued potential stack buffer overflow
                scores.append(40)
            elif details['exceptions'][exception]['EIF']:
            # The faulting address pattern is in the fuzzed file
                if '0x000000' in efa:
                    # Faulting address is near null
                    scores.append(70)
                elif '0x0000' in efa:
                    # Faulting address is somewhat near null
                    scores.append(60)
                elif '0xffff' in efa:
                    # Faulting address is likely a negative number
                    scores.append(60)
                else:
                    # Faulting address has high entropy.
                    scores.append(50)
    return min(scores)

def score_reports(results, crashscores, ignorejit):
    # Assign a ranking to each crash report.  The lower the rank, the higher
    # the exploitability
    if results:
        print "--- Interesting crashes ---\n"
        # For each of the crash ids in the results dictionary, apply ranking
        for crasher in results:
            try:
                crashscores[crasher] = score_crasher(crasher, results[crasher], ignorejit)
            except KeyError:
                print "Error scoring crash %s" % crasher
                continue

def main():
    pass

if __name__ == '__main__':
    main()