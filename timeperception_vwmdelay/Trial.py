# Header
import numpy as np
import scipy.stats as stats
import sys, datetime, os, glob
import pickle
from psychopy import visual, event, core, parallel, monitors, iohub
from math import pi, cos, sin, floor, fmod
from random import randrange, shuffle, choice, random, getrandbits
from IPython import embed as dbstop
from copy import deepcopy

# Class
class Trial(object):
	"""base class for Trials"""
	def __init__(self, trial_settings = {}, parameters = {}, screen = None):

		self.trial_settings = trial_settings
		self.parameters = parameters
		self.screen = screen

		self.targetStim = list()
		self.searchStim = list()
		self.probeStim = list()
		self.feedbackStim = list()
		self.response = list()
		self.accuracy = list()

		self.button = None
		self.keypress = None
		self.missing = False
		self.randpos = 0
		self.start_timer = False

		self.make_searchTarget()
		self.make_searchArray()
		self.make_Probe()
		self.make_fixation()
		self.make_feedback()

		self.timer = core.Clock()

	def make_fixation(self):
		self.fixStim = visual.Circle(self.screen, radius = 0.08, fillColor = [1,1,1])

	def make_searchTarget(self):
		tmp_ori = deepcopy(self.parameters['search_stim_ori'])
		self.array_ori = [x+choice([-1,1])*(random()*10) for x in tmp_ori]
		shuffle(self.array_ori)

		# memcue orientation
		# if 'novwm' in self.trial_settings:
		# 	self.gabor_ori = 0
		# else:
		self.gabor_ori = self.array_ori[0]

		# make gabor
		self.targetStim.append(visual.GratingStim(self.screen, ori=self.gabor_ori, pos = (0,0),tex="sin",mask="gauss",sf=3,size=self.parameters['cue_stim_size']))		

		# surrounding ring codes for task type
		# self.targetStim.append(visual.Circle(self.screen, radius=self.parameters['ring_stim_size'], pos = (0,0), fillColor = None, lineColor=self.parameters['ring_color'],lineWidth=self.parameters['ring_line_width']))
		# # dashed (search) or dotted (recogn)
		# if 'search' in self.trial_settings:
		# 	for ori in self.parameters['ring_dash_ori']:
		# 		self.targetStim.append(visual.Rect(self.screen, ori=ori, pos = (0,0), width=.3, height=self.parameters['ring_dash_length'], fillColor=self.parameters['screenBackground'],lineColor=None))
		# elif 'recognition' in self.trial_settings:
		# 	for ori in self.parameters['ring_dot_ori']:
		# 		self.targetStim.append(visual.Rect(self.screen, ori=ori, pos = (0,0), width=.3, height=self.parameters['ring_dash_length'], fillColor=self.parameters['screenBackground'],lineColor=None))

	def make_Probe(self):		
		self.probeStim = visual.Circle(self.screen, radius = 0.16, fillColor = None, lineColor = [1,1,1])
			
	def make_searchArray(self):

		if 'recognition' in self.trial_settings:
			self.recog_ori = choice([random()*180,self.gabor_ori])
			self.searchStim.append(visual.GratingStim(self.screen, ori=self.recog_ori, pos = (0,0),tex="sin",mask="gauss",sf=3,size=self.parameters['cue_stim_size']))
		else:
			self.randpos = range(self.parameters['search_set_size'])
			shuffle(self.randpos) # n positions of n-search-array, randomized

			if 'novwm' in self.trial_settings:
				while True:
					shuffle(self.randpos) # n positions of n-search-array, randomized
					# make sure the first two are on the same side
					if self.randpos[0] == 1 or self.randpos[0] == 0 or self.randpos[0] == 5:
						if not(self.randpos[1] == 2 or self.randpos[1] == 3 or self.randpos[1] == 4):
							break
					elif self.randpos[1] == 2 or self.randpos[1] == 3 or self.randpos[1] == 4:
						if not(self.randpos[1] == 1 or self.randpos[1] == 0 or self.randpos[1] == 5):
							break
				self.array_ori[1] = self.array_ori[0] # make the first two orientations similar
				print self.array_ori
				print self.randpos

			for k,ori_j in enumerate(self.array_ori):
				arrpos = [self.parameters['search_radius']*cos(self.parameters['search_angle']*(self.randpos[k])), self.parameters['search_radius']*sin(self.parameters['search_angle']*(self.randpos[k]))]
				self.searchStim.append(visual.GratingStim(self.screen, ori=ori_j, pos = arrpos,tex="sin",mask="gauss",sf=3,size=self.parameters['cue_stim_size']))

	def make_feedback(self):
		self.feedbackStim.append(visual.TextStim(self.screen,text='wrong...',pos=(0.0,0), height=0.6))
		self.feedbackStim.append(visual.TextStim(self.screen,text='correct!',pos=(0.0,0), height=0.6))
		self.feedbackStim.append(visual.TextStim(self.screen,text='respond earlier next time',pos=(0.0,0), height=0.6))
		self.feedbackStim.append(visual.TextStim(self.screen,text='too early...',pos=(0.0,0), height=0.6))
		self.feedbackStim.append(visual.TextStim(self.screen,text='about right!',pos=(0.0,0), height=0.6))
		self.feedbackStim.append(visual.TextStim(self.screen,text='too late...',pos=(0.0,0), height=0.6))

	def run(self):

		iti_time    = int(floor(float(self.parameters['timing_ITI_Duration']) * float(self.parameters['monitor_refRate'])))
		iti_jitt    = int(floor(float(self.parameters['timing_ITI_Jitter']) * float(self.parameters['monitor_refRate'])))
		target_time = int(floor(float(self.parameters['timing_target_Duration']) * float(self.parameters['monitor_refRate'])))
		tmp_probedur = [x for x in set(self.parameters['timing_probe_Duration']) if np.any(np.array(self.trial_settings,dtype=object)==x)]
		self.delay_dur = int(floor(float(tmp_probedur[0]) * float(self.parameters['monitor_refRate'])))
		self.delay_val = tmp_probedur[0]		

		# Change fixation to white to start ITI with jitter
		for frame in range(iti_time + randrange(-1*iti_jitt, iti_jitt)): 
			self.fixStim.fillColor=[1,1,1]
			self.fixStim.lineColor=[1,1,1]
			self.fixStim.draw()
			self.screen.flip()

		# Present search-target stimulus
		for frame in range(target_time):
			for currStim in self.targetStim: currStim.draw()
			self.screen.flip()

		# WM delay (independent variable!)
		for frame in range(self.delay_dur):
			self.fixStim.draw()
			self.screen.flip()

		# Present search array stimulus until response
		self.button = None
		self.timer.reset()

