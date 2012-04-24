import networkx as nx
import random as random
import math

global debug
debug = False

class ConvoPDA(nx.MultiDiGraph):
	
	def __init__(self, matrix=[[]], key=[]):
		super(nx.MultiDiGraph, self).__init__()
		
		#nodes, edges (key used to preserve order of nodes for easy initialization)
		self.key = key
		self.matrix = matrix
		self.add_from_matrix(matrix, key)
		
		#username for current conversant
		self.username = ""
		
		#every PDA has a stack... ours has 3 (but it doesn't need to):
		self.conversation_queue = []
		self.event_queue = []
		self.time_delay_queue = []
		
		#iteration initializes to the first value in the key
		self.curr = key[0]
		
		#possible punctuation values
		self.punctuation = ['.', ',', '!']
		
		#information about typing speed  http://web.archive.org/web/20060628012633/http://readi.info/TypingSpeed.pdf
		self.typing_speed = .66 #characters per second (based on 40 wpm average, on length 5 words) 
		
	def reset(self):
		self.conversation_queue = []
		self.event_queue = []
		self.time_delay_queue = []
		self.curr = self.key[0]
		
	def reset_for_user(self, username):
		self.username = username
		self.reset()
		
#region: graph creation --------------------------------------------------------
	def add_from_matrix(self, matrix, key):
		#matrix[i][j] is the weight of a directional edge from key[i] to key[j]
		edges = []
		nodes = key #just trying to be obvious.
		for i in range(len(matrix)):
			for j in range(len(matrix[i])):
				if matrix[i][j] != 0:
					edges.append((key[i], key[j],{'weight':matrix[i][j],'from':key[i]}))
						#add epsilon transition logic here (for repeating characters)--> think about how to store the probability for the next move... markov chain?
		
		self.add_nodes_from(nodes)
		self.add_edges_from(edges)
		self.key = key
		
		
		
	def weight_event(self, weight, event):
		eventIndex = -1
		
		#make sure the event exists, and raise an exception if it does not
		try:
			for i in range(len(self.key)):
				if (self.key[i] == event):
					eventIndex = i
					break
			if eventIndex == -1:
				raise Exception
			
		except Exception:
			print "Event "+event+" was not found in the key."
		
		weightPct = (weight/100.0)
		if debug: print "weightpct\t",weightPct
		

		#modify the weight of each edge based on the new weight of the event
		for row in self.matrix:
			#if weight is negative, the adjustment is a negative percent of its value
			if weightPct < 0:
				weightAdjustment = row[eventIndex]*weightPct
			#if weight is positive, the adjustment is a postive percent of 1-its value
			else:
				weightAdjustment = (1-row[eventIndex])*weightPct
			
			row[eventIndex]+=weightAdjustment
			#now modify each other weight to keep total row weight at 1
			rowWeightRemaining = 1-row[eventIndex]
			
			runningTotal = 0
			
			for i in range(len(row)):
				#don't re-modify the event we've already modified
				if i != eventIndex:
					row[i]=row[i]*rowWeightRemaining
				if debug: print self.key[i],"\t",row[i]
				runningTotal += row[i]
			if debug: print "total:\t",runningTotal
			runningTotal = 0
				
				

#region: inherited methods -----------------------------------------------------
	def add_edges_from(self, edges):
		return super(nx.MultiDiGraph,self).add_edges_from(edges)
		
	def add_weighted_edges_from(self, edges):
		return super(nx.MultiDiGraph,self).add_weighted_edges_from(edges)
		
	def add_nodes_from(self, nodes):
		return super(nx.MultiDiGraph,self).add_nodes_from(nodes)
		
	def __getitem__(self, key):
		return super(nx.MultiDiGraph, self).__getitem__(key)
		
	def __setitem__(self, key):
		return super(nx.MultiDiGraph, self).__setitem__(key)


