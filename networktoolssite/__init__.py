#!/usr/bin/env python3

import os
from flask import Flask
from networktoolssite.views.show_port_config import *
from networktoolssite.views.configure_access_port import *
from networktoolssite.views.clear_sticky_mac import *
from networktoolssite.views.show_arp import *

networktoolssite = Flask(__name__)
networktoolssite.secret_key = os.urandom(32)

# Set up blueprints for checking an interface configuration
networktoolssite.register_blueprint(device_select_blueprint)
networktoolssite.register_blueprint(interface_select_blueprint)
networktoolssite.register_blueprint(show_run_blueprint)

# Set up blueprints for configuring an access port port
networktoolssite.register_blueprint(configure_access_port_select_blueprint)
networktoolssite.register_blueprint(configure_access_port_option_select_blueprint)
networktoolssite.register_blueprint(configure_access_port_option_check_blueprint)

# Set up blueprints for clear sticky MAC addresses
networktoolssite.register_blueprint(clear_sticky_mac_select_blueprint)
networktoolssite.register_blueprint(clear_sticky_mac_option_select_blueprint)
networktoolssite.register_blueprint(clear_sticky_mac_complete_blueprint)

# Set up blueprints for checking ARP entries
networktoolssite.register_blueprint(show_arp_select_blueprint)
networktoolssite.register_blueprint(show_arp_result_blueprint)


from networktoolssite.views import main_menu

if __name__ == "__main__":
    networktoolssite.run()
