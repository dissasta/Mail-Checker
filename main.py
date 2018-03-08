from Tkinter import *
import tkFileDialog
import os
import time
from datetime import datetime

globFont = "Verdana 8 bold"
logFolder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LOGS')
logFile = str(datetime.now().strftime('%Y-%m-%d %H.%M.%S')) + ' LOG.txt'

class Verifier(object):
	def __init__(self, id):
		self.id = id
		self.active = False
		self.myJob = None

	def getMXRecords(self):
		pass

	def connect(self):
		pass


class Job(object):
	jobsList = []
	def __init__(self, host, accounts):
		self.host = host
		self.accounts = accounts
		self.custom = []
		self.done = False
		Job.jobsList.append(self)

class Main_Window(Frame):
	if not os.path.exists(logFolder):
		os.mkdir(logFolder)

	def __init__(self, master):
		Frame.__init__(self, master, relief=SUNKEN, bd=2)
		self.master = master
		self.hdEntryText = ''
		self.hdButtonTick = BooleanVar()
		self.log = []
		self.rows = 1
		self.emailDir = {}
		self.createMenus()
		self.createWindow()

	def createMenus(self):
		self.menubar = Menu(self)
		menu = Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label="File", menu=menu)
		menu.add_command(label="Exit", command=self.quit)
		menu.add_command(label="Open File", command=self.openFile)
		#self.menubar.add_command(label="Add Format", command=lambda: Item(master, ['', 'text1', ''], 3))
		self.menubar.add_command(label="Generate .STK", command=(lambda: self.saveToFile()))
		self.master.config(menu=self.menubar)

	def createWindow(self):
		self.mainFrame = Canvas(width=680, height=400, bg="GREY")
		self.mainFrame.pack()
		self.fnButton = Button(self.mainFrame, text = 'Choose input file', anchor = W, command=self.openFile)
		self.svButton = Button(self.mainFrame, text = 'Choose output file', anchor = W, command=self.openOutputFile)
		self.svLabel = Label(self.mainFrame, text='...', anchor = W, background = 'GREY')
		self.fnLabel = Label(self.mainFrame, text='...', anchor = W, background = 'GREY')
		self.hdLabel = Label(self.mainFrame, text='Additional queries:', anchor = W, background = 'GREY')
		self.hdEntry = Text(self.mainFrame, height = 10, width = 20, background = '#424242', foreground = "#2195E7")
		self.hdButton = Checkbutton(self.mainFrame, text="Exclusive Mode", variable=self.hdButtonTick, background = 'GREY')
		self.countLabel = Label(self.mainFrame, text='1000 / 1000', anchor = E, background = 'GREY')
		self.strtButton = Button(self.mainFrame, text= "START", anchor = W, command=self.runJobs)
		self.statLabel = Text(self.mainFrame, height = 10, width = 91, background = '#424242', state=DISABLED)
		self.statLabel.tag_config('OK', foreground='GREEN')
		self.statLabel.tag_config('WARN', foreground='RED')
		self.statLabel.tag_config('NA', foreground='#2195E7')

		self.fileButton = self.mainFrame.create_window(22, 20, anchor = NW, window = self.fnButton)
		self.fileName = self.mainFrame.create_window(125, 22, anchor = NW, window = self.fnLabel)
		self.savefileName = self.mainFrame.create_window(125, 52, anchor = NW, window = self.svLabel)
		self.saveButton = self.mainFrame.create_window(22, 50, anchor = NW, window = self.svButton)
		self.headerLabel = self.mainFrame.create_window(420, 22, anchor = NW, window = self.hdLabel)
		self.headerEntry = self.mainFrame.create_window(520, 22, anchor = NW, window = self.hdEntry)
		self.headerButton = self.mainFrame.create_window(570, 190, window = self.hdButton)
		self.counterLabel = self.mainFrame.create_window(650, 220, anchor = E, window = self.countLabel)
		self.startButton = self.mainFrame.create_window(22, 200, anchor = NW, window = self.strtButton)
		self.statusEntry = self.mainFrame.create_window(22, 230, anchor = NW, window = self.statLabel)

	def openFile(self):
		self.openFile = tkFileDialog.askopenfilename(filetypes = (('text files', '*.txt'),))
		if self.openFile:
			self.fnLabel.config(text = '...' + self.openFile.split('/')[-1])
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

			self.svLabel.config(text = '...' + self.openOutputFile.split('/')[-1])

			print self.openOutputFile


	def scanFile(self, file):
		importCount = 0
		emailCount = 0
		with open(file, 'r') as plik:
			for email in plik.readlines():
				try:
					mail = email.rstrip().split('@')
					if len(mail) == 2:
						if len(mail[-1].split('.')) >= 2:
							account = mail[0].split(' ')[-1]
							self.writeToLog('Imported: ' + account + '@' + mail[-1], 'NA')
							importCount += 1
							if mail[-1] in self.emailDir:
								#if domain already exists in the directory, add the additional account to the list. Only if it doesn't exist yet.
								if not mail[0] in self.emailDir[mail[-1]][0]:
									self.emailDir[mail[-1]][0].append(account)
									emailCount += 1
							else:
								#if account/domain doesn't exist add a directory entry
								self.emailDir[mail[-1]] = ([account], [])
								emailCount += 1

				except Exception:
					print 'something went wrong'

		Job.jobsList = []

		for i in self.emailDir:
			Job(i, self.emailDir[i][0])

		if self.hdButtonTick.get():
			self.addCustom()

		self.writeToLog('Total emails recognised: ' + str(importCount) + ', total imported: ' + str(emailCount), 'OK')
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
		#time.sleep(0.001)
		self.master.update()

	def addCustom(self):
		queries = [x for x in self.hdEntry.get('1.0', END).split('\n') if x != '']

		for job in Job.jobsList:
			for query in queries:
				if not query in job.accounts:
					job.custom.append(query)

	def runJobs(self):
		self.fnButton.config(state=DISABLED)
		self.hdButton.config(state=DISABLED)
		self.strtButton.config(state=DISABLED)
		self.hdEntry.config(state=DISABLED)



	def updateCounter(self, current, total):
		self.countLabel.config(text = current + '/' + total)
		self.master.update()

	def logToFile(self, text):
		log = open(os.path.join(logFolder, logFile), 'a')
		log.write(text + '\n')
		log.close()

	def saveToFile(self):
		f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".stk")
		if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
			return
		allInputs = []

		count = 0
		for i in Item.items:
			allInputs.append([])
			for x in i.inputs:
				allInputs[count].append(x.entry.get())
			count += 1


if __name__ == '__main__':
	root = Tk()
	app = Main_Window(root)
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