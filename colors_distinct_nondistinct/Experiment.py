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

		# incongruent trials
		self.trial_settings = list()
		for prob in self.parameters['probability']:
			for k in range(prob):
				for templatepos in self.parameters['template_side']:
					for color in self.parameters['colors']:
						for searchtype in self.parameters['search_type']:
							for respos in self.parameters['response_pos']:
								if prob < 5:
									self.trial_settings.append(['incongruent',templatepos,color,searchtype,respos])
								else:
									self.trial_settings.append(['congruent',templatepos,color,searchtype,respos])


		shuffle(self.trial_settings)
		if self.parameters['ntrials'] is not 'all':
			self.trial_settings = self.trial_settings[0:self.parameters['ntrials']]
		else:
			self.parameters['ntrials'] = len(self.trial_settings)
		dbstop()

		self.trials = list()
		loadtext = visual.TextStim(self.screen, text = 'preloading trials, may take a while...', color = 'white', pos = (0, 0), height = 0.4)
		for setting in self.trial_settings:
			loadtext.draw()
			self.screen.flip()
			self.trials.append(Trial(setting,self.parameters,self.screen))

	def run(self):

		with open (self.parameters['ready_text'], "r") as myfile:
			text2show=myfile.read().replace('\n,', '\n')
		try: text2show = text2show.replace('NBLOCKS', str(self.parameters['nblocks']))
		except: pass
		try: text2show = text2show.replace('NTRIALS', str(len(self.trials)/self.parameters['nblocks']))
		except: pass
		text_screen = Text(self.parameters, self.screen, text2show)
		text_screen.show()

		expdata = list()
		sumacc = 0
		blocki = 0
		# for k, settings in enumerate(self.trial_settings):
		for k, trial in enumerate(self.trials):

			# trial = Trial(settings, self.parameters, self.screen)
			trialdata = trial.run()
			expdata.append(trialdata)
			sumacc = sumacc+trialdata[2][0]
			if fmod(k+1,len(self.trial_settings)/self.parameters['nblocks'])==0: # feedback after mini/practice block
				blocki = blocki + 1
				avgacc = round(float(sumacc)/float(len(expdata))*100.0)
				text2show = 'This was block ' + str(blocki) + ' of ' + str(self.parameters['nblocks']) + '\n\nYour accuracy was ' + str(avgacc) + '\n\nPress a button to continue'
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
