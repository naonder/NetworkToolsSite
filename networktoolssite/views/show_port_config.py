#!/usr/bin/env python3

from flask import Blueprint, render_template, request, url_for, session, flash, redirect
from networktoolssite import connection_functions

device_select_blueprint = Blueprint('device_select', __name__)
interface_select_blueprint = Blueprint('interface_select', __name__)
show_run_blueprint = Blueprint('interface_show_run', __name__)


@device_select_blueprint.route('/deviceselect', methods=['GET', 'POST'])
def dev_select():
    session.clear()
    options = connection_functions.ConnectionMethods()
    switches = options.get_l2_devices()

    return render_template('switches.html', template_switches=switches,
                           url=url_for('interface_select.interface_select'))


@interface_select_blueprint.route('/checkconfigurationinterfaceselect', methods=['GET', 'POST'])
def interface_select():
    switch = request.form.get('Switch')
    options = connection_functions.ConnectionMethods()
    device = options.base_settings(switch)
    session['switch'] = switch
    all_interfaces, failed = options.get_interfaces(device, switch)
    if failed:
        flash('Connection attempt to {} failed, try again'.format(switch))
        return redirect(url_for('index'))

    else:
        return render_template('interfaces.html', template_interfaces=all_interfaces,
                               url=url_for('interface_show_run.show_running'))


@show_run_blueprint.route('/viewintconfiguration', methods=['GET', 'POST'])
def show_running():
    interface = request.form.get('Interface')
    switch = session.get('switch')
    options = connection_functions.ConnectionMethods()
    device = options.base_settings(switch)
    running_config = options.get_port_configuration(device, interface)

    return render_template('running_config.html', template_config=running_config, running_interface=interface)
