# Header
from Trial import *
from Text import *

# Class
class Experiment(object):

	def __init__(self, parameters = {}):

		self.parameters = parameters.copy()
		self.screen = self.parameters['screen']
		self.setup_trials()
		self.set_output_filename()
		self._finished = False
		self.output = list()

	def setup_trials(self):

		self.trial_settings = list()
		k=0
		for q in range(self.parameters['ntrials']/len(self.parameters['trial_type'])):
			for trialtype in self.parameters['trial_type']:
					self.trial_settings.append([trialtype,self.parameters['task_type'],self.parameters['timing_probe_Duration'][k],self.parameters['block_type']])
					k=k+1
		shuffle(self.trial_settings)

	def run(self):

		with open (self.parameters['ready_text'], "r") as myfile:
			text2show=myfile.read().replace('\n,', '\n')
		try: text2show = text2show.replace('NBLOCKS', str(self.parameters['nblocks']))
		except: pass
		try: text2show = text2show.replace('NTRIALS', str(len(self.trial_settings)/self.parameters['nblocks']))
		except: pass
		text_screen = Text(self.parameters, self.screen, text2show)
		text_screen.show()

		expdata = list()
		sumacc_mem = list()
		sumacc_tim = list()
		blocki = 0
		for k, settings in enumerate(self.trial_settings):

			trial = Trial(settings, self.parameters, self.screen)
			trialdata = trial.run()
			expdata.append(trialdata)

			if 'mem' in settings:
				sumacc_mem.append(trialdata[2][0])
			elif 'timing' in settings:
				sumacc_tim.append(trialdata[2][0])

			if fmod(k+1,len(self.trial_settings)/self.parameters['nblocks'])==0: # feedback after mini/practice block
				blocki = blocki + 1
				dbstop()
				avgacc_mem = round(float(np.mean(np.asarray(sumacc_mem)))*100.0)
				avgacc_tim = float(np.mean(np.asarray(sumacc_tim)))
				if avgacc_tim < 0.25:
					timefb = 'underestimated'
				elif avgacc_tim > 0.25:
					timefb = 'overestimated'
				else:
					timefb = 'correctly estimated'

				text2show = ('This was block ' + str(blocki) + ' of ' + str(self.parameters['nblocks']) + 
							 '\n\nYour memory/search accuracy was ' + str(avgacc_mem) + 
							 '\n\nOn average you ' + timefb + ' the delays' + 
							 '\n\nPress a button to continue')
				text_screen = Text(self.parameters, self.screen, text2show)
				text_screen.show()

		self._finished = True
		self.output = expdata

	#### functions for task instruction ###

	def run_instruction(self, text_file_path = ''):
		with open (text_file_path, "r") as myfile:
			text2show=myfile.read().replace('\n,', '\n')
		text_screen = Text(self.parameters, self.screen, text2show)
		text_screen.show()
                                        
	def run_example_trial(self, trial_parameters = list()):
	 	examp_trial = Trial(trial_parameters, self.parameters, self.screen) # example trial
	 	examp_trial.run()

	### administrative functions ###

	def set_output_filename(self):
		now = datetime.datetime.now()
		opfn = now.strftime("%Y%m%d_%H%M")
		if not os.path.isdir(self.parameters['data_directory']):
			os.mkdir(self.parameters['data_directory'])
		self.output_file = os.path.join(self.parameters['data_directory'], self.parameters['subject_id'] + '_' + self.parameters['task_type'] + '_' + opfn + '.p' )

	def finished(self):
		return self._finished

	def store(self, filename = ''):
		if len(filename)==0:
			filename = self.output_file
		# save the data
		with open(filename, 'wb') as f:
			pickle.dump(self.output, f)	


### END
