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
params['subject_id'] = 'test'
# params['subject_id'] = raw_input("Subject ID: ")

# Monitor / screen
# fS = raw_input("Full screen? Y/N: ")
# if any(ans in fS for ans in['n','N']):
params['fullScreen'] = False
# else:
# 	params['fullScreen'] = True

params['monitor_refRate'] = 60 # 60 on Mac, 120 in lab [for debugging, lower value to speed timing]
params['monitor_width'] = 47.5
params['monitor_viewdist'] = 90
# params['screenSize'] = [1680, 1050]
params['screenSize'] = [1200, 800]
params['screenBackground'] = [-1,-1,-1]

mon = monitors.Monitor(name = 'HP', width = params['monitor_width'], distance = params['monitor_viewdist'])
mon.setSizePix(params['screenSize'])
myWin = visual.Window(params['screenSize'], units = 'deg', monitor = mon, fullscr=params['fullScreen'],color = params['screenBackground'])
myWin.mouseVisible = False
params['screen'] = myWin

# Trial/stim settings
params['cue_stim_size']    = 3
params['ring_color']	   = 'grey'
params['ring_stim_size']   = 1.75
params['ring_line_width']  = 4
params['search_stim_size'] = params['cue_stim_size']
params['probe_stim_size']  = params['cue_stim_size']
params['search_set_size']  = 6
params['search_radius']    = 5
params['search_posjitt']   = 1 # so the search array is not exactly on a circle/hexagon
params['search_angle']     = 2*pi/params['search_set_size']
params['search_stim_ori']  = np.linspace(180/params['search_set_size'],180,params['search_set_size'])

# Response
if portIn:
	params['resp_keys'] = [39,71]
else:
	params['resp_keys'] = ['f','j']

# Timing
params['timing_ITI_Duration']    = 1.5 # ITI
params['timing_ITI_Jitter']      = 0.5 # set to 0 if no jitter
params['timing_target_Duration'] = 0.5 # duration of stimulus presentation, in sec
params['timing_ISI_Duration']    = 1.0 # time between target, probe, and search
params['timing_ISI_Jitter']      = 0.5 # set to 0 if no jitter

# truncated normal distribution around target duration (which becomes the 'standard' against which the probe duration is compared as shorter/longer)
params['standard_Duration'] = 3;
lower, upper = params['standard_Duration']-2, params['standard_Duration']+2
mu, sigma = params['standard_Duration'], 1
ntrials = 160
X = stats.truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)
params['timing_probe_Duration']  = X.rvs(ntrials) # this should be variable, and should be reproduced to measure subjective duration

block_order = ['search','recognition','novwm']
shuffle(block_order)
params['trial_type'] = ['mem','mem','mem','timing']

#### GO ####

# first a practice block with task instructions and example trials
for b,block in enumerate(block_order):

	params['task_type'] = block
	params['block_type'] = 'practice'
	params['ready_text'] = ('stimuli/ready_practice.txt')
	params['ntrials']    = 8 # so we get 4 timing trials
	params['nblocks']    = 1 
	exp = Experiment(params) 

	if b==0:
		exp.run_instruction(('stimuli/instruct1_' + block + '.txt'))
		exp.run_example_trial(['mem',block,choice(params['timing_probe_Duration']),'practice'])
		exp.run_instruction('stimuli/instruct2_timing.txt')
		exp.run_example_trial(['timing',block,choice(params['timing_probe_Duration']),'practice'])
	exp.run()
	exp.run_instruction('stimuli/finish_practice.txt')

	params['task_type'] = block
	params['block_type'] = 'real'
	params['ready_text'] = ('stimuli/ready_' + block + '.txt')
	params['ntrials']    = ntrials
	params['nblocks']    = 5 
	exp = Experiment(params) 
	exp.run()

