#TODO:
#	-Prevent more [bkb] than characters in message
#	-Add time
#	-Adjust edge weights based on previous character
#	-parse message stack and time stack in order to build convo half
#	-Implement function for realistic sentence patterns



import networkx as nx
import random as random
import math


class ConvoPDA(nx.MultiDiGraph):
	
	def __init__(self, matrix=[[]], key=[]):
		super(nx.MultiDiGraph, self).__init__()
		
		#nodes, edges (key used to preserve order of nodes for easy initialization)
		self.key = key
		self.add_from_matrix(matrix, key)
		
		#every PDA needs a stack!  Ours has 3:
		self.stack_conversation = []
		self.stack_message = []
		self.stack_time = []		
		#iteration initializes to the first value in the key
		self.curr = key[0]
		
		#random seed set to "" but we will allow other values?
		self.seed = ""
		
		#information about typing speed  http://web.archive.org/web/20060628012633/http://readi.info/TypingSpeed.pdf
		self.typing_speed = .66 #characters per second (based on 40 wpm average, on length 5 words) 
		
	#matrix[i][j] is the weight of a directional edge from key[i] to key[j]
	def add_from_matrix(self, matrix, key):
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
				edge_weights.append(int(current_node[neighbor][0]['weight']*1000))
		
		#from http://stackoverflow.com/questions/3655430/selection-based-on-percentage-weighting
		#select a random choice from a length 1000 array with the same distribution as the probabilities
		#print edges_out
		#print edge_weights
		picks = [v for v, d in zip(edges_out, edge_weights) for _ in range(d)]
		#print picks
		choice = random.choice(picks)
		
		#if it's a word, generate a word of some length
		#also generate a delay of appropriate length
		delay = 0
		if self.curr == 'x':
			self.curr = self.curr*self.generate_wordlen()
			delay = self.generate_delay(len(self.curr))
		else:
			delay = self.generate_delay()
		#add the event and its assoc. time delay to the stack
		self.stack_message.append(self.curr)
		self.stack_time.append(delay)
		
		self.curr = choice		
		
	
#region: random methods ----------------------------------------------------------
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
			delay += self.exponential_dist(self.typing_speed)
		return delay
			
#region: stack to convo --------------------------------------------------------
	def make_convo_string(self):
		pass
	


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
	nodes =  ['ST', 'x', ' ', '[bkb]', '[bka]', '[snd]']
	
	#	st 	x  ' '	 bb  ba	   sn	
	matrix =[[0,   1,   0,   0,   0,  0    ], #st
				[0,   0, .61, .27, 0,   .13   ], #x  
				[0,   .50, .38, .09, 0,   .07  ], #' '
				[0,   0,   0,   .55, .45, 0  ], #bb
				[0,   .25, .25, .25, 0,	  .25  ], #ba
				[1,   0,   0,   0,   0,	  0  ],]#snd
		
	#nodes = ['A', '|', 'C']
	
	#          a, b, c
	#matrix = [[0, 5, 5],  #a
	#          [.33, .33, .34],#b
	#	  [0, 1, 0]]  #c
	
	
	C = ConvoPDA(matrix, nodes)
	#print C.nodes()
	#print C.edges(None, True)
	#print "---------------------------------------------------------------------------------------------------------------------------------------\n\n"
	C.start_pda()

	for i in range(1000):
		C.step()
	
	#print what's on the stack
	print '\n\n'
	print ''.join(C.stack_message)
	print '\n\n'