from flask import Blueprint, render_template, request, url_for, session, redirect, flash
from networktoolssite import connection_functions

clear_sticky_mac_select_blueprint = Blueprint('clear_sticky_mac_select', __name__)
clear_sticky_mac_option_select_blueprint = Blueprint('clear_sticky_mac_option_select', __name__)
clear_sticky_mac_complete_blueprint = Blueprint('clear_sticky_mac_complete', __name__)


@clear_sticky_mac_select_blueprint.route('/clearstickydeviceselect', methods=['GET', 'POST'])
def clear_sticky_mac_select():  # Presents a dropdown of devices
    options = connection_functions.ConnectionMethods()
    switches = options.get_l2_devices()

    return render_template('switches.html', template_switches=switches,
                           url=url_for('clear_sticky_mac_option_select.clear_sticky_mac_option_select'))


@clear_sticky_mac_option_select_blueprint.route('/clearstickyoptions', methods=['GET', 'POST'])
def clear_sticky_mac_option_select():  # Presents options for user to choose from
    switch = request.form.get('Switch')
    options = connection_functions.ConnectionMethods()
    device = options.base_settings(switch)
    session['switch'] = switch
    all_interfaces, failed = options.get_interfaces(device, switch)
    if failed:
        flash('Connection attempt to {} failed, try again'.format(switch))
        return redirect(url_for('index'))
    else:
        return render_template('clear_sticky_template.html',
                               url=url_for('clear_sticky_mac_complete.clear_sticky_mac_complete'),
                               template_interfaces=all_interfaces)


@clear_sticky_mac_complete_blueprint.route('/stickyclear', methods=['GET', 'POST'])
def clear_sticky_mac_complete():  # Attempts to clear a sticky MAC or interface
    switch = session.get('switch')
    options = connection_functions.ConnectionMethods()
    device = options.base_settings(switch)
    clear_type = request.form.get('clear_type')
    if clear_type == 'clear_sticky':
        validate_mac = options.validate_format_mac(request.form.get('sticky_mac_address'))
        if not validate_mac:
            flash('Invalid input, try again')
            return redirect(url_for('clear_sticky_mac_select.clear_sticky_mac_select'))
        options.clear_sticky_mac(device, validate_mac)
        flash('MAC address {} as been cleared'.format(request.form.get('sticky_mac_address')))
        return redirect(url_for('index'))
    elif clear_type == 'clear_interface':
        options.clear_sticky_interface(device, request.form.get('interface_select'))
        flash('Interface {} sticky MAC addresses have been cleared'.format(request.form.get('interface_select')))
        return redirect(url_for('index'))
