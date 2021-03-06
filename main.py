# -*- coding: utf-8 -*
from Tkinter import *
from job import *
from verifier import *
import tkFont
import tkFileDialog
import os
import sys
import codecs
import time
import ttk
import threading
from datetime import datetime

globFont = "Verdena 8 bold"
logFolder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LOGS')
logFile = str(datetime.now().strftime('%Y-%m-%d %H.%M.%S')) + ' LOG.txt'

class MainWindow(Frame):
	if not os.path.exists(logFolder):
		os.mkdir(logFolder)

	def __init__(self, master):
		Frame.__init__(self, master, bd=2)
		self.master = master
		self.hdEntryText = ''
		self.hdButtonTick = BooleanVar()
		self.boxValue = StringVar()
		self.totalCount = 0
		self.customCount = 0
		self.log = []
		self.verifierLog = []
		self.rows = 1
		self.statLabelFull = False
		self.taskActive = False
		self.exportFails = False
		self.openSaveFile = None
		self.after(1, self.updateMainStates)
		self.emailDir = {}
		self.lock = threading.Lock()
		self.createMenus()
		self.createWindow()

	def createMenus(self):
		self.menubar = Menu(self)
		menu = Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label="File", menu=menu)
		menu.add_command(label="Exit", command=self.quit)
		menu.add_command(label="Open File", command=self.openFile)
		#self.menubar.add_command(label="Add Format", command=lambda: Item(master, ['', 'text1', ''], 3))
		#self.menubar.add_command(label="Generate .STK", command=(lambda: self.saveToFile()))
		self.master.config(menu=self.menubar)

	def createWindow(self):
		self.mainFrame = Canvas(width=680, height=400, bg="GREY")
		self.mainFrame.pack()
		self.fnButton = Button(self.mainFrame, text = '...', width = 3, command=self.openFile)
		self.svButton = Button(self.mainFrame, text = '...', width = 3, command=self.openOutputFile)
		self.svLabel = Text(self.mainFrame, height = 1, width = 24, wrap="none")
		self.fnLabel = Text(self.mainFrame, height = 1, width = 24, wrap="none")
		self.fnLabel.insert('1.0', 'Choose input file')
		self.fnLabel.config(state=DISABLED)
		self.svLabel.insert('1.0', 'Choose output file')
		self.svLabel.config(state=DISABLED)
		self.hdLabel = Label(self.mainFrame, text='Custom queries:', background = 'GREY')
		self.hdEntry = Text(self.mainFrame, height = 10, width = 20, background = '#424242', foreground = "#2195E7")
		#self.hdEntry.configure(encode = 'utf-8')
		self.hdButton = Checkbutton(self.mainFrame, text="Exclusive Mode", variable=self.hdButtonTick, background = 'GREY')
		self.countLabel = Label(self.mainFrame, text='0 / 0', background = 'GREY')
		self.strtButton = Button(self.mainFrame, text= "START", width = 8, command=self.runJobs, state=DISABLED)
		self.thLabel = Label(self.mainFrame, text='Threads:', background='GREY')
		self.thBox = ttk.Combobox(self.mainFrame, width = 2, textvariable = self.boxValue)
		self.thBox['values'] = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
		self.thBox.current(0)
		self.exButton = Button(self.mainFrame, text = 'EXPORT', width = 8, command=self.exportOutputFile, state=DISABLED)
		self.statLabel = Text(self.mainFrame, height = 10, width = 91, background = '#424242', state=DISABLED)
		self.statLabel.tag_config('OK', foreground='#08a83a')
		self.statLabel.tag_config('FAIL', foreground='#ff4444')
		self.statLabel.tag_config('NA', foreground='#2195E7')
		self.statLabel.tag_config('IN', foreground='#ce8b0e')

		self.fileButton = self.mainFrame.create_window(200, 20, anchor = NW, window = self.fnButton)
		self.fileName = self.mainFrame.create_window(22, 22, anchor = NW, window = self.fnLabel)
		self.savefileName = self.mainFrame.create_window(22, 52, anchor = NW, window = self.svLabel)
		self.saveButton = self.mainFrame.create_window(200, 50, anchor = NW, window = self.svButton)
		self.headerLabel = self.mainFrame.create_window(517, 22, anchor = NE, window = self.hdLabel)
		self.headerEntry = self.mainFrame.create_window(520, 20, anchor = NW, window = self.hdEntry)
		self.headerButton = self.mainFrame.create_window(565, 188, window = self.hdButton)
		self.counterLabel = self.mainFrame.create_window(664, 216, anchor = E, window = self.countLabel)
		self.startButton = self.mainFrame.create_window(22, 200, anchor = NW, window = self.strtButton)
		self.threadLabel = self.mainFrame.create_window(380, 22, anchor = NE, window=self.thLabel)
		self.threadBox = self.mainFrame.create_window(420, 20, anchor = NE, window = self.thBox)
		self.statusEntry = self.mainFrame.create_window(22, 230, anchor = NW, window = self.statLabel)
		self.exportButton = self.mainFrame.create_window(22, 82, anchor = NW, window = self.exButton)

	def exportOutputFile(self):
		if self.openSaveFile:
			with open(self.openSaveFile, 'w') as file:
				for i in Job.jobsResultsMain:
					print 'good results main: ' + i
					file.write((i + '\n').decode('windows-1250'))

				for i in Job.jobsResultsCustom:
					print 'good results custom: ' + i
					file.write((i + '\n').decode('windows-1250'))

			if Job.jobsResultsMainFailed or Job.jobsResultsCustomFailed:
				with open(self.openSaveFile.split('.')[0] + '_failed' + '.txt', 'w') as file:
					for i in Job.jobsResultsMainFailed:
						print 'failed results main: ' + i
						file.write((i + '\n').encode('windows-1250').decode('windows-1250'))

					for i in Job.jobsResultsCustomFailed:
						print 'failed results custom: ' + i
						file.write((i + '\n').decode('windows-1250'))

	def openFile(self):
		self.openFile = tkFileDialog.askopenfilename(filetypes = (('text files', '*.txt'),))
		if self.openFile:
			self.fnLabel.config(state=NORMAL)
			self.fnLabel.delete('1.0', END)
			self.fnLabel.insert('1.0', self.openFile)
			self.fnLabel.config(state=DISABLED)
			self.writeToLog('INPUT FILE OPEN: ' + self.openFile, 'NA')
			self.scanFile(self.openFile)

	def openOutputFile(self):
		self.openSaveFile = tkFileDialog.asksaveasfilename(filetypes = (('text files', '*.txt'),))
		if self.openSaveFile:
			if len(self.openSaveFile.split('.')) == 1:
				self.openSaveFile += '.txt'
			else:
				if self.openSaveFile.split('.')[-1] != 'txt':
					self.openSaveFile += '.txt'

			self.svLabel.config(state=NORMAL)
			self.svLabel.delete('1.0', END)
			self.svLabel.insert('1.0', self.openSaveFile)
			self.svLabel.config(state=DISABLED)

	def cleanLogLines(self, logLength):
		for i in range(logLength):
			# find longer than 91 chars and split
			if len(self.verifierLog[i][0]) > 91:
				string1 = ''
				print self.verifierLog[i][0]
				words = self.verifierLog[i][0][0: 91].split(' ')[0: -1]
				for word in words:
					string1 += word + ' '
				string1 = string1[:-1]

				string2 = '     ' + self.verifierLog[i][0][len(string1):]

				self.verifierLog.insert(i, (string2, self.verifierLog[i][-1]))
				self.verifierLog.insert(i, (string1, self.verifierLog[i][-1]))
				del (self.verifierLog[i + 2])

	def updateMainStates(self):
		#to screen log printing logic
		if self.verifierLog:
			if len(self.verifierLog) >= 10:
				self.cleanLogLines(10)
				self.statLabelFull = True
				self.statLabel.config(state=NORMAL)
				self.statLabel.delete('1.0', END)

				for i in range(10):

					if i == 9:
						self.statLabel.insert(END, self.verifierLog[i][0], self.verifierLog[i][1])

					else:
						self.statLabel.insert(END, self.verifierLog[i][0] + '\n', self.verifierLog[i][1])

				self.statLabel.config(state=DISABLED)
				self.logToFile(self.verifierLog[0][0])
				self.verifierLog.pop(0)

			else:
				self.cleanLogLines(len(self.verifierLog))
				if not self.statLabelFull:
					self.statLabel.config(state=NORMAL)
					self.statLabel.delete('1.0', END)
				for i in range(len(self.verifierLog)):
					self.statLabel.insert(END, self.verifierLog[i][0]  + '\n', self.verifierLog[i][1])
			self.statLabel.config(state=DISABLED)

		#job count label update
		if self.hdButtonTick.get():
			finalCounter = self.customCount
		else:
			finalCounter = self.totalCount + self.customCount

		self.countLabel.config(text=str(Verifier.verified) + ' / ' + str(finalCounter))

		#update button states
		if Job.jobsList and not self.taskActive:
			self.strtButton.config(state=NORMAL)

		elif not Job.jobsList and not self.taskActive:
			self.strtButton.config(state=DISABLED)

		elif self.taskActive:
			self.strtButton.config(state=DISABLED)

		else:
			self.strtButton.config(state=NORMAL)

		any = False

		for i in Job.jobsAllResults:
			if i:
				any = True
				break

		if any and not self.taskActive:
			self.exButton.config(state=NORMAL)

		else:
			self.exButton.config(state=DISABLED)

		# activating/deactivating logic for threads
		if self.taskActive:
			if Job.jobsList:

				activeThreads = 0
				for thread in Verifier.threads:
					if thread.active:
						activeThreads += 1

				if activeThreads > int(self.thBox.get()):
					toKeep = range(1, (activeThreads - (activeThreads - int(self.thBox.get()))) + 1)
					for thread in Verifier.threads:
						if thread.id in toKeep:
							pass
						else:
							thread.active = False

				elif activeThreads < int(self.thBox.get()):
					toActivate = range(activeThreads + 1, int(self.thBox.get()) + 1)
					for thread in Verifier.threads:
						if thread.id in toActivate:
							thread.active = True

			else:
				activeThreads = 0
				for thread in Verifier.threads:
					if thread.active:
						activeThreads += 1
				if not activeThreads:
					self.taskActive = False
		else:
			self.fnButton.config(state=NORMAL)
			self.hdButton.config(state=NORMAL)
			self.hdEntry.config(state=NORMAL)

			if self.verifierLog:
				for i in self.verifierLog:
					self.logToFile(i[0])
				self.verifierLog = []

		self.after(100, self.updateMainStates)

	def scanFile(self, file):
		importCount = 0
		emailCount = 0
		self.verifierLog = []
		if not Job.jobsList:
			self.totalCount = 0
			self.customCount = 0
			Verifier.verified = 0
		reload(sys)
		sys.setdefaultencoding("windows-1250")
		with codecs.open(file, 'r', "windows-1250") as plik:
			for email in plik.readlines():
				try:
					mail = email.encode('utf-8').rstrip().split('@')
					if len(mail) == 2:
						if len(mail[-1].split('.')) >= 2:
							host = mail[-1]
							account = mail[0].split(' ')[-1]
							self.writeToLog('Imported: ' + account + '@' + mail[-1], 'NA')
							importCount += 1
							if host in self.emailDir:
								#if domain already exists in the directory, add the additional account to the list. Only if it doesn't exist yet.
								if not [account, 'main', None] in self.emailDir[host]:
									self.emailDir[host].append([account, 'main', None])
									self.totalCount += 1
									emailCount += 1

							else:
								#if account/domain doesn't exist add a directory entry
								self.emailDir[host] = [[account, 'main', None]]
								self.totalCount += 1
								emailCount += 1

				except Exception:
					print 'wrong encoding'

		Job.jobsList = []

		for i in self.emailDir:
			Job(i, self.emailDir[i])

		self.writeToLog('Total e-mails recognised: ' + str(importCount) + ', total imported: ' + str(emailCount), 'OK')
		print self.emailDir

	def writeToLog(self, text, status):
		if len(self.log) >= 10:
			self.log.pop(0)

		self.log.append((text, status))
		self.logToFile(text)

		self.statLabel.config(state=NORMAL)
		self.statLabel.delete('1.0', END)
		for i in range(len(self.log)):

			if i == 9:
				self.statLabel.insert(END, self.log[i][0], self.log[i][1])

			else:
				self.statLabel.insert(END, self.log[i][0] + '\n', self.log[i][1])

		self.statLabel.config(state=DISABLED)
		self.master.update()

	def clearLog(self):
		self.log = []
		self.verifierLog = []
		self.statLabelFull = False
		self.statLabel.config(state=NORMAL)
		self.statLabel.delete('1.0', END)
		self.statLabel.config(state=DISABLED)

	def addCustom(self):
		queries = set([x for x in self.hdEntry.get('1.0', END).split('\n') if x != ''])
		if queries:
			self.writeToLog('Adding custom queries to jobs', 'OK')
			for job in Job.jobsList:
				for query in queries:
					query = query.encode('utf-8')
					print 'QUERY: ', query
					if not [query, 'main', None] in job.accounts:
						self.customCount += 1
						self.writeToLog('Added: ' + query + '@' + job.host, 'NA')
						job.accounts.append([query, 'custom', None])


	def runJobs(self):
		if Job.jobsList:
			Verifier.verified = 0
			self.emailDir = {}
			self.clearLog()
			Job.clearResults()
			self.addCustom()
			self.writeToLog('Batch e-mail verification process started.', 'OK')
			self.writeToLog('Initializing Threads.', 'OK')
			self.taskActive = True
			self.fnButton.config(state=DISABLED)
			self.hdButton.config(state=DISABLED)
			self.strtButton.config(state=DISABLED)
			self.hdEntry.config(state=DISABLED)

			if not Verifier.threads:
				for i in range(1, 11):
					thread = Verifier(i, self)
					thread.start()
					time.sleep(0.1)

	def logToFile(self, text):
		log = open(os.path.join(logFolder, logFile), 'a')
		log.write(text + '\n')
		log.close()

if __name__ == '__main__':
	root = Tk()
	app = MainWindow(root)
	app.master.title('E-mail Verifier')
	app.pack()
	root.update()
	if "favicon.ico" in os.listdir(os.getcwd()):
		root.iconbitmap(True, "favicon.ico")
	root.minsize(root.winfo_width(), root.winfo_height())
	root.resizable(False, False)
	app.mainloop()

	try:
		root.destroy()
	except:
		pass