#region: iterator methods ------------------------------------------------------	
	def start_pda(self):
		self.curr = self.key[0]
		
	def step(self):
		rand = random.random()
		current_node = self[self.curr]
		
		edges_out = []
		edge_weights = []
		
		#detect outgoing nodes
		for neighbor in current_node:
			#print "Neighbor:", neighbor
			#print "Cur Node Neighbor:", current_node[neighbor]
			#print "Cur Node:", self.nodes(True)
			
			if current_node[neighbor][0]['from'] == self.curr:
				edges_out.append(neighbor)
				edge_weights.append(int(current_node[neighbor][0]['weight']*100))
		
		#from http://stackoverflow.com/questions/3655430/selection-based-on-percentage-weighting
		#select a random choice from a length 1000 array with the same distribution as the probabilities
		#print edges_out
		#print edge_weights
		picks = [v for v, d in zip(edges_out, edge_weights) for _ in range(d)]
		#print picks
		choice = random.choice(picks)
		
		#if it's a word, generate a word of some length
		#for a "word," spit the word up and add a delay for each letter
		if self.curr == 'x':
			self.curr = self.curr*self.generate_wordlen()
			for char in self.curr:
				self.event_queue.append(char)
				self.time_delay_queue.append(self.generate_delay())
		else:
			self.event_queue.append(self.curr)
			self.time_delay_queue.append(self.generate_delay())
		
		self.curr = choice		
		
	
#region: random methods --------------------------------------------------------
	def generate_wordlen(self):
		return self.poisson_dist_length(3)
	
	def poisson_dist_length(self, l):
		n, s = 0, 0
		while (s < 1):
			while (True):
				u = random.random()
				if u>0:
					break
			s -= math.log(u, math.e)/l;
			n += 1
		return n
	
	def exponential_dist(self, u=1):
		U=random.random()
		while(U==0):
			U=random.random()
		return -u*math.log(U)

	def generate_delay(self, numchars=1):
		delay = 0
		for i in range(numchars):
			delay += round(self.exponential_dist(self.typing_speed), 2)
		return delay
	
	def choose_punctuation(self):
		return random.choice(self.punctuation)
			
			
#region: convo generation-------------------------------------------------------
	def generate_convo_file(self, steps):
		C.reset_for_user(self.username)
		for i in range(steps):
			self.step()
		self.load_stack_convo()
		self.print_stack()
			
	def load_stack_convo(self):
		"""Loads the conversation_queue from the messages and timestamp stacks to
		create a stack of events (essentially a text file without a username)"""
		elapsed_time = 0
		last_timestamp = 0
		window_contents = ''
		prev_keystroke = ''
		for i in range(len(self.event_queue)):
			#don't add every character to the conversation stack
			event = False
			#tick the clock
			elapsed_time += self.time_delay_queue[i]

			#build the conversation based on what has been typed
			keystroke = self.event_queue[i]
			if keystroke == 'x':
				window_contents += keystroke
			elif keystroke == ' ':
				window_contents += keystroke
			elif keystroke == '[bkb]':
				#don't delete if nothing to delete
				if len(window_contents) > 0:
					window_contents = window_contents[0:len(window_contents)-1]
					event = True
			elif keystroke == '[bka]':
				event = True
			elif keystroke == '[pnc]':
				window_contents += self.choose_punctuation()
			elif keystroke == '[snd]':
				event = True
			elif keystroke == '[pau]':
				pass
			elif keystroke == 'ST':
				pass
			else:
				print "UNHANDLED EVENT", keystroke
			
			#each time the event flag is raised, append the window's contents to	  
			#the conversation																		  
			if event:
				self.conversation_queue.append((window_contents, elapsed_time, keystroke))
			#check to see if a timestamp needs to happen!
			elif elapsed_time - last_timestamp > .5:
				self.conversation_queue.append((window_contents, elapsed_time, '[tim]'))
				last_timestamp	= elapsed_time
			#reset window contents on send
			if keystroke == '[snd]':
				window_contents = ''
			
			#update vars for next iteration
			elapsed_time += self.time_delay_queue[i]
			prev_keystroke = keystroke

	def print_stack(self):
		f = open('files/User '+self.username+".txt", "w")
		for contents,time,event in self.conversation_queue:
			#print contents, time, event
			#print self.username+", 2011-11-11 "+self.convert_seconds_date(time)+", "+event[1:-1]+", "+contents+"[end]"
			f.write(self.username+", 2011-11-11 "+self.convert_seconds_date(time)+", "+event[1:-1]+", "+contents+"[end]\n")
			
	def convert_seconds_date(self, seconds):
		floor = math.floor
		date = seconds/60./60./24.
		days = int(floor(date))
		remainder = date - days
		remainder*= 24
		hours = int(floor(remainder))
		remainder -= hours
		remainder *= 60
		minutes = int(floor(remainder))
		remainder = remainder - minutes
		remainder *= 60
		seconds = round(remainder, 3)
		return str(hours)+':'+str(minutes).zfill(2)+':'+str(seconds).zfill(2)


