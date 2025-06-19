#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#######             
                              #                    
        ############ -#####+.##     ######         |	DataDrivenConstruction.io
        ##+########## .-##+ #-   .+########        |	
        ####     ####.     ..    #      ###        |	Dive into the future of flexibility in processing data 
        ####     .#+#.     #    .# .               |    without using BIM tools!
        ####     -#+#.    #.     .#.               |	
        ####      #+#.   ##-                       |	
        ####     ####        #.  #     -####       |	
        ############  .###+ #. ############        |
        #########.   +#### #+.   ########          |	If you have any questions, concerns or special requests,
                           #+                      |	please contact us at info@datadrivenconstruction.io	
                          #                        
                         #  

#------------------------------------Input data-----------------------------------

# Path address to the folder where RvtExporter.exe|IfcExporter.exe converter is located
path_conv = r'C:\DDC_2023\\'
# Path address of the folder where Revit|IFC files are located
path = r'C:\IFCprojects\\'

#-----------------------------------------------------------------------------------------

import os
import subprocess
import time

def convert_and_wait(path_conv, exporter_name, file_path, extension):
    subprocess.Popen([os.path.join(path_conv, exporter_name), file_path], cwd=path_conv)
    output_file = os.path.join(path, f"{os.path.splitext(file)[0]}_{extension}.xlsx")
    while not os.path.exists(output_file):
        time.sleep(0.5)
    print(f"Conversion Done for Project {os.path.splitext(file)[0]}")  
    
# Ensure output directory exists
os.makedirs(path, exist_ok=True)
# Conversion process from RVT and IFC
for file in os.listdir(path):
    full_path = os.path.join(path, file)
    if file.endswith('.ifc'):
        convert_and_wait(path_conv, 'IfcExporter.exe', full_path, 'ifc')
    elif file.endswith('.rvt'):
        convert_and_wait(path_conv, 'RvtExporter.exe', full_path, 'rvt')
        


# In[ ]:




