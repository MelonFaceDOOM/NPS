'''
Assumes DataDirectory = etc/tor
'''

import os

def create_torrc_files(tor_directory, torrc_count):
    
    if torrc_count > 1000:
        raise ValueError("provided torrc_count {} exceeds maximum value of 1000".format(torrc_count))
    
    with open("torrc_template", "r") as f:
        torrc_template = f.read()
    
    torrcs = []
    
    for i in range(torrc_count):
        
        SOCKSPort = 40000 + i
        ControlPort = 41000 + i
        
        file_path = os.path.join(tor_directory, "torrc.{}".format(i))
        
        if not os.path.isfile(file_path):
            with open(file_path, "w") as f:
                f.write(torrc_template.format(
                    SOCKSPort=SOCKSPort,
                    ControlPort=ControlPort,
                    i=i))
        
        torrcs.append({"path": file_path, "SOCKSPort": SOCKSPort, "ControlPort": ControlPort})
   
    return torrcs