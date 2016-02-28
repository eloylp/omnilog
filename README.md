<h1>OmniLog</h1>

<h3>Introduction</h3>
<p>
It was conceived with the idea on mind that not all IT infraestructures
or applications have a well defined and centralized logging system. This cant be a 
  reason to not "listen" a those remote logs on that servers. Log reviews can be very 
   painfull if you dont have a tool like this on your toolbelt.
</p>

<p>
With this application we can 'ssh in' all our servers simultaneously , get
each line of those logs of interest and write it on local files, show 
 them on a html fashion through its integrated HTTP server or launch notification events when one log entry arrives
 from servers. 
</p> 

<h3>Architecture</h3>
<p>
Broadly speaking we can think that this application have 2 layers. One of them is the main process omnilogd (daemon), 
that launches, controls and communicate the second layer, the app runnable sub components (threading involved).
</p>
<p>
The other components are all subcomponents , and some wrappers around third party libraries .
</p>

<h3>Installation</h3>
<p>
From pypi install as:
 pip install omnilog
</p>

<h3>Use it</h3>
<p>
omnilogd condig.json
</p>
<p>
Where config.json is the route to your configuration file. You can get an example of this in docs/config.dist.json.
</p>

<p>
For further and more detailed documentation visit the docs subfolder. If you simply "want to use it" this README
shoul be sufficient.
</p>