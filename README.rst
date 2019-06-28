NetworkToolsSite
================


Web based GUI written in Python3 and HTML. Uses Nornir on the backend for device connections

Source Code
-----------

https://github.com/naonder/NetworkToolsSite



Notes
-------------

| While Flask comes w/ a built-in server, you should use a production ready server
| Also keep in mind this is in the early stages of development (not feature complete) so use is as-is

Setup
-----
| You'll need to setup defaults, groups, and hosts for Nornir and the site to function correctly
| See the example .yaml files. Keep in mind that the groups can be changed in the groups file.
| If you do that, make sure to adjust the code in connectionfunctions.py to reflect your groups
| Lastly, the access_port.j2 template can be modified as you desire

Screenshots
-----------
.. image:: /images/main_menu.png
   :width: 100px
   :height: 100px
.. image:: /images/device_select.png
.. image:: /images/interface_select.png
.. image:: /images/port_type_select.png
.. image:: /images/user_port.png
.. image:: /images/other_port.png
.. image:: /images/arp.png
.. image:: /images/arp_response.png



Author
------
naonder <nate.a.onder@gmail.com>
