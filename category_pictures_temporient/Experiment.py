# Header
from Trial import *
from Text import *
import sys, datetime, os, glob
import pickle

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

		self.parameters['ntargets'] = self.parameters['ntrials'] / len(self.parameters['stimuli'])  # compute number of unique targets 
		
		self.trial_settings = list()
		for c,files in enumerate(self.parameters['stimuli']): # loop over categories
			category = self.parameters['categories'][c]
			files_c = deepcopy(files)
			shuffle(files_c)
			for target in files_c[0:self.parameters['ntargets']]: # within category, loop over unique pictures
				self.trial_settings.append([category,target,choice(self.parameters['absent_present']),choice(self.parameters['temp_prob'])])
		shuffle(self.trial_settings)

		# do a repetition check of present/absent sequences:
		chunck = self.parameters['rep_check'][0] # This divides a list of 300 in 10 chuncks of 30; this speeds up the shuffleAgain while-loop
		repeatCheck = self.parameters['rep_check'][1]  # How many repeats are not *allowed*
		chunckSeq = [chunck*k for k in range(len(self.trial_settings)/chunck+1)] 
		presence = list()
		for k in range(len(self.trial_settings)/chunck):
			while True:
				a = [trial[len(trial)-2] for trial in self.trial_settings[chunckSeq[k]:chunckSeq[k+1]]]
				shuffle(a)
				while True:
					if k and a[0] == presence[k-1][len(presence[k-1])-1]:
						shuffle(a)
					else:
						break
				shuffleAgain = False
				for i in range(len(a)-(repeatCheck-1)):
					slice = a[i:i+repeatCheck]
					if len(np.unique(slice)) == 1:
						shuffleAgain = True
				if not shuffleAgain:
					presence = presence + a
					break
		for i in range(len(self.trial_settings)):
			self.trial_settings[i][len(self.trial_settings[i])-2] = presence[i]

		# do a repetition check of long/short sequences in short block with 20% long trials
		repeatCheck = 2  # How many repeats are not *allowed*
		chunckSeq = [chunck*k for k in range(len(self.trial_settings)/chunck+1)] 
		longshort = list()
		for k in range(len(self.trial_settings)/chunck):
			while True:
				a = [trial[len(trial)-1] for trial in self.trial_settings[chunckSeq[k]:chunckSeq[k+1]]]
				shuffle(a)
				shuffleAgain = False
				for i in range(len(a)-(repeatCheck-1)):
					slice = a[i:i+repeatCheck]
					if sum(map(int,slice)) == 0:
						shuffleAgain = True
				if not shuffleAgain:
					longshort = longshort + a
					break		
		for i in range(len(self.trial_settings)):
			self.trial_settings[i][len(self.trial_settings[i])-1] = longshort[i]

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
			sumacc = sumacc+trialdata[5]
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
