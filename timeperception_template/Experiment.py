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

		# 200 time perception trials
		self.trial_settings = list()
		for typeprobe in self.parameters['probe_type']:
			for probedur in self.parameters['timing_probe_Duration']: 
				self.trial_settings.append([typeprobe,probedur,choice(self.parameters['color_combs'])])

		# 600 search trials
		for block in range(self.parameters['nblocks']):
			for colcomb in self.parameters['color_combs']:
				self.trial_settings.append(['none',0,colcomb]) # change this to 'none' and 0

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
		sumacc = 0
		blocki = 0
		for k, settings in enumerate(self.trial_settings):

			trial = Trial(settings, self.parameters, self.screen)
			trialdata = trial.run()
			expdata.append(trialdata)
			# sumacc = sumacc+trialdata[5]
			# if fmod(k+1,len(self.trial_settings)/self.parameters['nblocks'])==0: # feedback after mini/practice block
			# 	blocki = blocki + 1
			# 	avgacc = round(float(sumacc)/float(len(expdata))*100.0)
			# 	text2show = 'This was block ' + str(blocki) + ' of ' + str(self.parameters['nblocks']) + '\n\nYour accuracy was ' + str(avgacc) + '\n\nPress a button to continue'
			# 	text_screen = Text(self.parameters, self.screen, text2show)
			# 	text_screen.show()

		self._finished = True
		self.output = expdata

	#### functions for task instruction ###

	def run_instruction(self, text_file_path = ''):
		with open (text_file_path, "r") as myfile:
			text2show=myfile.read().replace('\n,', '\n')
		text_screen = Text(self.parameters, self.screen, text2show)
		text_screen.show()
                                        
	def run_example_trial(self, trial_parameters = list()):
	 	examp_trial = Trial(np.array(trial_parameters), self.parameters, self.screen) # example trial
	 	examp_trial.run()

	### administrative functions ###

	def set_output_filename(self):
		now = datetime.datetime.now()
		opfn = now.strftime("%Y%m%d_%H%M")
		if not os.path.isdir(self.parameters['data_directory']):
			os.mkdir(self.parameters['data_directory'])
		self.output_file = os.path.join(self.parameters['data_directory'], self.parameters['subject_id'] + '_' + self.parameters['block_type'] + '_' + opfn + '.p' )

	def finished(self):
		return self._finished

	def store(self, filename = ''):
		if len(filename)==0:
			filename = self.output_file
		# save the data
		with open(filename, 'wb') as f:
			pickle.dump(self.output, f)	


### END
