from flask import Blueprint, render_template, request, url_for, redirect, flash
from networktoolssite import connection_functions

show_arp_select_blueprint = Blueprint('show_arp_select', __name__)
show_arp_result_blueprint = Blueprint('show_arp_result', __name__)


@show_arp_select_blueprint.route('/inputarpcheck', methods=['GET', 'POST'])
def show_arp_select():
    options = connection_functions.ConnectionMethods()
    l3_devices = options.get_arp_devices()
    return render_template('check_arp.html', url=url_for('show_arp_result.show_arp_result'), devices=l3_devices)


@show_arp_result_blueprint.route('/arpresults', methods=['GET', 'POST'])
def show_arp_result():  # Attempt to validate entered address then resolve the ARP mapping
    options = connection_functions.ConnectionMethods()

    l3_device = request.form.get('device_select')
    address = request.form.get('address_input')

    validate_mac = options.validate_format_mac(address)
    if not validate_mac:
        validate_ip = options.validate_ip_address(address)
        if not validate_ip:
            flash('Invalid input, try again')
            return redirect(url_for('show_arp_select.show_arp_select'))

    device = options.base_settings(l3_device)
    ip_mac_mapping = options.check_arp(device, address)
    flash(ip_mac_mapping)
    return redirect(url_for('index'))
