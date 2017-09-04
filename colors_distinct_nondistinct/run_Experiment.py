# Header
from Experiment import *

## Define parameters
params = {}

# Ports and Triggers
try:
	portOut = parallel.PParallelInpOut32(address=0x378); portOut.setData(0)
	portIn = parallel.PParallelInpOut32(address=0x379); portIn.setData(0)
except AttributeError:
	portOut=portIn=None
params['ports'] = [portOut,portIn]

# Where should behavioral data be stored?
params['data_directory'] = 'data'

# subject/session ID
params['subject_id'] = raw_input("Subject ID: ")

# Monitor / screen
fS = raw_input("Full screen? Y/N: ")
if any(ans in fS for ans in['n','N']):
	params['fullScreen'] = False
else:
	params['fullScreen'] = True

params['monitor_refRate'] = 60 # 60 on Mac laptop; 120 in lab
params['monitor_width'] = 47.5
params['monitor_viewdist'] = 90
params['screenSize'] = [1680, 1050]

mon = monitors.Monitor(name = 'HP', width = params['monitor_width'], distance = params['monitor_viewdist'])
mon.setSizePix(params['screenSize'])
myWin = visual.Window(params['screenSize'], units = 'deg', monitor = mon, fullscr=params['fullScreen'])
myWin.mouseVisible = False
params['screen'] = myWin

# Trial/stim settings

hue_val = {}
hue_val['red'] = ['Crimson','Firebrick','IndianRed','OrangeRed','Red','Tomato']
hue_val['yellow'] = ['DarkKhaki','Gold','Goldenrod','Khaki','Moccasin','Yellow']
hue_val['green'] = ['SpringGreen','Limegreen','OliveDrab','Lime','LightGreen','ForestGreen']
hue_val['cyan'] = ['Cyan','DarkCyan','DarkTurquoise','PowderBlue','Turquoise','SkyBlue']
hue_val['blue'] = ['Blue','DarkBlue','SlateBlue','Royalblue','Dodgerblue','Deepskyblue']
hue_val['purple'] = ['MediumOrchid','DarkMagenta','Fuchsia','MediumVioletRed','DeepPink','HotPink']

params['ncolors']          = len(hue_val)
params['nvalues']          = len(hue_val['red'])
params['colors']           = hue_val
params['response_pos']     = [0,1,2,3]
params['template_side']    = ['left','right']
params['search_type']      = ['distinct','nondistinct']
params['cue_stim_size']    = 0.75
params['ring_color']	   = ['black','darkgrey']
params['ring_stim_size']   = 0.75
params['ring_line_width']  = 6
params['ring_dash_ori']    = [0, 45, 90, 135]
params['ring_dash_length'] = params['ring_stim_size']*2+0.5
params['ring_dash_width']  = pi*2*params['ring_stim_size']/(4*len(params['ring_dash_ori']))
params['cue_pos']          = 3.0
params['search_stim_size'] = 0.75
params['probe_stim_size']  = params['cue_stim_size']
params['search_set_size']  = 6
params['search_radius']    = 4
params['search_angle']     = 2*pi/params['search_set_size']

# Create trigger dictionary, handy for indexing with names
params['triggers'] = {
	'left': 		10,
	'right':		20,
	'incongruent':	0,
	'congruent': 	100,
	'distinct': 	0,
	'nondistinct': 	20
}
for c,col in enumerate(hue_val):
	params['triggers'][col] = c

# Response
if portIn:
	params['resp_keys'] = [39,71]
else:
	params['resp_keys'] = ['d','f','j','k']

# Timing
params['timing_ITI_Duration']    = 1.5 # ITI
params['timing_ITI_Jitter']      = .5 # set to 0 if no jitter
params['timing_target_Duration'] = .5 # duration of stimulus presentation, in sec
params['timing_ISI_Duration']    = 2.5 # time between target, probe, and search
params['timing_WS_Latency']      = 1. # warning signal for incongruent trials after 1 sec; "reorienting" delay is then 1.5 sec.

params['probability'] = (3,7)

dbstop()

#### GO ####

# first a practice block with task instructions and example trials
params['block_type'] = 'practice'
params['ready_text'] = 'stimuli/ready_practice.txt'
params['ntrials']    = 20 
params['nblocks']    = 1 
exp = Experiment(params) 
exp.run_instruction('stimuli/instruct1.txt')
exp.run_example_trial(['left','red','distinct',2,'congruent'])
exp.run_instruction('stimuli/instruct2.txt')
exp.run_example_trial(['right','blue','nondistinct',1,'congruent'])
exp.run_instruction('stimuli/instruct3.txt')
exp.run_example_trial(['right','yellow','distinct',0,'congruent'])
exp.run_example_trial(['left','green','distinct',3,'incongruent'])
exp.run_instruction('stimuli/instruct4.txt')
exp.run()

params['block_type'] = 'real'
params['ready_text'] = 'stimuli/ready_real.txt'
params['ntrials']    = 600
params['nblocks']    = 10 
exp = Experiment(params)
exp.run()

if exp.finished():
   exp.store()
   exp.run_instruction('stimuli/finished.txt')

