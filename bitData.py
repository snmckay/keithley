
class bitData:
        
        def __init__(self, numIn):
            self.bitNum = numIn
            self.x_data = []
            self.x_label = ""
            self.y_data = []
            self.y_label = ""

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

        def getBitNum(self):
            return self.bitNum