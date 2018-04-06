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
params['subject_id'] = raw_input("Subject ID: ")

# Monitor / screen
fS = raw_input("Full screen? Y/N: ")
if any(ans in fS for ans in['n','N']):
	params['fullScreen'] = False
else:
        params['fullScreen'] = True

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

# params['rgb_colors'] = ['IndianRed','SandyBrown','Khaki','MediumAquaMarine','Cornflower','Plum']
# params['rgb_colors'] = [[0.,.55,.8],[28.,.61,.96],[54.,.42,.94],[160.,.5,.8],[219.,.58,.93],[300.,.28,.87]]
d=0; l=1
params['dkl_colors'] = [[d,0,l],[d,30,l],[d,60,l],[d,120,l],[d,210,l],[d,270,l]]
params['rgb_colors'] = [tools.colorspacetools.dkl2rgb(np.array(col)) for col in params['dkl_colors']]
params['color_combs']   = [comb for comb in combinations(params['rgb_colors'], 2)] + [comb for comb in combinations(list(reversed(params['rgb_colors'])), 2)]
params['probe_type']   = ['template','accessory']
params['gap']           = ('left','right')

params['cue_stim_size']    = 0.75
params['ring_color']	   = 'darkgrey'
params['ring_stim_size']   = 1.2
params['ring_line_width']  = 6
params['ring_dash_ori']    = [0, 45, 90, 135]
params['ring_dash_length'] = params['ring_stim_size']*2+0.5
params['ring_dash_width']  = pi*2*params['ring_stim_size']/(4*len(params['ring_dash_ori']))
params['cue_pos']          = 2.0
params['search_stim_size'] = params['cue_stim_size']
params['probe_stim_size']  = params['cue_stim_size']
params['gap_stim_size']    = 50 # gap is a grey line drawn over one side of the rectangle; this is the linewidth of visual.Line
params['search_set_size']  = 5
params['search_radius']    = 5
params['search_posjitt']   = 1 # so the search array is not exactly on a circle/hexagon
params['search_angle']     = 2*pi/params['search_set_size']

# Response
if portIn:
	params['resp_keys'] = [39,71]
else:
	params['resp_keys'] = ['f','j']

# The above parameters are assigned to the corresponding stimuli that need these as settings; this is done in Trial.py
# The actual index of some parameters (e.g. the true/false for present/absent get index 0/1 respectively) is determined in Experiment.py

# Timing
params['timing_ITI_Duration']    = 1.5 # ITI
params['timing_ITI_Jitter']      = 0.5 # set to 0 if no jitter
params['timing_target_Duration'] = 0.75 # duration of stimulus presentation, in sec
params['timing_ISI_Duration']    = 1.5 # time between target, probe, and search
params['timing_ISI_Jitter']      = 0.5 # set to 0 if no jitter

# Probability of timing probe
#params['prope_prob'] = .75

# truncated normal distribution around target duration (which becomes the 'standard' against which the probe duration is compared as shorter/longer)
params['standard_Duration'] = 0.5;
lower, upper = params['standard_Duration']-0.3, params['standard_Duration']+0.3
mu, sigma = params['standard_Duration'], 0.1
X = stats.truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)

params['timing_probe_Duration']  = X.rvs(100) # this should be variable, and should be reproduced to measure subjective duration
dbstop()
# determine number of trials for (practice) block
# 50 targets by abs/pres by short/long block by house/face/letter = 600 trials; divided by 6 blocks = 100 trials per block
# this gives 168 trials per category, collapsed over conditions

#### GO ####

# first a practice block with task instructions and example trials
params['block_type'] = 'practice'
params['ready_text'] = 'stimuli/ready_practice.txt'
params['ntrials']    = 600 # needs to be divided by 30 color combinations
params['rep_check']  = (12,4) # in chuncks of 12 trials, it is checked whether repetitions of 4 or more occur for absent/present
params['nblocks']    = 20 


exp = Experiment(params) 
exp.run()

