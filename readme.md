Requires Apache, Python3 and Perl and modules. It'll complain and tell you what modules are not installed when you run it.

Put barkfront2.pl in your cgi-bin directory

Put bark_graphs.py in /usr/local/bin

bark.txt has this format.
F |Bark Detected | Tue Aug  1 14:58:40 2023 | Level: 0.083862305 | dB: -43.0573281981549

Decibels are adjusted for a 40' distance.

Put this in your crontab:
15,45 * * * * /usr/bin/python3 /usr/local/bin/bark_graphs.py

Configure Agent DVR with CallURL (see AgentDVRCallURL.png)

Graph pdf is saved to /var/www/html

