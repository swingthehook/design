from var import dic, S, vt, predictSet,vt_path, formula_path, predict_path

ffirstSet = {}  # 产生式右端的first集
cfirstSet = {}  # 产生式左端vt的first集
followSet = {}  # follow集

def generateFFTSet():
    fv = open(vt_path, 'r')
    ff = open(formula_path, 'r')
    # 读VT
    for v in fv.read().strip(' ').split(' '):
        vt.add(v)
    # 读产生式
    for line in ff.readlines():
        temp = line.strip('\n').strip(' ').split(' ::= ')
        dic[temp[0]] = temp[1]
        # cfirst集初始化
        cfirstSet[temp[0]] = set()
        # follow集初始化
        followSet[temp[0]] = set()
    fv.close()
    ff.close()

    # first集
    for key in dic.keys():
        genFirstSet(key)
    # follow集
    genFollowSet()
    # predict集
    genPredictSet()

    # 写predict集
    fp = open(predict_path, 'w')
    for key in dic.keys():
        for formula in dic[key].split(' | '):
            for item in predictSet[key + ' = ' + formula]:
                fp.write(item + ' ')
            fp.write('\n')
    fp.close()

    return


def genFirstSet(key):
    # 生成cfirst集和ffirst集
    for formula in dic[key].split(' | '):
        ffirstSet[key + ' = ' + formula] = set()
        flag = 0
        for v in formula.split(' '):
            flag = 0
            if v in vt:
                ffirstSet[key + ' = ' + formula].add(v)
                break
            elif v == '$':
                ffirstSet[key + ' = ' + formula].add("$")
                break
            else:
                # 判断v的fist是否已经生成
                if cfirstSet[v]:
                    ffirstSet[key + ' = ' + formula] |= cfirstSet[v]
                else:
                    ffirstSet[key + ' = ' + formula] |= genFirstSet(v)
                if "$" not in ffirstSet[key + ' = ' + formula]:
                    break
                else:
                    ffirstSet[key + ' = ' + formula].remove('$')
                    flag = 1
        if flag == 1:
            ffirstSet[key + ' = ' + formula].add("$")
        cfirstSet[key] |= ffirstSet[key + ' = ' + formula]
    return cfirstSet[key]


def findFirstSet(vl):
    # 根据已生成的first集，寻找特定串的first集，用于follow集生成
    s = set()
    flag = 1
    for v in vl:
        flag = 0
        if v in vt:
            s.add(v)
            break
        else:
            s |= cfirstSet[v]
            if '$' not in s:
                break
            else:
                s.remove('$')
                flag = 1
    if flag == 1:
        s.add('$')
    return s


def genFollowSet():
    # 生成follow集
    followSet[S].add('#')
    change = set()
    for key in dic.keys():
        for formula in dic[key].split(' | '):
            if formula == '$':
                continue
            else:
                vl = formula.split(' ')
                for v in range(len(vl)):
                    if vl[v] not in vt:
                        # 这里取并集而不用‘=’
                        followSet[vl[v]] |= findFirstSet(vl[v + 1:])
                        if '$' in followSet[vl[v]]:
                            followSet[vl[v]].remove('$')
                            followSet[vl[v]] |= followSet[key]
                            # 将vl[v],key记录下来，这是每次迭代可能发生变化的地方
                            if vl[v] != key:
                                change.add((vl[v], key))
    flag = 1
    while flag == 1:
        flag = 0
        for t in change:
            if not followSet[t[0]].issuperset(followSet[t[1]]):
                followSet[t[0]] |= followSet[t[1]]
                flag = 1
    return


def genPredictSet():
    # 生成predict集
    for key in dic.keys():
        for formula in dic[key].split(' | '):
            predictSet[key + ' = ' + formula] = ffirstSet[key + ' = ' + formula]
            if '$' in predictSet[key + ' = ' + formula]:
                predictSet[key + ' = ' + formula].remove('$')
                predictSet[key + ' = ' + formula] |= followSet[key]
    return