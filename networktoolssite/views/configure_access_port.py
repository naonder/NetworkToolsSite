#!/usr/bin/env python3

from flask import Blueprint, render_template, request, url_for, session, redirect, flash
from networktoolssite import connection_functions

configure_access_port_select_blueprint = Blueprint('configure_access_port_select', __name__)
configure_access_port_option_select_blueprint = Blueprint('configure_access_port_option_select', __name__)
configure_access_port_option_check_blueprint = Blueprint('configure_access_port_option_check', __name__)


@configure_access_port_select_blueprint.route('/accessportdeviceselect', methods=['GET', 'POST'])
def configure_access_port_select():
    session.clear()
    options = connection_functions.ConnectionMethods()
    switches = options.get_l2_devices()

    return render_template('switches.html', template_switches=switches,
                           url=url_for('configure_access_port_option_select.configure_access_port_option_select'))


@configure_access_port_option_select_blueprint.route('/accessportselect', methods=['GET', 'POST'])
def configure_access_port_option_select():
    switch = request.form.get('Switch')
    options = connection_functions.ConnectionMethods()
    device = options.base_settings(switch)
    session['switch'] = switch
    all_interfaces, failed = options.get_interfaces(device, switch)
    if failed:
        flash('Connection attempt to {} failed, try again'.format(switch))
        return redirect(url_for('index'))
    else:
        session['vlans'] = options.get_vlans(switch, device)
        return render_template('access_port_template.html',
                               url=url_for('configure_access_port_option_check.configure_access_port_option_check'),
                               template_interfaces=all_interfaces, vlans=session.get('vlans'))


@configure_access_port_option_check_blueprint.route('/accessportoptions', methods=['GET', 'POST'])
def configure_access_port_option_check():
    switch = session.get('switch')
    options = connection_functions.ConnectionMethods()
    interface = request.form.get('interface_select')
    port_type = request.form.get('port_type')
    access_vlan = request.form.get('access_select')
    voice_vlan = request.form.get('voice_select', None)
    description = request.form.get('interface_description')
    session['interface'] = interface
    device = options.base_settings(switch)
    neighbor_check = options.check_cdp_neighbor(switch, device, interface)

    if neighbor_check:
        for neighbor in neighbor_check:
            flash('{} was detected on port {}. Select a different port'.format(neighbor, interface))
        return redirect(url_for('index'))

    else:

        config = render_template('access_port.j2', interface=interface, access_vlan=access_vlan,
                                 voice_vlan=voice_vlan, description=description, port_type=port_type)
        options.push_configuration(device, interface, config)
        running_config = options.get_port_configuration(device, interface)
        return render_template('running_config.html', template_config=running_config, running_interface=interface)
