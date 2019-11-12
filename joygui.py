#!/usr/bin/env Python3
from __future__ import print_function
import PySimpleGUI as sg      
import odrive
from odrive.enums import *
import time
import math
from odrive.utils import *
#from selfupdate import update

#print ("check for updates")
#update()
#os.system("echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="1209", ATTR{idProduct}=="0d[0-9][0-9]", MODE="0666"' | sudo tee /etc/udev/rules.d/50-odrive.rules")
#os.system("sudo udevadm control --reload-rules")
#os.system("sudo udevadm trigger") # until you reboot you may need to do this everytime you reset the ODrive


print("finding an odrive...")
my_drive = odrive.find_any()
print (my_drive)

origin_theta =0
origin_fi=0
border_delta=10


# The callback functions
def button1():
    print('starting callibration of axis 1')
    my_drive.axis0.controller.config.vel_gain=0
    my_drive.axis1.controller.config.vel_gain=0

    # Calibrate motor and wait for it to finish
    print("ctrl+C to calibrate axis 0")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    my_drive.axis0.controller.config.vel_gain=0.0001
    my_drive.axis1.controller.config.vel_gain=0
    my_drive.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
    while my_drive.axis0.current_state != AXIS_STATE_IDLE:
        time.sleep(0.1)


    print("ctrl+C to calibrate axis 1")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    my_drive.axis0.controller.config.vel_gain=0
    my_drive.axis1.controller.config.vel_gain=0.0001
    my_drive.axis1.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
    while my_drive.axis1.current_state != AXIS_STATE_IDLE:
        time.sleep(0.1)

    #motors in closed loop
    my_drive.axis0.controller.config.vel_gain=0.0001
    my_drive.axis1.controller.config.vel_gain=0.0001
    my_drive.axis0.controller.config.pos_gain=50
    my_drive.axis1.controller.config.pos_gain=50
    my_drive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    my_drive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

def button2():
    print(dump_errors(my_drive, True))
    my_drive.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    my_drive.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

# Lookup dictionary that maps button to function to call
func_dict = {'1':button1, '2':button2}




sg.ChangeLookAndFeel('Dark')      

layout = [      
    
    [sg.Text('Stick of Joy', size=(30, 1), justification='center', font=("Helvetica", 25), relief=sg.RELIEF_RIDGE)],
    [sg.Frame('Axis 0',[ 
     [sg.Slider(range=(0, 100), orientation='h', size=(50, 10), default_value=0,key='axis0velgain', enable_events=True)],      #, enable_events=True
     [sg.Slider(range=(0, 100), orientation='h', size=(50, 10), default_value=0, key='axis0posgain', enable_events=True)],      
     [sg.Slider(range=(0, 100), orientation='h', size=(50, 20), default_value=0,key='axis0intgain', enable_events=True)],      
     ])],
    [sg.Frame('Axis 1',[      
     [sg.Slider(range=(0, 100), orientation='h', size=(50, 10), default_value=0,key='axis1velgain', enable_events=True)],      #, enable_events=True
     [sg.Slider(range=(0, 100), orientation='h', size=(50, 10), default_value=0, key='axis1posgain', enable_events=True)],      
     [sg.Slider(range=(0, 100), orientation='h', size=(50, 10), default_value=0,key='axis1intgain', enable_events=True)],      
     ])],
    [sg.Text (text = 'theta: ',size = (5,1)),sg.Text(text='',size=(20,1), key='theta'), sg.Text (text = 'fi: ',size = (5,1)), sg.Text(text='',size=(20,1), key='fi')],
    [sg.Graph(canvas_size=(250, 250), graph_bottom_left=(-1000,-1000), graph_top_right=(1000,1000), background_color='white', key='graph', tooltip='This is a cool graph!')],
    [sg.Radio('Back Driven', group_id ='mode', key='backdriven', size=(12, 1), enable_events=True,default=True)],      
    [sg.Radio('Hold Current', group_id ='mode',key='holdcurrent', size=(12, 1), enable_events=True)],      
    [sg.Radio('Square Walls', group_id ='mode', key = 'square', size=(12, 1), enable_events=True)],      
    [sg.Radio('Stick Drive', group_id ='mode', key= 'stick', size=(12, 1), enable_events=True)],  
    [sg.Button('Calibrate'),sg.Button('ERROR')]
]      


window = sg.Window('Stick of Joy', layout, default_element_size=(20, 1), grab_anywhere=False)


# Find a connected ODrive (this will block until you connect one)



