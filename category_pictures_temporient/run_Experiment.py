# Header
from Experiment import *

## Define parameters
params = {}

params['categories'] = ('face','house','letter')
# Get filenames of pictures 
inFiles = list()
extension = ".png"
thispath = os.getcwd()
for category in params['categories']:
	searchString = os.path.join(thispath,'stimuli', category, category+'*'+extension) 
	inFiles.append(glob.glob(searchString))
params['stimuli'] = inFiles # a 3 (category) by 100 (n unique pics) list

# Ports and Triggers
try:
	portOut = parallel.PParallelInpOut32(address=0x378); portOut.setData(0)
	portIn = parallel.PParallelInpOut32(address=0x379); portIn.setData(0)
except AttributeError:
	portOut=portIn=None
params['ports'] = [portOut,portIn]

# Create trigger dictionary, handy for indexing with names
params['triggers'] = {
	'practice': 90,
	'long': 	20,
	'short': 	10,
	'face': 	1,
	'house': 	2,
	'letter': 	3,
	'absent': 	0,
	'present': 	1
}

# Where should behavioral data be stored?
params['data_directory'] = 'data'

# subject/session ID
params['subject_id'] = raw_input("Subject ID: ")
# params['session_no'] = raw_input("Session: ")

# Monitor / screen
fS = raw_input("Full screen? Y/N: ")
if any(ans in fS for ans in['n','N']):
	params['fullScreen'] = False
else:
        params['fullScreen'] = True

params['monitor_refRate'] = 120 # fixed to 60hz for now 
params['monitor_width'] = 47.5
params['monitor_viewdist'] = 90
#params['monitor_pixelDims'] = (3200, 1800)
params['screenSize'] = [1680, 1050]

mon = monitors.Monitor(name = 'HP', width = params['monitor_width'], distance = params['monitor_viewdist'])
mon.setSizePix(params['screenSize'])
myWin = visual.Window(params['screenSize'], units = 'deg', monitor = mon, fullscr=params['fullScreen'])
myWin.mouseVisible = False
params['screen'] = myWin

# Trial/stim settings
params['absent_present'] = ('absent','present')
params['cue_stim_size'] = 2 # resize fraction (2 means half size)
params['search_stim_size'] = 4 # quarter of original picture size
params['search_set_size'] = 6
params['search_radius'] = 4.5
params['search_angle'] = 2*pi/params['search_set_size']

# Response
if portIn:
	params['resp_keys'] = [39,71]
else:
	params['resp_keys'] = ['f','j']

# The above parameters are assigned to the corresponding stimuli that need these as settings; this is done in Trial.py
# The actual index of some parameters (e.g. the true/false for present/absent get index 0/1 respectively) is determined in Experiment.py

# Timing
params['timing_ITI_Duration']    = 1.0 # ITI
params['timing_ITI_Jitter']      = 0.5 # set to 0 if no jitter
params['timing_target_Duration'] = .25 # duration of stimulus presentation, in sec
params['timing_ISI_Duration']    = [1.5,5] # very short for debugging purposes; change to 1.5 and 5 seconds

params['temp_prob'] = [1,1,1,1,0]


# determine number of trials for (practice) block
# 50 targets by abs/pres by short/long block by house/face/letter = 600 trials; divided by 6 blocks = 100 trials per block
# this gives 168 trials per category, collapsed over conditions

#### GO ####

# first a practice block with task instructions and example trials
params['block_type'] = 'practice'
params['ready_text'] = 'stimuli/ready_practice.txt'
params['ntrials']    = 24 # needs to be divided by 3 categories
params['rep_check']  = (12,4) # in chuncks of 12 trials, it is checked whether repetitions of 4 or more occur for absent/present
params['nblocks']    = 1 
exp = Experiment(params) 
exp.run_instruction('stimuli/instruct1.txt')
exp.run_example_trial(['face',inFiles[0][0],'present','short'])
exp.run_instruction('stimuli/instruct2.txt')
exp.run_example_trial(['house',inFiles[1][10],'absent','long'])
exp.run_instruction('stimuli/instruct3.txt')
exp.run()
exp.run_instruction('stimuli/finish_practice.txt')
##
# experimental block with only long intervals
params['block_type'] = 'long'
params['ready_text'] = 'stimuli/ready_long.txt'
params['ntrials']    = 300 # needs to be divided by 3*2 (category by absent/present) -> for real experiment 300
params['rep_check']  = (30,5) # 300 trials are divided up in chuncks of 30 where absent/present is shuffled such that no 5 repetitions are allowed
params['nblocks']    = 4 #                                                           -> for real experiment 4
exp = Experiment(params) 
exp.run()
if exp.finished():
   exp.store()
   
# experimental block with mostly short, sometimes long intervals (80/20 prob.)
params['block_type'] = 'short'
params['ready_text'] = 'stimuli/ready_short.txt'
exp = Experiment(params) 
exp.run()

if exp.finished():
   exp.store()
   exp.run_instruction('stimuli/finish_exp.txt')

# END #
#################################################

# -- parallel port check -- #
##toggle=True
##while toggle:
##        val=portIn.readData()
##        if not val==7:
##                print(val)
##                toggle=False
##quit()

