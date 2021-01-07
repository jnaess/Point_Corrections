#!/usr/bin/env python
# coding: utf-8

# In[52]:


get_ipython().run_line_magic('matplotlib', 'notebook')

import math as m
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.tri as tri

track = False

def trackPrint(string):
    """
    If the global variable 'track' is true then it will add these prints
    """
    if track:
        print(string)
        
def d(deg,min=0,sec=0):
    """
    Enter the degree, minute, second angle
    returns the angle in radians
    """
    return m.radians(deg + min/60 + sec/3600)

def dms(dd):
    """
    Takes in angle in radians
    returns andgle in degree, minute, second
    """
    dd = m.degrees(dd)
    mnt,sec = divmod(dd*3600,60)
    deg,mnt = divmod(mnt,60)
    return deg,mnt,sec

class Survey():
    def __init__(self):
        """
        To help contain east set of measurements
        """
        self.meas = []
        
    def write(self):
        """
        Iterates through list of data to print each row
        """
        tackPrint("new set")
        for data in self.meas:
            data.write()
            
    def orientation_correction(self):
        """
        Find the orientation correction to apply 
        to this bunch of measurements
        
        returns
        Orientation correction in d
        """
        E5 = Point("E5",  700893.200, 63095.110, 1107.150)
        WS2 = Point("WS2", 700831.459, 63043.566, 1106.683)
        
        #Calculated bearing
        CalcB = m.atan((WS2.E-E5.E)/(WS2.N-E5.N))
        
        #Orientation correction
        #New orientation correct for each set
        OC = self.add((CalcB - self.meas[0].B),d(180))
            
        #correct all measurements in the bunch
        for mea in self.meas:
            try:
                mea.B = self.add(mea.B,OC)
            except:
                print("oh well")
    def add(self, m1, m2):
        """
        Adds the measurements and checks to see if over 360, 
        if so then it subtracts 360
        
        m1: d
        m2: d
        
        returns:
        d
        """
        #add the two in radians together
        mea = m1 + m2
        
        #check to see if too large
        if dms(mea)[0] > 360 :
            mea = mea-d(360)
  
        return mea

    def misclosure_error(self):
        """
        Checks to see if the misclosure is greater than 10arc sec
        If it is then applied equal shift to the second half of the data
        
        Assumes no misclosure larger than 45 arc sec
        Assumes no measurements within 359 or 0 degrees other than datum
        """
        #find index fro next datum (sometimes 6 sometime 5)
        #"i" is the index
        i = 0
        count = 0
        for mea in self.meas:
            #checks to see if the degrees is 0 or 359 (corr was 230)
            trackPrint("Degrees is: "+ str(dms(mea.B)[0]))
            if dms(mea.B)[0] == 0 or dms(mea.B)[0] == 359:
                i = count
            count = count + 1
            
        
        #if i is 0 then no datum was found
        
        if i == 0:
            trackPrint("No second set found")
        else:
            trackPrint("Equal Shift Being Checked")
            
            #check miscolsure
            misc = 0
            first = dms(self.meas[0].B)[2]
            second = dms(self.meas[i].B)[2]

            #make misclosure
            if second > 45:
                misc = 60 - second + first
            else:
                misc = second - first

            #is misclosure large enough?
            if m.sqrt(misc*misc) > 10:
                trackPrint("Equal Shift Being Applied for a misc of: "+str(misc))
                #find misclosure correction
                misc_corr = misc / (len(self.meas) - i)
                total_corr = 0

                #apply to all indices in self.misc that are equal in the second data set
                while i < len(self.meas):
                    #add a new equal shift
                    total_corr = misc_corr + total_corr

                    #adds the total correction contactenated to a whole number
                    trackPrint(int(total_corr))
                    self.meas[i].B = self.meas[i].B + d(0,0,int(total_corr))

                    #increments count
                    i = i + 1
            else:
                trackPrint("Equal Shift Not Applied for a misc of: "+str(misc))
                
    def VD_HD(self):
        """
        Initiates the vertical and horizontal change of all sets
        """
        for mea in self.meas:
            mea.V_Dist()
            mea.H_Dist()
            
    def set_coords(self, p, instrument, prism):
        """
        Sets the height, easting, and northing in a point object in each set
        """
        for mea in self.meas:
            mea.set_coords(p, instrument, prism)
        
            

