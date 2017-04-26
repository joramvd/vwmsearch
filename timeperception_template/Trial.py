# Header
import numpy as np
import scipy.stats as stats
import sys, datetime, os, glob
import pickle
from psychopy import visual, event, core, parallel, monitors, tools  
from math import pi, cos, sin, floor, fmod
from random import randrange, shuffle, choice, random, getrandbits
from copy import deepcopy
from itertools import combinations
from IPython import embed as dbstop

# Class
class Trial(object):
	"""base class for Trials"""
	def __init__(self, trial_settings = {}, parameters = {}, screen = None):

		self.trial_settings = trial_settings
		self.parameters = parameters
		self.screen = screen

		self.targetStim = list()
		self.probeStim = list()
		self.searchStim1 = list()
		self.searchStim2 = list()
		self.feedbackStim = list()
		self.response = list()
		self.accuracy = list()

		self.button = None
		self.keypress = None
		self.missing = False
		self.randpos = 0

		self.make_searchTarget()
		self.make_Probe()
		self.make_searchArray1()
		self.make_searchArray2()
		self.make_fixation()
		self.make_feedback()

		self.timer = core.Clock()

	def make_fixation(self):
		self.fixStim = visual.Circle(self.screen, radius = 0.08, fillColor = [1,1,1])

	def make_searchTarget(self):
		LR = [-1,1]
		shuffle(LR)

		self.cue_colors = self.trial_settings[2]

		self.targetStim.append(visual.Circle(self.screen, radius=self.parameters['ring_stim_size'], pos = (LR[0]*self.parameters['cue_pos'],0), fillColor = None, lineColor=self.parameters['ring_color'],lineWidth=self.parameters['ring_line_width']))
		self.targetStim.append(visual.Circle(self.screen, radius=self.parameters['cue_stim_size'], pos = (LR[0]*self.parameters['cue_pos'],0), fillColor = self.cue_colors[0], fillColorSpace='rgb', lineColor=None))

		self.targetStim.append(visual.Circle(self.screen, radius=self.parameters['ring_stim_size'], pos = (LR[1]*self.parameters['cue_pos'],0), fillColor = None, lineColor=self.parameters['ring_color'],lineWidth=self.parameters['ring_line_width']))
		for ori in self.parameters['ring_dash_ori']:
			self.targetStim.append(visual.Rect(self.screen, ori=ori, pos = (LR[1]*self.parameters['cue_pos'],0), width=self.parameters['ring_dash_width'], height=self.parameters['ring_dash_length'], fillColor=self.parameters['screenBackground'],lineColor=None))
		self.targetStim.append(visual.Circle(self.screen, radius=self.parameters['cue_stim_size'], pos = (LR[1]*self.parameters['cue_pos'],0), fillColor = self.cue_colors[1], fillColorSpace='rgb', lineColor=None))

	def make_Probe(self):
		if not 'none' in self.trial_settings:
			if 'template' in self.trial_settings: 
				toggle=0
			elif 'accessory' in self.trial_settings:
				toggle=1
		
			self.probeStim.append(visual.Circle(self.screen, radius=self.parameters['probe_stim_size'], pos = (0,0), fillColor = 'grey', lineColor='white'))
			self.probeStim.append(visual.Circle(self.screen, radius=self.parameters['probe_stim_size'], pos = (0,0), fillColor = self.cue_colors[toggle], lineColor='white', fillColorSpace='rgb'))
			
	def make_searchArray1(self):
		self.randpos = range(self.parameters['search_set_size']); shuffle(self.randpos) # n positions of n-search-array, randomized
		self.gappos = [[0,1],[0,-1],[1,0],[-1,0]] # top, bottom, right, left

		array_cols = [item for item in self.parameters['rgb_colors'] if item is not self.cue_colors[1]]
		for k,circ in enumerate(array_cols):
			arrpos = [self.parameters['search_radius']*cos(self.parameters['search_angle']*(self.randpos[k]+1)+self.parameters['search_angle']/2), self.parameters['search_radius']*sin(self.parameters['search_angle']*(self.randpos[k]+1)+self.parameters['search_angle']/2)*-1]
			posjitt = [choice([-1*self.parameters['search_posjitt'],self.parameters['search_posjitt']])*random(), choice([-1*self.parameters['search_posjitt'],self.parameters['search_posjitt']])*random()]
			defpos = [x + y for x, y in zip(arrpos, posjitt)]
			if np.array_equal(circ,self.cue_colors[0]): # if this search array stimulus is the template
				defgap = choice(self.gappos[0:2]) # pick only top/bottom gap
				self.template_gap = defgap # save the side of the gap to evaluate accuracy of response
			else:
				defgap = choice(self.gappos) # distractors may have gap on all sides
			self.searchStim1.append(visual.Rect(self.screen, width=self.parameters['search_stim_size'],height=self.parameters['search_stim_size'], fillColor = circ, fillColorSpace='rgb', lineColor = None, pos = defpos))
			self.searchStim1.append(visual.Rect(self.screen, width=self.parameters['search_stim_size']/2,height=self.parameters['search_stim_size']/2, fillColor = self.parameters['screenBackground'], lineColor = None, pos = defpos))			
			self.searchStim1.append(visual.Line(self.screen, lineWidth=self.parameters['gap_stim_size'], lineColor = self.parameters['screenBackground'], start = defpos, end = (defpos[0]+defgap[0],defpos[1]+defgap[1])))

	def make_searchArray2(self):
		shuffle(self.randpos)
		
		array_cols = [item for item in self.parameters['rgb_colors'] if item is not self.cue_colors[0]]

		for k,circ in enumerate(array_cols):
			arrpos = [self.parameters['search_radius']*cos(self.parameters['search_angle']*(self.randpos[k]+1)+self.parameters['search_angle']/2), self.parameters['search_radius']*sin(self.parameters['search_angle']*(self.randpos[k]+1)+self.parameters['search_angle']/2)*-1]
			posjitt = [choice([-1*self.parameters['search_posjitt'],self.parameters['search_posjitt']])*random(), choice([-1*self.parameters['search_posjitt'],self.parameters['search_posjitt']])*random()]
			defpos = [x + y for x, y in zip(arrpos, posjitt)]
			if np.array_equal(circ,self.cue_colors[1]): # if this search array stimulus is the accessory of search 1
				defgap = choice(self.gappos[0:2]) # pick only top/bottom gap
				self.accessory_gap = defgap # save the side of the gap to evaluate accuracy of response
			else:
				defgap = choice(self.gappos) # distractors may have gap on all sides
			self.searchStim2.append(visual.Rect(self.screen, width=self.parameters['search_stim_size'],height=self.parameters['search_stim_size'], fillColor = circ, fillColorSpace='rgb', lineColor = None, pos = defpos))
			self.searchStim2.append(visual.Rect(self.screen, width=self.parameters['search_stim_size']/2,height=self.parameters['search_stim_size']/2, fillColor = self.parameters['screenBackground'], lineColor = None, pos = defpos))			
			self.searchStim2.append(visual.Line(self.screen, lineWidth=self.parameters['gap_stim_size'], lineColor = self.parameters['screenBackground'], start = defpos, end = (defpos[0]+defgap[0],defpos[1]+defgap[1])))

	def make_feedback(self):
		self.feedbackStim.append(visual.TextStim(self.screen,text='wrong...',pos=(0.0,0), height=0.6))
		self.feedbackStim.append(visual.TextStim(self.screen,text='correct!',pos=(0.0,0), height=0.6))
		self.feedbackStim.append(visual.TextStim(self.screen,text='respond faster!',pos=(0.0,0), height=0.6))

	def run(self):

		iti_time    = int(floor(float(self.parameters['timing_ITI_Duration']) * float(self.parameters['monitor_refRate'])))
		iti_jitt    = int(floor(float(self.parameters['timing_ITI_Jitter']) * float(self.parameters['monitor_refRate'])))
		target_time = int(floor(float(self.parameters['timing_target_Duration']) * float(self.parameters['monitor_refRate'])))
		isi_time    = int(floor(float(self.parameters['timing_ISI_Duration']) * float(self.parameters['monitor_refRate'])))
		isi_jitt    = int(floor(float(self.parameters['timing_ISI_Jitter']) * float(self.parameters['monitor_refRate'])))

		# Change fixation to white to start ITI with jitter
		for frame in range(iti_time + randrange(-1*iti_jitt, iti_jitt)): 
			self.fixStim.fillColor=[1,1,1]
			self.fixStim.lineColor=[1,1,1]
			self.fixStim.draw()
			self.screen.flip()

		# Present search-target stimulus
		for frame in range(target_time):
			for currStim in self.targetStim: currStim.draw()
			self.fixStim.draw()
			self.screen.flip()

		# ISI
		for frame in range(isi_time + randrange(-1*isi_jitt, isi_jitt)):
			self.fixStim.draw()
			self.screen.flip()

		# probe of variable duration
		if not 'none' in self.trial_settings:
			tmp_probedur = [x for x in set(self.parameters['timing_probe_Duration']) if np.any(np.array(self.trial_settings,dtype=object)==x)]
			self.probedur = tmp_probedur[0]		
			probe_time  = int(floor(float(self.probedur) * float(self.parameters['monitor_refRate'])))
			standard_time = int(floor(float(self.parameters['standard_Duration']) * float(self.parameters['monitor_refRate'])))

			for frame in range(standard_time):
				self.probeStim[1].draw()
				self.screen.flip()
			for frame in range(isi_time + randrange(-1*isi_jitt, isi_jitt)):
				self.fixStim.draw()
				self.screen.flip()
			for frame in range(probe_time):
				self.probeStim[0].draw()
				self.screen.flip()

			# response window for time judgment
			self.timer.reset()
			while True:
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

			# determine timing accuracy
			if (probe_time <  standard_time and self.button==self.parameters['resp_keys'][0]) or (probe_time >  standard_time and self.button==self.parameters['resp_keys'][1]):
				self.accuracy.append(1)
			else: 
				self.accuracy.append(0)

			# Present feedback after response
			if self.missing:
				for frame in range(iti_jitt):
					self.feedbackStim[2].draw()
					self.screen.flip()
			elif self.parameters['block_type']=='practice':
				for frame in range(iti_jitt):
					self.feedbackStim[self.accuracy[0]].draw()
					self.screen.flip()
			else:
				# Present black fixation point right after self.button press of previous trial
				for frame in range(iti_jitt): 
					self.fixStim.fillColor=[-1,-1,-1]
					self.fixStim.lineColor=[-1,-1,-1]
					self.fixStim.draw()
					self.screen.flip()

		else:
			# Present first search array stimulus until response
			self.button = None
			self.timer.reset()
			while True:
				for currStim in self.searchStim1: currStim.draw()
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
			# determine accuracy of first search
			if (self.template_gap==[0,1] and self.button == self.parameters['resp_keys'][0]) or (self.template_gap==[0,-1] and self.button == self.parameters['resp_keys'][1]):
				self.accuracy.append(1)
			else: 
				self.accuracy.append(0)

			# Present feedback after response
			if self.missing:
				for frame in range(iti_jitt):
					self.feedbackStim[2].draw()
					self.screen.flip()
			elif self.parameters['block_type']=='practice':
				for frame in range(iti_jitt):
					self.feedbackStim[self.accuracy[0]].draw()
					self.screen.flip()
			else:
				# Present black fixation point right after self.button press of previous trial
				for frame in range(iti_jitt): 
					self.fixStim.fillColor=[-1,-1,-1]
					self.fixStim.lineColor=[-1,-1,-1]
					self.fixStim.draw()
					self.screen.flip()

			# ISI
			for frame in range(isi_time + randrange(-1*isi_jitt, isi_jitt)):
				self.fixStim.draw()
				self.screen.flip()

			# Present second search array stimulus until response
			self.button = None
			self.timer.reset()
			while True:
				for currStim in self.searchStim2: currStim.draw()
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

			# determine accuracy of second search
			if (self.accessory_gap==[0,1] and self.button == self.parameters['resp_keys'][0]) or (self.accessory_gap==[0,-1] and self.button == self.parameters['resp_keys'][1]):
				self.accuracy.append(1)
			else: 
				self.accuracy.append(0)

			# Present feedback after response
			if self.missing:
				for frame in range(iti_jitt):
					self.feedbackStim[2].draw()
					self.screen.flip()
			elif self.parameters['block_type']=='practice':
				for frame in range(iti_jitt):
					self.feedbackStim[self.accuracy[1]].draw()
					self.screen.flip()
			else:
				# Present black fixation point right after self.button press of previous trial
				for frame in range(iti_jitt): 
					self.fixStim.fillColor=[-1,-1,-1]
					self.fixStim.lineColor=[-1,-1,-1]
					self.fixStim.draw()
					self.screen.flip()

		return ([self.trial_settings, self.response, self.accuracy])


	#def export(self):
	#	return np.concatenate([self.trial_settings.copy(), self.response.copy()])