# Event loop. Read buttons, make callbacks
while True:
    # Read the Window
    event, value = window.Read(timeout=1)
    theta=my_drive.axis0.encoder.shadow_count
    fi=my_drive.axis1.encoder.shadow_count

    if value.get('backdriven'):
        theta_setpoint=theta
        fi_setpoint=fi
        window.Element('graph').erase()

    if value.get('holdcurrent'):
        window.Element('graph').erase()

    if value.get('square'):
        if theta+origin_theta >500:
            my_drive.axis0.controller.config.vel_gain= value.get('axis0velgain')/100000
            my_drive.axis0.controller.config.pos_gain= value.get('axis0posgain')
            theta_setpoint=500-origin_theta -border_delta
        elif theta+origin_theta<-500:
            my_drive.axis0.controller.config.vel_gain= value.get('axis0velgain')/100000
            my_drive.axis0.controller.config.pos_gain= value.get('axis0posgain')
            theta_setpointt=-500-origin_theta +border_delta
        else:
            my_drive.axis0.controller.config.vel_gain=0.0000
            my_drive.axis0.controller.config.pos_gain=0
            theta_setpoint = theta

        if fi+origin_fi>500:
            my_drive.axis1.controller.config.vel_gain= value.get('axis1velgain')/100000
            my_drive.axis1.controller.config.pos_gain= value.get('axis1posgain')
            fi_setpoint=500-origin_fi -border_delta
        elif fi+origin_fi <-500:
            my_drive.axis1.controller.config.vel_gain= value.get('axis1velgain')/100000
            my_drive.axis1.controller.config.pos_gain= value.get('axis1posgain')
            fi_setpoint=-500-origin_fi +border_delta
        else:
            my_drive.axis1.controller.config.vel_gain=0.0000
            my_drive.axis1.controller.config.pos_gain=0
            fi_setpoint = fi

   
            
    my_drive.axis0.controller.pos_setpoint =theta_setpoint
    my_drive.axis1.controller.pos_setpoint = fi_setpoint

    window.Element('theta').Update(theta)
    window.Element('fi').Update(fi)
    window.Element('graph').DrawPoint((origin_theta + theta,origin_fi+fi),size=3, color='red')    


    if event in ('axis0velgain', None):
        my_drive.axis0.controller.config.vel_gain= value.get('axis0velgain')/100000
    if event in ('axis0posgain', None):
        my_drive.axis0.controller.config.pos_gain= value.get('axis0posgain')
    if event in ('axis0intgain', None):
        my_drive.axis0.controller.config.vel_integrator_gain= value.get('axis0intgain')/100000
    if event in ('axis1velgain', None):
        my_drive.axis1.controller.config.vel_gain= value.get('axis1velgain')/100000
    if event in ('axis1posgain', None):
        my_drive.axis1.controller.config.pos_gain= value.get('axis1posgain')
    if event in ('axis1intgain', None):
        my_drive.axis1.controller.config.vel_integrator_gain= value.get('axis1intgain')/100000

    if event in ('backdriven', None):
        print("back driven")
        window.Element('axis0velgain').Update(0)
        window.Element('axis0posgain').Update(0)
        window.Element('axis0intgain').Update(0)
        window.Element('axis1velgain').Update(0)
        window.Element('axis1posgain').Update(0)
        window.Element('axis1intgain').Update(0)

    if event in ('holdcurrent', None):
        print("hold current position")
        window.Element('axis0velgain').Update(15)
        window.Element('axis0posgain').Update(80)
        window.Element('axis0intgain').Update(0)
        window.Element('axis1velgain').Update(15)
        window.Element('axis1posgain').Update(80)
        window.Element('axis1intgain').Update(0)
        theta_setpoint=theta
        fi_setpoint=fi
        origin_theta =-theta
        origin_fi=-fi

    if event in ('square', None):
        print("virtual square")
        origin_theta =-theta
        origin_fi=-fi
        window.Element('graph').DrawRectangle((-530,-530), (530,530), line_color='purple')
        window.Element('axis0velgain').Update(70)
        window.Element('axis0posgain').Update(22)
        window.Element('axis0intgain').Update(5)
        window.Element('axis1velgain').Update(70)
        window.Element('axis1posgain').Update(22)
        window.Element('axis1intgain').Update(5)

    if event in ('stick', None):
        print("stick drive")
        origin_theta =-theta
        origin_fi=-fi
        window.Element('graph').DrawLine((-500,-500), (-500,500), color='purple')
        window.Element('graph').DrawLine(( 0,-500), (0,500), color='purple')
        window.Element('graph').DrawLine((500,0), (500,-500), color='purple')
        window.Element('graph').DrawLine((-500,0), (500,0), color='purple')
        
        window.Element('axis0velgain').Update(0)
        window.Element('axis0posgain').Update(0)
        window.Element('axis0intgain').Update(0)
        window.Element('axis1velgain').Update(0)
        window.Element('axis1posgain').Update(0)
        window.Element('axis1intgain').Update(0)
        
    if event in ('Quit', None):
        break
    if event in ('Calibrate', None):
        button1()
    if event in ('ERROR', None):
        button2()
    # Lookup event in function dictionary
    try:
        func_to_call = func_dict[event]   # look for a match in the function dictionary
        func_to_call()                    # if successfully found a match, call the function found
    except:
        pass

window.Close()

    # All done!
sg.PopupOK('Done')     
