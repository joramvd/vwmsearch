The Python code in this repo are different versions of a visual search task that relies on visual working memory.
The basic structure is:
- the presentation of a cue that a participant has to remember
- an empty delay period or retention interval
- a search display with various stimuli, amongst which is the cue (the search target)

The specifics differ per project, but the Python objects have the same logic:
- A Trial object constructs one instance of a trial, mostly with the PsychoPy package; it creates the stimuli in different sub-functions, and presents everything consecutively in a run() function
- An Experiment object defines multiples of these trials, shows explanation screens and runs blocks of trials in a run() function
- A run_Experiment script defines all the parameters for the Experiment and Trial objects, and calls the Experiment.run() function


