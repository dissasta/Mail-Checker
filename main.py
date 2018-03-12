# -*- coding: utf-8 -*-
from Tkinter import *
from job import *
from verifier import *
import tkFileDialog
import os
import sys
import codecs
import time
import ttk
import threading
from datetime import datetime

globFont = "Verdana 8 bold"
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
		self.taskActive = False
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
		self.hdButton = Checkbutton(self.mainFrame, text="Exclusive Mode", variable=self.hdButtonTick, background = 'GREY')
		self.countLabel = Label(self.mainFrame, text='0 / 0', background = 'GREY')
		self.strtButton = Button(self.mainFrame, text= "START", width = 8, command=self.runJobs, state=DISABLED)
		self.thLabel = Label(self.mainFrame, text='Threads:', background='GREY')
		self.thBox = ttk.Combobox(self.mainFrame, width = 2, textvariable = self.boxValue)
		self.thBox['values'] = (1, 2, 3, 4, 5, 6)
		self.thBox.current(0)
		self.exButton = Button(self.mainFrame, text = 'EXPORT', width = 8, command=self.exportOutputFile, state=DISABLED)
		self.statLabel = Text(self.mainFrame, height = 10, width = 91, background = '#424242', state=DISABLED)
		self.statLabel.tag_config('OK', foreground='GREEN')
		self.statLabel.tag_config('WARN', foreground='RED')
		self.statLabel.tag_config('NA', foreground='#2195E7')

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
		for i in Job.jobsResultsMain:
			print 'good results main: ' + i

		for i in Job.jobsResultsMainFailed:
			print 'failed results main: ' + i

		for i in Job.jobsResultsCustom:
			print 'good results custom: ' + i

		for i in Job.jobsResultsCustomFailed:
			print 'failed results custom: ' + i

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
		self.openOutputFile = tkFileDialog.asksaveasfilename(filetypes = (('text files', '*.txt'),))

		if self.openOutputFile:
			if len(self.openOutputFile.split('.')) == 1:
				self.openOutputFile += '.txt'
			else:
				if self.openOutputFile.split('.')[-1] != 'txt':
					self.openOutputFile += '.txt'

			self.svLabel.config(state=NORMAL)
			self.svLabel.delete('1.0', END)
			self.svLabel.insert('1.0', self.openOutputFile)
			self.svLabel.config(state=DISABLED)

			print self.openOutputFile

	def updateMainStates(self):
		#to screen log printing logic
		if self.verifierLog:
			self.statLabel.config(state=NORMAL)
			self.statLabel.delete('1.0', END)
			if len(self.verifierLog) >= 11:

				#self.logToFile(text)

				for i in range(10):

					if i == 9:
						self.statLabel.insert(END, self.verifierLog[i][0], self.verifierLog[i][1])

					else:
						self.statLabel.insert(END, self.verifierLog[i][0] + '\n', self.verifierLog[i][1])

				self.statLabel.config(state=DISABLED)
				self.verifierLog.pop(0)

			else:
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
				self.taskActive = False
		else:
			self.fnButton.config(state=NORMAL)
			self.hdButton.config(state=NORMAL)
			self.hdEntry.config(state=NORMAL)

		self.after(10, self.updateMainStates)

	def scanFile(self, file):
		print 'scanning'
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
								if not account in self.emailDir[host]:
									self.emailDir[host].append(account)
									self.totalCount += 1

							else:
								#if account/domain doesn't exist add a directory entry
								self.emailDir[host] = [account]
								self.totalCount += 1

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
		self.statLabel.config(state=NORMAL)
		self.statLabel.delete('1.0', END)
		self.statLabel.config(state=DISABLED)

	def addCustom(self):
		queries = [x for x in self.hdEntry.get('1.0', END).split('\n') if x != '']
		print queries
		if queries:
			self.writeToLog('Adding custom queries to jobs', 'OK')

			for job in Job.jobsList:
				for query in queries:
					if not query in job.accounts and not query in job.custom:
						self.customCount += 1
						time.sleep(0.01)
						self.writeToLog('Added: ' + query + '@' + job.host, 'NA')
						job.custom.append(query)

	def runJobs(self):
		if Job.jobsList:
			Verifier.verified = 0
			self.emailDir = {}
			self.clearLog()
			Job.clearResults()
			self.fnButton.config(state=DISABLED)
			self.hdButton.config(state=DISABLED)
			self.strtButton.config(state=DISABLED)
			self.hdEntry.config(state=DISABLED)
			self.addCustom()
			self.writeToLog('Batch e-mail verification process started.', 'OK')

			self.taskActive = True

			if not Verifier.threads:
				for i in range(1, 7):
					thread = Verifier(i, self)
					thread.start()
					time.sleep(0.3)

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