class Point():
    def __init__(self, name, E, N, H):
        """
        name, String of point name
        E, Easting of point
        N, Northing of Point
        H, Height of point
        """
        self.name = name
        self.E = E
        self.N = N
        self.H = H
        
class Set():
    def __init__(self,Bd,Bm,Bs,
                 Zd, Zm, Zs, D, name="N/A"):
        """
        Input:
        name, name of point
        Bd, degree
        Bm, minutes
        Bs, seconds
        Zd, degree
        Zm, minute
        Zs, seconds
        D
        
        Output:
        name -- name of the point taken
        B -- the bearing to the point (radians)
        Z -- the zenith angle to the point (radians)
        D -- slope distance (meters)
        """
        self.name = name
        self.B = self.d(Bd,Bm,Bs)
        self.Z = self.d(Zd,Zm,Zs)
        self.D = D
                
        
    def write(self):
        """
        Should print the destails of this set of data
        """
        print("-------------")
        print(self.name)
        print("B: "+str(dms(self.B)))
        print("Z: "+str(dms(self.Z)))
        print("S: "+str(self.D))
        
    def d(self,deg,min,sec):
        """
        Enter the degree, minute, second angle
        returns the angle in radians
        """
        return m.radians(deg + min/60 + sec/3600)

    def dms(self,dd):
        """
        Takes in angle in radians
        returns andgle in degree, minute, second
        """
        dd = m.degrees(dd)
        mnt,sec = divmod(dd*3600,60)
        deg,mnt = divmod(mnt,60)
        return deg,mnt,sec
    
    def H_Dist(self):
        """
        D*m.cos(self.Z)
        
        initiates H_D: float of horizontal distance
        """
        self.H_D = self.D*m.sin(self.Z)
        
    def V_Dist(self):
        """
        D*m.cos(self.Z)
        
        initiates V_D: float of vertical distance change
        """
        self.V_D = self.D*m.cos(self.Z)
        
    def change_E(self):
        """
        Finds the change in Easting
        
        Calls the H_Dist to make sure that the variable is initated
        Then does the calculations
        
        returns: 
        float: Eastings change
        """
        self.H_Dist()
        
        return m.sin(self.B)*self.H_D
        
    def change_N(self):
        """
        Finds the change in Northing
        
        Calls the H_Dist to make sure that the variable is initated
        Then does the calculations
        
        returns: 
        float: Northing change
        """
        self.H_Dist()
        
        return m.cos(self.B)*self.H_D
    
    def change_V(self, instrument, prism):
        """
        Find the change in height
        
        Input:
        Instrument height
        Prism Height
        
        Returns:
        float: Vertical change from point
        """
        self.V_Dist()
        
        return self.V_D - instrument + prism
    
    def set_coords(self, p, instrument, prism):
        """
        Set the coordinates to the set of data
        
        Input:
        Point p: of the location where measurements were taken from
        
        Initiates: 
        self.point: Point type object
        """
        
        E = p.E + self.change_E()
        N = p.N + self.change_N()
        V = p.H + self.change_V(instrument, prism)
        
        self.point = Point(self.name, E, N, V)
        
