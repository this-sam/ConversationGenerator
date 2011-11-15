class ConversationGenerator:
	
	global os, random
	import os, random
	
        #---------------------------------------------
        global DISTRIBUTION
        DISTRIBUTION = {};
        DISTRIBUTION['A'] = {'x':.7, ' ':.95, '\n[newline]':.955, '[del]':1}
        
	def __init__(self):
	    print DISTRIBUTION
            self.printSomeSentences()            
                        
        def printSomeSentences(self):
            outstring = ""
            for i in range(1000):
                n = random.random()
                prevCap = 0
                for key, value in DISTRIBUTION['A'].iteritems():
                    print prevCap
                    if prevCap < n < value:
                        outstring += key
                        prevCap = value
                        break
                    prevCap = value
                    
            print outstring
            
if __name__ == '__main__':
	gen = ConversationGenerator()