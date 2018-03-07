from Tkinter import *
import tkFileDialog
import os
globFont = "Verdana 8 bold"

class EntryBox(object):
	def __init__(self, layer, row, column):
		self.entry = Entry(layer, width = 50, bg = 'grey')
		self.entry.grid(row = row, column = column)



class Main_Window(Frame):
	def __init__(self, master):
		Frame.__init__(self, master, relief=SUNKEN, bd=2)
		self.hdEntryText = 'sadas'
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
		self.fnButton = Button(self.mainFrame, text = 'Wybierz plik wsadowy', anchor = W, command=self.openFile)
		self.fnLabel = Label(self.mainFrame, text='...', anchor = W)
		self.hdLabel = Label(self.mainFrame, text='Dodatkowe zapytania:', anchor = W)
		self.hdEntry = Text(self.mainFrame, height = 10, width = 20, background = '#424242', foreground = "#2195E7")
		self.statLabel = Text(self.mainFrame, height = 10, width = 91, background = '#424242', foreground = "#2195E7", state=DISABLED)
		#self.fnLabel.configure(relief = FLAT)
		self.fileButton = self.mainFrame.create_window(20, 20, anchor = NW, window = self.fnButton)
		self.fileName = self.mainFrame.create_window(150, 22, anchor = NW, window = self.fnLabel)
		self.headerLabel = self.mainFrame.create_window(400, 22, anchor = NW, window = self.hdLabel)
		self.headerEntry = self.mainFrame.create_window(520, 22, anchor = NW, window = self.hdEntry)
		self.statusEntry = self.mainFrame.create_window(22, 230, anchor = NW, window = self.statLabel)

	def openFile(self):
		self.openFile = tkFileDialog.askopenfilename(filetypes = (('text files', '*.txt'),))
		if self.openFile:
			self.fnLabel.config(text = '...' + self.openFile.split('/')[-1])
			print self.hdEntry.get('1.0', END)
			self.writeToLog('Otworzono plik wsadowy: ' + self.openFile)
			self.scanFile(self.openFile)

	def scanFile(self, file):
		with open(file, 'r') as plik:
			for email in plik.readlines():
				try:
					mail = email.rstrip().split('@')
					if len(mail) == 2:
						if len(mail[-1].split('.')) >= 2:
							self.writeToLog('Zaimportowano: ' + email.rstrip())
							if mail[-1] in self.emailDir:
								#if domain already exists in the directory, add the additional account to the list. Only if it doesn't exist yet.
								if not mail[0] in self.emailDir[mail[-1]][0]:
									self.emailDir[mail[-1]][0].append(mail[0])
							else:
								#if account/domain doesn't exist add a directory entry
								self.emailDir[mail[-1]] = ([mail[0]], [])

				except Exception:
					print 'something went wrong'

		print self.emailDir

	def writeToLog(self, text):
		if len(self.log) >= 10:
			self.log.pop(0)

		self.log.append(text)
		self.statLabel.config(state=NORMAL)
		self.statLabel.delete('1.0', END)
		for i in range(len(self.log)):
			if i == 9:
				self.statLabel.insert(END, self.log[i])
			else:
				self.statLabel.insert(END, self.log[i] + '\n')
		self.statLabel.config(state=DISABLED)

	def updateStat(self):
		pass

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
	app.master.title('Mail-Checker')
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