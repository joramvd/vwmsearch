# Header
import numpy as np
from psychopy import visual, event, core, parallel, monitors #  
from math import pi, cos, sin, floor, fmod
from random import randrange, shuffle, choice, random, getrandbits
from copy import deepcopy
from IPython import embed as dbstop

# Class
class Trial(object):
	"""base class for Trials"""
	def __init__(self, trial_settings = {}, parameters = {}, screen = None):

		self.block = parameters['block_type']
		self.category = trial_settings[0]
		self.target = trial_settings[1]
		self.presence = trial_settings[2]
		try:
			self.temp_prob = int(trial_settings[3])
		except: pass
		self.trial_settings = trial_settings
		self.parameters = parameters
		self.screen = screen

		self.searchStim = list()
		self.feedbackStim = list()
		self.response = list()
		self.button = None
		self.keypress = None
		self.missing = False
		self.randpos = 0

		self.make_searchTarget()
		self.make_searchArray()
		self.make_fixation()
		self.make_feedback()

		self.timer = core.Clock()

	def make_fixation(self):
		self.fixStim = visual.Circle(self.screen, radius = 0.08, fillColor = [1,1,1])

	def make_searchTarget(self):
		# This is the target
		self.targetStim = visual.ImageStim(self.screen, image=self.target, pos = (0,0))
		self.targetStim.size /= self.parameters['cue_stim_size']

	def make_searchArray(self):
		# copy, shuffle the stim category list with filenames, and remove target
		# for target-present trials, put the target back in first position shuffled list

		getPics = deepcopy(self.parameters['stimuli'])
		for k,cat in enumerate(getPics): 

			if k==0: # if stimset is faces then shuffle a subset of same gender as target, for search array
				# determine gender
				if self.target[len(self.target)-16]=='F':
					cat = cat[0:50] # subselect female faces
				else:
					cat = cat[50:100] # subselect male faces
				shuffle(cat)

			elif k==2: # if stimset is letters then shuffle a subset of same letters, same capitalization, from different font, for search array
				if self.category=='letter':
					whichletter = int(self.target[len(self.target)-13:len(self.target)-11])
				else:
					whichletter = choice(range(25))
				cat = cat[whichletter*4-4:whichletter*4]
				shuffle(cat)
			else:
				shuffle(cat)

			try: 
				cat.remove(self.target) # remove the target filename
				if 'present' in self.presence: 
					cat[0] = self.target
			except: pass
			getPics[k] = cat

		## Fill up search array
		search_array = [k for c in getPics for k in c[0:self.parameters['search_set_size']/len(getPics)]]
		self.randpos = range(self.parameters['search_set_size']); shuffle(self.randpos) # n positions of n-search-array, randomized

		for k, searchPic in enumerate(search_array):
			self.searchStim.append(visual.ImageStim(self.screen, image=searchPic, pos = (self.parameters['search_radius']*cos(self.parameters['search_angle']*(self.randpos[k]+1)+self.parameters['search_angle']/2), self.parameters['search_radius']*sin(self.parameters['search_angle']*(self.randpos[k]+1)+self.parameters['search_angle']/2)*-1)))
			self.searchStim[k].size /= self.parameters['search_stim_size']

	def make_feedback(self):
		self.feedbackStim.append(visual.TextStim(self.screen,text='wrong...',pos=(0.0,0), height=0.6))
		self.feedbackStim.append(visual.TextStim(self.screen,text='correct!',pos=(0.0,0), height=0.6))
		self.feedbackStim.append(visual.TextStim(self.screen,text='respond faster!',pos=(0.0,0), height=0.6))

	def run(self):

		portOut = self.parameters['ports'][0]
		portIn = self.parameters['ports'][1]

		iti_time    = int(floor(float(self.parameters['timing_ITI_Duration']) * float(self.parameters['monitor_refRate'])))
		iti_jitt    = int(floor(float(self.parameters['timing_ITI_Jitter']) * float(self.parameters['monitor_refRate'])))
		target_time = int(floor(float(self.parameters['timing_target_Duration']) * float(self.parameters['monitor_refRate'])))

		# in principle, the trial type is the same as the block type
		# the block with short delays has a long delay in 20% of the trials
		if self.block == 'short' and self.temp_prob==0:
			self.trial_type = 'long'
		elif self.block == 'practice':
			self.trial_type = choice(['short','long'])
		else:
			self.trial_type = self.block

		if   self.trial_type == 'short': toggle = 0
		elif self.trial_type == 'long': toggle = 1

		# example trials during intruction have short/long hard-coded as arguments
		if   'short' in self.trial_settings: toggle = 0
		elif 'long'  in self.trial_settings: toggle = 1

		isi_time = int(floor(float(self.parameters['timing_ISI_Duration'][toggle]) * float(self.parameters['monitor_refRate'])))

		# Change fixation to white to start ITI with jitter
		for frame in range(iti_time + randrange(-1*iti_jitt, iti_jitt)): 
			self.fixStim.fillColor=[1,1,1]
			self.fixStim.lineColor=[1,1,1]
			self.fixStim.draw()
			self.screen.flip()

		# Present search-target stimulus
		if portOut:
			portOut.setData(int(self.parameters['triggers'][self.block]+self.parameters['triggers'][self.trial_type]+self.parameters['triggers'][self.category])); core.wait(0.02) # code for category (1,2,3) and short/long/practice block type (+ 60/70/80)
			portOut.setData(0)
		else:
			print(int(self.parameters['triggers'][self.block]+self.parameters['triggers'][self.trial_type]+self.parameters['triggers'][self.category]))
		for frame in range(target_time):
			self.targetStim.draw()
			self.fixStim.draw()
			self.screen.flip()

		# ISI
		for frame in range(isi_time):
			self.fixStim.draw()
			self.screen.flip()

		# Present search array stimulus until response
		if portOut:
			portOut.setData(int((self.parameters['triggers'][self.presence]*(self.randpos[0]+1))+10)); core.wait(0.02) # code for stimulus position in array (1-6; 0 when absent) 
			portOut.setData(0)
		else:
			print(int((self.parameters['triggers'][self.presence]*(self.randpos[0]+1))+10))

		self.timer.reset()
		while True:
			for currStim in self.searchStim: currStim.draw()
			self.fixStim.draw()
			self.screen.flip()
			if portIn:
				self.button = portIn.readData()
				for key in event.getKeys():
					self.keypress = key
			else:
				for key in event.getKeys():
					self.button = key
					self.keypress = key

			# to pause/quit the experiment, press p/q
			if self.keypress=='p':
				continue
			elif self.keypress=='q':
				quit()			
			# otherwise, or to resume a pause, an appropriate button has to be pressed
			elif self.button in self.parameters['resp_keys']:
				rt=self.timer.getTime()
				break
			# if not paused, and no button is pressed, next trial after 5 seconds
			elif self.timer.getTime() > 5.0:
				self.button=None
				self.missing=True
				rt=0.0
				break

		self.response = [self.button,rt]

		# determine accuracy
		if ('present' in self.presence and self.response[0] == self.parameters['resp_keys'][0]) or ('absent' in self.presence and self.response[0] == self.parameters['resp_keys'][1]):
			accuracy = 1
		else: 
			accuracy = 0

		# Present feedback after response
		if self.missing:
			for frame in range(iti_jitt):
				self.feedbackStim[2].draw()
				self.screen.flip()
		elif self.block=='practice':
			for frame in range(iti_jitt):
				self.feedbackStim[accuracy].draw()
				self.screen.flip()
		else:
			# Present black fixation point right after self.button press of previous trial
			for frame in range(iti_jitt): 
				self.fixStim.fillColor=[-1,-1,-1]
				self.fixStim.lineColor=[-1,-1,-1]
				self.fixStim.draw()
				self.screen.flip()

		return ([self.block, self.trial_type, self.category, self.presence, self.response[1], accuracy])


	#def export(self):
	#	return np.concatenate([self.trial_settings.copy(), self.response.copy()])

