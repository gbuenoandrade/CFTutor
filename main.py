import json
import urllib2
import webbrowser
import os
from Tkinter import *

selectedTags = set()
listsLabels = ['Div1A', 'Div1B', 'Div1C', 'Div1D', 'Div1E', 'Other', 'Div2A', 'Div2B', 'Div2C', 'Div2D', 'Div2E']
lists = {}
root = Tk()
handleEntry = Entry(root)
solvedProblemsPerUser = {}
divDict = {}
probDict = {}

def getResultFromFile(fileName):
	data = open(fileName, 'r').read()
	parsedJson = json.loads(data)
	return parsedJson['result']

def getResultFromURL(url, fileName):
	response = urllib2.urlopen(url)
	data = response.read()
	if fileName != '':
		with open(fileName, 'w') as file_:
			file_.write(data)
	parsedJson = json.loads(data)
	return parsedJson['result']

def refreshDumpFiles():
	urls = {}
	urls['problems_dump'] = 'http://codeforces.com/api/problemset.problems'
	urls['contests_dump'] = 'http://codeforces.com/api/contest.list?gym=false'
	for key, value in urls.iteritems():
		with open(key + '.json', 'w') as file_:
			response = urllib2.urlopen(value)
			data = response.read()
			file_.write(data)

def updateDivDict():
	global divDict
	divDict = {}
	contests = getResultFromFile('contests_dump.json')
	for contest in contests:
		cid = contest['id']
		cdiv = 0
		if contest['name'].find('Div. 1') != -1:
			cdiv = 1
		elif contest['name'].find('Div. 2') != -1:
			cdiv = 2
		divDict[cid] = cdiv

def updateProbDict():
	global probDict
	probDict = {}
	result = getResultFromFile('problems_dump.json')
	problems = result['problems']
	problemsStatistics = result['problemStatistics']
	for idx, problem in enumerate(problems):
		probDictItem = {}
		problemID = str(problem['contestId']) + str(problem['index'])
		problemURL = 'http://codeforces.com/problemset/problem/' +  str(problem['contestId']) + '/' + str(problem['index'])
		probDictItem['url'] = problemURL
		solvedCount = problemsStatistics[idx]['solvedCount']
		probDictItem['solvedCount'] = solvedCount
		problemName = problem['name']
		probDictItem['name'] = problemName
		problemDiv = divDict[problem['contestId']]
		probDictItem['div'] = problemDiv
		problemIdx = str(problem['index'])
		if problemDiv == 0 or len(problemIdx) > 1 or problemIdx[0] < 'A' or problemIdx[0] > 'E':
			problemIdx = 'Other'
		if problemIdx != 'Other':
			problemIdx = 'Div' + str(problemDiv) + problemIdx
		probDictItem['idx'] = problemIdx
		probDictItem['tags'] = set()
		for tag in problem['tags']:
			probDictItem['tags'].add(tag)
		probDict[problemID] = probDictItem

def getSolvedProblems(handle, starting_from, all_prob):
	BLOCK_SIZE = 10
	url = ''
	if all_prob:
		url = 'http://codeforces.com/api/user.status?handle=' + handle
	else:
		url = 'http://codeforces.com/api/user.status?handle=' + handle + '&from=' + str(starting_from) + '&count=' + str(BLOCK_SIZE)
	fileName = ''
	if all_prob:
		fileName = handle + '.json'
	problems = getResultFromURL(url,fileName)
	solvedProblems = set()
	smaller_id = 0
	for problem in problems:
		verdict = problem['verdict']
		smaller_id = problem['id']
		if verdict == 'OK':
			problemID = str(problem['problem']['contestId']) + str(problem['problem']['index'])
			solvedProblems.add(problemID)
	largestID = -1
	if handle in solvedProblemsPerUser:
		largestID = solvedProblemsPerUser[handle][1]
	if len(problems) == BLOCK_SIZE and smaller_id > largestID:
		return (solvedProblems.union(getSolvedProblems(handle, starting_from + BLOCK_SIZE, False)[0]), problems[0]['id'])
	else:
		return (solvedProblems, problems[0]['id'])

def refreshDumps():
	root.config(cursor="wait")
	root.update()
	refreshDumpFiles()
	updateDivDict()
	updateProbDict()
	updateTables()
	root.config(cursor="")
	root.update()

def refreshUserFromFile(handle):
	if os.path.isfile(handle + '.json') == False:
		return
	problems = getResultFromFile(handle + '.json')
	solvedProblems = set()
	for problem in problems:
		verdict = problem['verdict']
		if verdict == 'OK':
			problemID = str(problem['problem']['contestId']) + str(problem['problem']['index'])
			solvedProblems.add(problemID)

	solvedProblemsPerUser[handle] = (solvedProblems, problems[0]['id'])

def refreshUser():
	root.config(cursor="wait")
	root.update()	
	handle = handleEntry.get()
	if handle not in solvedProblemsPerUser:
		refreshUserFromFile(handle)
	if handle not in solvedProblemsPerUser:
		solvedProblemsPerUser[handle] = getSolvedProblems(handle,1,True)
	else:
		newProblems,lastID = getSolvedProblems(handle,1,False)
		oldProblems = solvedProblemsPerUser[handle][0]
		newProblems = newProblems.union(oldProblems)
		solvedProblemsPerUser[handle] = (newProblems, lastID)
	updateTables()
	root.config(cursor="")
	root.update()	

def updateTables():
	solvedProblems = solvedProblemsPerUser[handleEntry.get()][0]

	for key, value in lists.iteritems():
		value[0].delete(0,END)
		del value[1][:]

	for problemID, problem in probDict.iteritems():
		if problemID not in solvedProblems:
			ok = True
			for tag in selectedTags:
				if tag not in problem['tags']:
					ok = False
					break
			if ok == False:
				continue
			problemIdx = problem['idx']                
			problemURL = problem['url']
			lists[problemIdx][1].append((problem['name'], problem['solvedCount'], problemURL))

	for value in lists.itervalues():
		value[1].sort(key = lambda x : -x[1])
		for item in value[1]:
			value[0].insert(END,item[0] + ' (' + str(item[1]) + ')')


if __name__ == "__main__":
	root.title('CF Tutor')
	DEFAULT_HANDLE = open('default_handle.txt', 'r').read()
	updateDivDict()
	updateProbDict()
	Label(root, text="Handle: ").grid(row=0,column=2)
	handleEntry.grid(row=0,column=3,sticky=W)
	handleEntry.insert(0,DEFAULT_HANDLE)

	updateButton = Button(root, text="Refresh User", command=refreshUser)
	updateButton.grid(row=0,column=4)
	updateButton = Button(root, text="Refresh Dumps", command=refreshDumps)
	updateButton.grid(row=0,column=5)

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
			updateTables()
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
		Label(root, text=listLabel).grid(row=ROWS + 2 + (idx/6)*2, column=idx%6)
		list = Listbox(root)
		lists[listLabel] = (list,['a'])
		list.grid(row=ROWS+3 + (idx/6)*2, column=idx%6)
		list.bind('<<ListboxSelect>>', selector2(listLabel))

	refreshUser()
	root.mainloop()
