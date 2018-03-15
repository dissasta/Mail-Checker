class Job(object):
	jobsList = []
	jobsCount = 1
	jobsResultsMain = []
	jobsResultsCustom = []
	jobsResultsMainFailed = []
	jobsResultsCustomFailed = []
	jobsAllResults = [jobsResultsMain, jobsResultsCustom, jobsResultsMainFailed, jobsResultsCustomFailed]

	def __init__(self, host, accounts):
		self.host = host
		self.accounts = accounts
		self.custom = []
		self.mx = []
		self.done = False
		self.active = False
		self.id = Job.jobsCount
		self.connected = False
		self.status = None
		self.mxServer = None
		self.greeted = False
		self.mailFrom = False
		self.replies = []
		self.relayAllowed = True
		self.serverResponsive = None

		Job.jobsList.append(self)
		Job.jobsCount += 1

	@staticmethod
	def clearResults():
		Job.jobsResultsMain = []
		Job.jobsResultsCustom = []
		Job.jobsResultsMainFailed = []
		Job.jobsResultsCustomFailed = []
		Job.jobsAllResults = [Job.jobsResultsMain, Job.jobsResultsCustom, Job.jobsResultsMainFailed, Job.jobsResultsCustomFailed]