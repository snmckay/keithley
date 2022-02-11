
class bitData:  
    
        def __init__(self, numIn):
            self.bitNum = numIn
            self.x_data = []
            self.x_label = ""
            self.y_data = []
            self.y_label = ""
            self.y2_data = []
            self.y2_label = ""

        def setXData(self, data_in):
            self.x_data = data_in
            return
        
        def getXData(self):
            return self.x_data
        
        def appendXData(self, data_in):
            self.x_data.append(data_in)
            return

        def setYData(self, data_in):
            self.y_data = data_in
            return
        
        def getYData(self):
            return self.y_data

        def setXLabel(self, label_in):
            self.x_label = label_in
            return

        def appendYData(self, data_in):
            self.y_data.append(data_in)
            return
        
        def setYLabel(self, label_in):
            self.y_label = label_in
            return
        
        def setY2Data(self, data_in):
            self.y_data = data_in
            return
        
        def getY2Data(self):
            return self.y_data
        
        def setY2Label(self, label_in):
            self.y_label = label_in
            return

        def getBitNum(self):
            return self.bitNum
        
        def getAverages(self):
            averagedX = []
            averagedY = []
            averaged = []
            y_col_pos = 0
            for collection in self.x_data:
                y_pos = 0
                if len(collection) > 5:
                    for data in collection:
                        if float(data) > 0:
                            if data not in averagedX:
                                #print("Adding: " + str(data))
                                averagedX.append(data)
                                averagedY.append((self.y_data[y_col_pos])[y_pos])
                            else:
                                averagedY[averagedX.index(data)] = averagedY[averagedX.index(data)] + (self.y_data[y_col_pos])[y_pos]
                        y_pos = y_pos + 1
                y_col_pos = y_col_pos + 1
            for dat in averagedY:
                dat = dat/y_col_pos
            print("Averaged lengths: " + str(len(averagedX)) + "/" + str(len(averagedY)))
            averaged.append(averagedX)
            averaged.append(averagedY)
            return averaged
            
                    
                    