########################### SEARCH / RECOGNITION TRIAL ###########################
#
#
		if 'mem' in self.trial_settings:

			while True:
				for currStim in self.searchStim: currStim.draw()
				if not 'recognition' in self.trial_settings:
					self.fixStim.draw()
				self.screen.flip()
				for key in event.getKeys():
					self.button = key

				# to pause/quit the experiment, press p/q
				if self.button=='p':
					continue
				elif self.button=='q':
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
			self.response.append([self.button,rt])

			# determine accuracy
			if not 'recognition' in self.trial_settings:
				if ((self.randpos[0]==2 or self.randpos[0]==3 or self.randpos[0]==4) and self.button == self.parameters['resp_keys'][0]) or ((self.randpos[0]==1 or self.randpos[0]==0 or self.randpos[0]==5) and self.button == self.parameters['resp_keys'][1]):
					self.accuracy.append(1)
				else: 
					self.accuracy.append(0)
			else:
				if (self.recog_ori == self.gabor_ori and self.button == self.parameters['resp_keys'][0]) or (not(self.recog_ori == self.gabor_ori) and self.button == self.parameters['resp_keys'][1]):
					self.accuracy.append(1)
				else:
					self.accuracy.append(0)

			# Present feedback after response
			if self.missing:
				for frame in range(iti_jitt):
					self.feedbackStim[2].draw()
					self.screen.flip()
			elif 'practice' in self.trial_settings:
				for frame in range(iti_jitt):
					self.feedbackStim[self.accuracy[0]].draw()
					self.screen.flip()
			else:
				for frame in range(iti_jitt): 
					self.fixStim.fillColor=[-1,-1,-1]
					self.fixStim.lineColor=[-1,-1,-1]
					self.fixStim.draw()
					self.screen.flip()


########################### TIMING TRIAL ###########################
#
#
		elif 'timing' in self.trial_settings:
			npress=0
			while True:
				self.button = None # reset button at each screen refresh
				self.fixStim.draw()
				self.probeStim.draw()
				self.screen.flip()
				for key in event.getKeys():
					self.button = key
					self.start_timer = True
				if self.button == 'space':
					npress = npress+1
					self.probeStim.fillColor=[1,-1,-1]
				if npress >1:
					self.probeStim.fillColor=[1,1,1]
					rt=self.timer.getTime()
					break

				if self.timer.getTime() > 10.0:
					self.button=None
					self.missing=True
					rt=0.0
					break
			self.response.append([self.button,rt])

			# determine accuracy
			if abs(rt - self.delay_val) < 0.25:
				self.accuracy.append(1)
			elif rt - self.delay_val < 0:
					self.accuracy.append(0)
			elif rt - self.delay_val > 0:
					self.accuracy.append(2)

			# Present feedback after response
			if self.missing:
				for frame in range(iti_jitt):
					self.feedbackStim[2].draw()
					self.screen.flip()
			elif 'practice' in self.trial_settings:
				for frame in range(iti_jitt):
					self.feedbackStim[self.accuracy[0]+3].draw()
					self.screen.flip()
		return ([self.trial_settings, self.response, self.accuracy])

