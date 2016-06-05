import json
import urllib2
import webbrowser
from Tkinter import *

selectedTags = set()
listsLabels = ['A', 'B', 'C', 'D', 'E', 'Other']
lists = {}
root = Tk()
handleEntry = Entry(root)

def updateTablesWithUnsolvedProblems(solvedProblems):
    url = 'http://codeforces.com/api/problemset.problems?tags='
    for tag in selectedTags:
        fixedTag = ''
        for c in tag:
            if c == ' ':
                fixedTag += '%20'
            else:
                fixedTag += c
        url += fixedTag + ';'
    result = getResult(url)
    problems = result['problems']
    problemsStatistics = result['problemStatistics']

    for key, value in lists.iteritems():
        value[0].delete(0,END)
        del value[1][:]

    for idx, problem in enumerate(problems):
        problemID = str(problem['contestId']) + str(problem['index'])
        if problemID not in solvedProblems:
            problemIdx = str(problem['index'])
            if(len(problemIdx) > 1 or problemIdx[0] < 'A' or problemIdx[0] > 'E'):
                problemIdx = 'Other'
                
            problemURL = 'http://codeforces.com/contest/' +  str(problem['contestId']) + '/problem/' + str(problem['index'])
            # problemURL = 'http://codeforces.com/problemset/problem/' +  str(problem['contestId']) + '/' + str(problem['index'])
            lists[problemIdx][1].append((problem['name'], problemsStatistics[idx]['solvedCount'], problemURL))

    for value in lists.itervalues():
        value[1].sort(key = lambda x : -x[1])
        for item in value[1]:
            value[0].insert(END,item[0] + ' (' + str(item[1]) + ')')

def refresh():
    root.config(cursor="wait")
    root.update()
    solvedProblems = getSolvedProblems(handleEntry.get())
    updateTablesWithUnsolvedProblems(solvedProblems)
    root.config(cursor="")
    root.update()

def getResult(url):
    response = urllib2.urlopen(url)
    data = response.read()
    parsedJson = json.loads(data)
    return parsedJson['result']

def getSolvedProblems(handle):
    url = 'http://codeforces.com/api/user.status?handle=' + handleEntry.get()
    problems = getResult(url)
    solvedProblems = set()
    for problem in problems:
        verdict = problem['verdict']
        if verdict == 'OK':
            problemID = str(problem['problem']['contestId']) + str(problem['problem']['index'])
            solvedProblems.add(problemID)
    return solvedProblems

if __name__ == "__main__":
    root.title('CF Tutor')
    DEFAULT_HANDLE = 'gbuenoandrade'
    Label(root, text="Handle: ").grid(row=0,column=2,sticky=W)
    handleEntry.grid(row=0,column=3,sticky=W)
    handleEntry.insert(0,DEFAULT_HANDLE)
    tags = ['2-sat', 'binary search', 'bitmasks', 'brute force', 'chinese remainder theorem', 'combinatorics',
            'constructive algorithms', 'data structures', 'dfs and similar', 'divide and conquer', 'dp', 'dsu',
            'expression parsing', 'fft', 'flows', 'games', 'geometry', 'graph matchings', 'graphs', 'greedy', 'hashing',
            'implementation', 'math', 'matrices', 'meet-in-the-middle', 'number theory', 'probabilities', 'schedules',
            'shortest paths', 'sortings', 'string suffix structures', 'strings', 'ternary search', 'trees',
            'two pointers']

    def selector1(option):
        def selectTag(tag=option):
            if tag in selectedTags:
                selectedTags.discard(tag)
            else:
                selectedTags.add(tag)
        return selectTag

    for idx,tag in enumerate(tags):
        COLUMNS = 6
        ROWS = len(tags)/6
        if len(tags)/6:
            ROWS+=1
        check = Checkbutton(root, text=tag, command=selector1(tag))
        check.grid(row=idx%ROWS+1, column=(idx/ROWS),sticky=W)

    def selector2(option):
        def onselect(evt,label=option):
            w = evt.widget
            index = int(w.curselection()[0])
            url = lists[label][1][index][2]
            webbrowser.open(url, new=2)
        return onselect

    for idx, listLabel in enumerate(listsLabels):
        Label(root, text=listLabel).grid(row=ROWS + 2, column=idx)
        list = Listbox(root)
        lists[listLabel] = (list,['a'])
        list.grid(row=ROWS+3, column=idx)
        list.bind('<<ListboxSelect>>', selector2(listLabel))

    updateButton = Button(root, text="Refresh", command=refresh)
    updateButton.grid(row=ROWS+4,column=3, stick=W)
    root.mainloop()
