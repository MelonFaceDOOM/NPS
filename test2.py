SOCKSPort=9050
ControlPort=9051
torrc_dir="/etc/tor/test"

with open("torrc_template", "r") as f:
    torrc_template = f.read()

with open(torrc_dir, "w") as f:
    f.write(torrc_template.format(
        SOCKSPort=SOCKSPort,
        ControlPort=ControlPort))
