import matplotlib.pyplot as plt

"""
 This class deals with plotting
"""
class DataPlotter():
    def __init__(self, subplots=1, window=25):
        self.window = window
        self.subplots = subplots

        fig = plt.figure()
        plt.ion()

        self.values = [[] for i in range(subplots)] 
        self.ax = []
        for i in range(subplots):
            self.ax.append(fig.add_subplot(subplots,1,i+1)) # subplots start with 1

    def plot(self, seq):
        if self.subplots != len(seq):
            return
	for i in range(self.subplots):
            self.values[i].append(seq[i])

        if(len(self.values[0]) > self.window): #drop one
   	    for i in range(subplots):
                self.values[i] = self.values[i][1:]

	for i in range(self.subplots):
            self.ax[i].clear()
            self.ax[i].plot(self.values[i])

        plt.pause(0.01)

if __name__ == "__main__":
    # used for testing only
    ui = DataPlotter(subplots=3)
    ui.plot([4, 5, 6])
    ui.plot([6, 4, 8])
    ui.plot([5, 5, 3])
