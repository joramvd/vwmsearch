from psychopy import visual, event, core

class Text(object):

	def __init__(self, parameters = {}, screen = None, text = {}):

		self.parameters = parameters.copy()
		self.screen = screen
		self.tstim = text
		self.make_Text()

	def make_Text(self):
		self.text2show = visual.TextStim(self.screen, text = self.tstim, color = 'white', pos = (0, 0), height = 0.4)

	def show(self):
		portIn = self.parameters['ports'][1]

		core.wait(0.5)
		if portIn:
			while True:
				self.text2show.draw()
				self.screen.flip()
				val = portIn.readData()
				if val in self.parameters['resp_keys']:
					break
				for key in event.getKeys():
					if key in ['escape','q']:
						quit()
		else:
			self.text2show.draw()
			self.screen.flip()
			resp = event.waitKeys()
			if resp[0] in  ['escape','q']: 
				quit()