#region: edge weight manipulation ----------------------------------------------
	#take a 2-tuple edge and add weight attribute
	def set_edge_weight(self, edge):
		node1, node2 = edge
		return (node1, node2, {'weight':self.calc_edge_weight(edge)})
	
	#calculates edge weight based on something.  here is 1
	def calc_edge_weight(self, edge):
		#actually make intelligent!
		return 1
		

#END OF CLASS ConvoPDA ---------------------------------------------------------
if __name__ == "__main__":
	nodes =  ['ST', 'x', ' ', '[bkb]', '[bka]', '[pnc]', '[pau]','[snd]']

	#			st 	x   ' '	 bb   ba	  pc  pa  sn	
	matrix =[[0,   1,   0,   0,   0,   0,	0,	0    ], #st
				[0,   0, .61, .22,   0, .05,	0,	.13  ], #x  
				[0, .76, .09, .14,   0,   0,	0,	.17  ], #' '
				[0,   0,   0, .55, .45,   0,	0,	0    ], #bb
				[0, .30, .30, .20,   0,	.10,	0,	.10  ], #ba
				[0,   0, .61, .30,   0,   0,	0,	.10  ], #pnc
				[.08, 0,   0,   0,  0,	  0,.92,	0    ], #pa
				[.01, 0,   0,   0,   0,	  0,.99,	0    ]] #snd
		
	#nodes = ['A', '|', 'C']
	
	#          a, b, c
	#matrix = [[0, 5, 5],  #a
	#          [.33, .33], .34],#b
	#	  		  [0, 1, 0]]  #c
	
	numConvos = 10 #should be DIVISIBLE BY 2
	numUsers = numConvos*2+(4-(numConvos*2)%4)
	username_list = []
	for i in range(numUsers/2):
		for gender in ["A","B"]:
			username_list.append(gender+'_01_'+str(i)+'_01')
	
	#create initial matrix
	C = ConvoPDA(matrix, nodes)
	C.start_pda()
	
	#write to the survey file
	fHandle = open("Surveys.csv", 'w')
	niceSurvey = ';"5";"5";"5";"5";"5";"5";"5";"5";"5";"5";"5";"5";"5";"5";"21"\n'
	meanSurvey = ';"1";"1";"1";"1";"1";"1";"1";"1";"1";"1";"1";"1";"1";"1";"21"\n'
	
	
	#first make some nice people (now just less pause and more send)
	C.weight_event(-10,'[pau]')
	C.weight_event(10, '[snd]')
	for i in range(numUsers/2):
		C.username = username_list[i]
		#30min*60sec/.66 average actions/second ~= 2727 actions
		C.generate_convo_file(2727)
		C.reset()
		fHandle.write("["+username_list[i]+"]"+niceSurvey)
		
	#now make some mean people (now just more pause and less send)
	C.add_from_matrix(matrix, nodes)
	C.reset()
	C.start_pda()
	C.weight_event(10,'[pau]')
	C.weight_event(-10, '[snd]')
	for i in range(numUsers/2, numUsers):
		C.username = username_list[i]
		#30min*60sec/.66 average actions/second ~= 2727 actions
		C.generate_convo_file(2727)
		C.reset()
		fHandle.write("["+username_list[i]+"]"+meanSurvey)
		
	fHandle.close()
		
	

