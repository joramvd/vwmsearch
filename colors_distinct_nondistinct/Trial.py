# Header
import numpy as np
import scipy.stats as stats
import sys, datetime, os, glob
import pickle
from psychopy import visual, event, core, parallel, monitors, sound #  
from math import pi, cos, sin, floor, fmod, radians
from random import randrange, shuffle, choice, random, getrandbits
from copy import deepcopy
from itertools import combinations
from IPython import embed as dbstop
from psychopy import prefs

prefs.general['audioLib'] = ['pygame']

# Class
class Trial(object):
	"""base class for Trials"""
	def __init__(self, trial_settings = {}, parameters = {}, screen = None):

		self.trial_settings = trial_settings
		self.parameters = parameters
		self.screen = screen

		self.targetStim = list()
		self.probeSound = list()
		self.color_idx = list()
		self.array_cols = list()
		self.warningSignal = list()
		self.searchStim = list()
		self.feedbackStim = list()
		self.response = list()
		self.accuracy = list()

		self.button = None
		self.keypress = None
		self.missing = False
		self.randpos = 0

		self.make_searchTarget()
		self.make_searchArray()
		self.make_fixation()
		self.make_feedback()

		self.probeSound = list()
		self.probeSound.append(sound.Sound(value=800,secs=0.05))
		self.probeSound.append(sound.Sound(value=500,secs=0.05))

		self.timer = core.Clock()

	def make_fixation(self):
		self.fixStim = visual.Circle(self.screen, radius = 0.08, fillColor = [1,1,1])

	def make_searchTarget(self):

		colval = [val for val in range(self.parameters['ncolors']) if val in self.trial_settings][0]
		distractor_cols = [v for v in range(self.parameters['ncolors']) if v is not colval and (abs(v-colval)>1 and abs(v-colval)<5)]
		self.color_idx.append(colval)
		self.color_idx.append(choice(distractor_cols))

		self.shadeval = randrange(self.parameters['nvalues'])
		self.template_color   = self.parameters['colors'][self.color_idx[0]][self.shadeval]
		self.distractor_color = self.parameters['colors'][self.color_idx[1]][self.shadeval]

		self.template_side = 1
		if 'left' in self.trial_settings:
			self.template_side = -1
		self.distractor_side = self.template_side*-1

		# target stim always gets black circle -- distractor stim always gets grey circle
		self.targetStim.append(visual.Circle(self.screen, radius=self.parameters['ring_stim_size'], pos = (self.template_side*self.parameters['cue_pos'],0),   fillColor = None, lineColor=self.parameters['ring_color'][0],lineWidth=self.parameters['ring_line_width']))
		self.targetStim.append(visual.Circle(self.screen, radius=self.parameters['ring_stim_size'], pos = (self.distractor_side*self.parameters['cue_pos'],0), fillColor = None, lineColor=self.parameters['ring_color'][1],lineWidth=self.parameters['ring_line_width']))
		# if this is 80% probability distinct trial, then target stim gets dashed circle
		if 'distinct' in self.trial_settings:
			for ori in self.parameters['ring_dash_ori']:
				self.targetStim.append(visual.Rect(self.screen, ori=ori, pos = (self.template_side*self.parameters['cue_pos'],0), width=self.parameters['ring_dash_width'], height=self.parameters['ring_dash_length'], fillColor='grey',lineColor=None))
		
		# colors of target and distractor
		self.targetStim.append(visual.Circle(self.screen, radius=self.parameters['cue_stim_size'], pos = (self.template_side*self.parameters['cue_pos'],0),   fillColor = self.template_color,   lineColor=None, fillColorSpace = 'hsv'))
		self.targetStim.append(visual.Circle(self.screen, radius=self.parameters['cue_stim_size'], pos = (self.distractor_side*self.parameters['cue_pos'],0), fillColor = self.distractor_color, lineColor=None, fillColorSpace = 'hsv'))

		trig = [self.parameters['triggers'][key] for key in self.parameters['triggers'] if key in self.trial_settings]
		trig.append(colval)
		self.stimtrig = sum(trig)

	def make_searchArray(self):

		self.randpos = range(self.parameters['search_set_size']); shuffle(self.randpos) # n positions of n-search-array, randomized
		self.template_clockwheel = [pos for pos in self.parameters['clockwheel_pos'] if pos in self.trial_settings][0]

		if ('distinct' in self.trial_settings and 'congruent' in self.trial_settings) or ('nondistinct' in self.trial_settings and 'incongruent' in self.trial_settings):
			self.array_cols.append(self.template_color)
			self.array_cols.append(self.distractor_color)
			self.array_cols.append([-.5,-.5,-.5])
			self.array_cols.append([0,0,0])
			self.array_cols.append([.5,.5,.5])
		else:
			self.array_cols.append(self.template_color)
			distractor_shades = [v for v in range(self.parameters['nvalues']) if v is not self.shadeval]
			shuffle(distractor_shades)
			for item in range(self.parameters['search_set_size']-1):
				self.array_cols.append(self.parameters['colors'][self.color_idx[0]][distractor_shades[item]])

		for k,circ in enumerate(self.array_cols):
			defpos = np.array([self.parameters['search_radius']*cos(self.parameters['search_angle']*(self.randpos[k]+1)+self.parameters['search_angle']/2), self.parameters['search_radius']*sin(self.parameters['search_angle']*(self.randpos[k]+1)+self.parameters['search_angle']/2)*-1])
			if k==0:
				clockwheel_pos = self.template_clockwheel
			else:
			 	clockwheel_pos = choice(self.parameters['clockwheel_pos'])
			posshift = np.array([self.parameters['search_stim_size']/1.2*cos(radians(clockwheel_pos)), self.parameters['search_stim_size']/1.2*sin(radians(clockwheel_pos))])
			self.searchStim.append(visual.Circle(self.screen, radius=self.parameters['search_stim_size'], fillColor = circ, fillColorSpace='rgb', lineColor = self.parameters['ring_color'][0], pos = defpos))
			self.searchStim.append(visual.Rect(self.screen, ori=clockwheel_pos, pos=defpos+posshift, width=0.15, height=self.parameters['cue_stim_size']/1.2, fillColor = self.parameters['ring_color'][0], lineColor=None))

		for p,pos in enumerate(self.parameters['clockwheel_pos']):
			if self.template_clockwheel == pos:
				self.searchtrig = p+1

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
		isi_time    = int(floor(float(self.parameters['timing_ISI_Duration']) * float(self.parameters['monitor_refRate'])))
		ws_latency  = int(floor(float(self.parameters['timing_WS_Latency']) * float(self.parameters['monitor_refRate'])))

		# Change fixation to white to start ITI with jitter
		for frame in range(iti_time + randrange(-1*iti_jitt, iti_jitt)): 
			self.fixStim.fillColor=[1,1,1]
			self.fixStim.lineColor=[1,1,1]
			self.fixStim.draw()
			self.screen.flip()

		# Present search-target stimulus
		if portOut:
			portOut.setData(int(self.stimtrig)); core.wait(0.02) # code for category (1,2,3) and short/long/practice block type (+ 60/70/80)
			portOut.setData(0)
		else:
			print(int(int(self.stimtrig)))
		for frame in range(target_time):
			for currStim in self.targetStim: currStim.draw()
			self.fixStim.draw()
			self.screen.flip()

		# ISI with warning signal
		for frame in range(isi_time):
			if frame==ws_latency and 'incongruent' in self.trial_settings:
				self.probeSound[0].play()
			self.fixStim.draw()
			self.screen.flip()


		# Present first search array stimulus until response
		self.button = None
		self.timer.reset()
		if portOut:
			portOut.setData(int(self.searchtrig)); core.wait(0.02) # code for category (1,2,3) and short/long/practice block type (+ 60/70/80)
			portOut.setData(0)
		else:
			print(int(int(self.searchtrig)))
		while True:
			for currStim in self.searchStim: currStim.draw()
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

		if self.template_clockwheel==135 and self.button == self.parameters['resp_keys'][0]:
			self.accuracy.append(1)
		elif self.template_clockwheel==-135 and self.button == self.parameters['resp_keys'][1]:
			self.accuracy.append(1)
		elif self.template_clockwheel==45 and self.button == self.parameters['resp_keys'][2]:
			self.accuracy.append(1)
		elif self.template_clockwheel==-45 and self.button == self.parameters['resp_keys'][3]:
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

		return ([self.trial_settings, self.response, self.accuracy])