class Project():
    def __init__(self, filename):
        """
        Contains a list of all of the Surveys to do stuff to
        
        Input:
        filename: string of the cvs to read
        
        Output:
        self.project: list of the surveys
        """
        self.read(filename)
        
    def read(self, filename):
        """
        Initializes the project by reading in all sets of the data
        """
        trackPrint("Reading in Data")
        Data = pd.read_csv(filename)

        #adds a column of saying whether it's NaN or a value
        Data.loc[Data['Bearing'].isnull(),'value_is_NaN'] = 'Yes'
        Data.loc[Data['Bearing'].notnull(), 'value_is_NaN'] = 'No'
        
        self.project = [Survey()]
        i = 0

        for index, row in Data.iterrows():
            #check to see if it is a new dataset
            #if it is then it sets up a new Survey set to be entered
            if Data.loc[index][7] == "Yes":
                trackPrint("Appending new survey")
                i = i + 1
                self.project.append(Survey())
            elif i<59:
                #append a new measurement to the Survey that is currently being made
                trackPrint("Adding to exsisting survey")
                self.project[i].meas.append(
                            Set(Data.loc[index][0],
                                Data.loc[index][1],
                                Data.loc[index][2],
                                Data.loc[index][3],
                                Data.loc[index][4],
                                Data.loc[index][5],
                                Data.loc[index][6],
                                Data.loc[index][7]))

    def write(self):
        """
        Output as a dataframe to assist with visualization
        
        returns: dataframe
        """
        df = pd.DataFrame(columns=['Point','B_D','B_M','B_S','Z_D','Z_M','Z_S','Change_E','Change_N','H_Dist',
                                   'V_Change',
                                  'Easting','Northing','Vertical'])
        count = 0
        for survey in self.project:
            for mea in survey.meas:
                if count < 60:
                    df.loc[count] = [mea.name,
                                        dms(mea.B)[0],
                                        dms(mea.B)[1],
                                        dms(mea.B)[2],
                                        dms(mea.Z)[0],
                                        dms(mea.Z)[1],
                                        dms(mea.Z)[2],
                                        mea.change_E(),
                                        mea.change_N(),
                                        mea.H_D,
                                        mea.V_D,
                                        mea.point.E,
                                        mea.point.N,
                                        mea.point.H]
                    count = count + 1
                
        return df
                
    def orientation_correction(self):
        """
        Applied orientation correction to all surveys
        """
        for survey in self.project:
            survey.orientation_correction()
            
    def misclosure_error(self):
        """
        Applied equal shift orientation correction to all surveys
        """
        for survey in self.project:
            survey.misclosure_error()
            
    def VD_HD(self):
        """
        Initiates vertical distance and horizontal distance change
        Should not be applied until desired corrections are done
        """
        for survey in self.project:
            survey.VD_HD()
            
    def set_coords(self, point, instrument, prism):
        """
        Sets the N, E, V of each point
        """
        for survey in self.project:
            survey.set_coords(point, instrument, prism)
            
    def plot_2D(self):
        """
        Plots a scatter plot of the given points in a 2d graph
        
        """
        #extract the regular data in a dataframe
        df = self.write()
        
        X = df['Easting'].tolist()
        Y = df['Northing'].tolist()
        labels = df['B_M'].tolist()
        
        #set up the figure and plot it
        fig, ax = plt.subplots()
        ax.scatter(X, Y, color = '#D471D0')
        
        #label title and axises
        plt.title('Survey Points Recorded')
        plt.xlabel('Easting')
        plt.ylabel('Northing')
        
        #colouring
        ax.set_facecolor('#c2ecc3')
        ax.set_clip_on(False)

        
        #number all points according to the dataframe index
        for i, txt in enumerate(range(len(X))):
            ax.annotate(txt, (X[i], Y[i]))
            
        plt.savefig('2DPlot.jpg', dpi = 200)
        
    def plot_3D(self):
        """
        Plots a 3D representation of the points
        """
        #extract the regular data in a dataframe
        df = self.write()
        
        ax = plt.axes(projection='3d')
        
        
        Z = df['Vertical'].tolist()
        X = df['Easting'].tolist()
        Y = df['Northing'].tolist()
        label = df['B_M'].tolist()
               
        ax.scatter3D(X, Y, Z, label, c=Z)
        
    def output_coords(self, name="Final_Coordinates.csv"):
        """
        Will output the current set of corrdinates
        
        Input:
        name: string of the output file **make sure to add a .csv to the end**
        
        saves a csv "Final_Coordinates.csv"
        """
        #take in the completed dataframe
        df = self.write()
        
        #these are the columns we're taking
        df = df[['Point',"Easting", 'Northing', 'Vertical']]
        
        #save the file
        df.to_csv(name, index=True)        


# In[53]:


#survey is a list of the different data inputs
data = Project("project1.csv") 

data.misclosure_error()

#apply to orientation correction
data.orientation_correction()

#make the vertical distance and horizontal distance changes
data.VD_HD()

E5 = Point("E5",  700893.200, 63095.110, 1107.150)
data.set_coords(E5, 1.55, 2.05)

#check and apply rounding correction via equal shift
data.write().to_csv("Cumulative_Data.csv", index=True)

#data.output_coords()
#data.plot_2D();


# In[57]:





# In[ ]:



    



# In[ ]:





# In[ ]:





# In[ ]:




