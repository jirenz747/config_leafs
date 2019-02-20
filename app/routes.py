# -*- coding: utf-8 -*-

from app import app
from flask import render_template, redirect, url_for, request, flash, session
from app.read_yml import ReadYml

from flask import jsonify
from app import juniper
import json
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import ldap


@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('login.html')

    y = ReadYml()
    locations = y.get_location()
    return render_template('menu.html', locations=locations)


@app.route('/login', methods=['POST', 'GET'])
def login():
    try:
        password = request.form['password']
        username = request.form['username']
    except KeyError:
        return render_template('login.html')

    if len(username) == 0 or len(password) == 0:
        flash('Enter login and password!')
        return render_template('login.html')
    y = ReadYml()
    if y.config_yml['Global_parametrs']['authentication_web']['ldap']['use'].lower() in 'yes':

        LDAP_SERVER = y.config_yml['Global_parametrs']['authentication_web']['ldap']['ldap_server']
        LDAP_USERNAME = '{}@{}'.format(username, y.config_yml['Global_parametrs']['authentication_web']['ldap']['ldap_domain'])
        LDAP_PASSWORD = password
        base_dn = y.config_yml['Global_parametrs']['authentication_web']['ldap']['base_dn']
        permission_groups = y.config_yml['Global_parametrs']['authentication_web']['ldap']['domain_groups']
        ldap_filter = 'userPrincipalName={}@{}'.format(username, y.config_yml['Global_parametrs']['authentication_web']['ldap']['ldap_domain'])
        attrs = ['memberOf']
        try:
            ldap_client = ldap.initialize(LDAP_SERVER)
            ldap_client.set_option(ldap.OPT_REFERRALS, 0)
            ldap_client.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)
        except ldap.INVALID_CREDENTIALS:
            ldap_client.unbind()
            flash('Wrong login or password!')
            return render_template('login.html')
        except ldap.SERVER_DOWN:
            flash('LDAP server is not available!')
            return redirect(url_for('login'))
        groups = ldap_client.search_s(base_dn, ldap.SCOPE_SUBTREE, ldap_filter, attrs)[0][1]['memberOf']
        ldap_client.unbind()
        for group in groups:
            for permission_group in permission_groups:
                if permission_group in group.decode("utf-8"):
                    session['logged_in'] = True
        if session['logged_in'] is False:
            flash('Wrong login or password!')
            return render_template('login.html')
    else:
        if username == y.config_yml['Global_parametrs']['authentication_web']['plain_text_password']['username'] and \
                password == y.config_yml['Global_parametrs']['authentication_web']['plain_text_password']['password']:
            session['logged_in'] = True
        else:
            flash('Wrong login or password!')
            return render_template('login.html')
    return redirect(url_for('index'))


@app.route('/test_toast')
def test_toast():
    if not session.get('logged_in'):
        return render_template('login.html')

    return render_template('test.html')


@app.route('/change_location', methods=['POST'])
def change_location():
    location = request.form['location']
    if 'None' in location:
        return jsonify({'racks': ''})
    y = ReadYml()
    racks = y.get_rack(location)
    return jsonify({'racks': racks})


@app.route('/config_port', methods=['POST'])
def config_port():
    location = request.form['location']
    rack = request.form['rack']
    port = request.form['port']
    type_port = request.form['type_port']
    description = '"' + request.form['description'] + '"'
    mtu = request.form['mtu']
    speed = request.form['speed']
    vlans = request.form['vlan']
    set_juniper = []
    set_juniper.append('delete interfaces {}'.format(port.replace('xe', 'ge')))
    set_juniper.append('delete interfaces {}'.format(port.replace('ge', 'xe')))
    if speed == '1Gbit':
        port = port.replace('xe', 'ge')
    else:
        port = port.replace('ge', 'xe')

    y = ReadYml()
    ip = y.config_yml[location][rack]['device_ip']
    set_juniper.append('set interfaces {} mtu {} '.format(port, mtu))
    set_juniper.append('set interfaces {} description {}'.format(port, description))
    set_juniper.append('set interfaces {} unit 0 family ethernet-switching interface-mode {}'.format(port, type_port))
    set_juniper.append('set interfaces {} unit 0 family ethernet-switching vlan members [{}]'.format(port, vlans))
    return render_template('test.html', set_juniper=set_juniper, ip=ip)


@app.route('/configs_ports', methods=['POST'])
def configs_ports():
    location = request.form['location']
    rack = request.form['rack']
    json_interfaces = request.form['interfaces']
    interfaces = json.loads(json_interfaces)
    set_juniper = []
    y = ReadYml()
    login = y.config_yml['Global_parametrs']['authentication_network_device']['username']
    password = y.config_yml['Global_parametrs']['authentication_network_device']['password']
    ip = y.config_yml[location][rack]['device_ip']
    for interface in interfaces:
        port = interface[0:3] + interface[3:].replace('-', '/')
        set_juniper.append('delete interfaces {}'.format(port.replace('xe', 'ge')))
        set_juniper.append('delete interfaces {}'.format(port.replace('ge', 'xe')))
        if interfaces[interface]['speed'] == '1000mbps':
            port = port.replace('xe', 'ge')
        else:
            port = port.replace('ge', 'xe')
        description = '"' + interfaces[interface]['description'] + '"'
        if len(description) != 2:
            set_juniper.append('set interfaces {} description {}'.format(port, description))
        set_juniper.append('set interfaces {} mtu {} '.format(port, interfaces[interface]['mtu']))
        port_mode = interfaces[interface]['port_mode']
        if 'access' in port_mode:
            vlan = interfaces[interface]['vlan']
        else:
            vlan =' '.join(interfaces[interface]['vlan'])
        set_juniper.append('set interfaces {} unit 0 family ethernet-switching interface-mode {}'.format(port, port_mode))
        set_juniper.append('set interfaces {} unit 0 family ethernet-switching vlan members [{}]'.format(port, vlan))

    dev = Device(host=ip, user=login, password=password, port='22')
    dev.open(normalize=True)
    with Config(dev, mode='exclusive') as cu:
        for command in set_juniper:
            cu.load(command, format='set', ignore_warning=True)
        cu.commit()
    dev.close()
    return render_template('test.html', set_juniper=set_juniper, ip=ip, interfaces=interfaces)


@app.route('/change_rack', methods=['POST'])
def change_rack():
    location = request.form['location']
    rack = request.form['rack']
    y = ReadYml()
    device = y.config_yml[location][rack]['device_ip']
    device_count = int(y.config_yml[location][rack]['device_count'])
    port_count = int(y.config_yml[location][rack]['port_count'])
    login = y.config_yml['Global_parametrs']['authentication_network_device']['username']
    password = y.config_yml['Global_parametrs']['authentication_network_device']['password']
    d = juniper.get_juniper(device, login=login, password=password)
    if type(d) is str:
        return render_template('errors.html', errors=d)
    interfaces = []
    mac_table = []
    count = 0
    for interface in juniper.output_interface(list(d['interface'].keys()), ['ae']):
        flap = d['interface'][interface]['flap']
        flap = flap[flap.find('('):]
        interfaces.append({
            'interface': interface,
            'description': d['interface'][interface]['description'],
            'status': d['interface'][interface]['status'],
            'speed': d['interface'][interface]['speed'],
            'mtu': d['interface'][interface]['mtu'],
            'port_mode': d['interface'][interface]['port-mode'],
            'vlan': d['interface'][interface]['vlans'],
            'flap': flap,
            'mac': d['interface'][interface]['mac'],
            'interface_for_jquery': interface})
        if len(d['interface'][interface]['mac']) == 0:
            continue
        mac_table.append({interface: {}})
        all_mac_count = 0
        for vlan in d['interface'][interface]['mac']:
            mac_table[count][interface][vlan] = {'mac_address': {}}
            for mac in d['interface'][interface]['mac'][vlan]:
                if mac in d['arp']:
                    mac_table[count][interface][vlan]['mac_address'][mac] = d['arp'][mac]
                else:
                    mac_table[count][interface][vlan]['mac_address'][mac] = '---'
            count_mac = len(mac_table[count][interface][vlan]['mac_address'])
            mac_table[count][interface][vlan]['count_mac'] = count_mac
            all_mac_count += count_mac
        mac_table[count][interface]['interface_count'] = all_mac_count
        count += 1

    for interface in juniper.output_interface(list(d['interface'].keys()), ['xe', 'ge'], port_count, device_count):

        if not interface in d['interface']:
            interface_for_jquery = interface.replace('/','-').replace('/','-')

            if 'xe' in interface:
                speed = '10Gbps'
            elif 'ge' in interface:
                speed = '1000mbps'
            interfaces.append({
                'interface': interface,
                'description': 'do not have in configuration',
                'status': 'none',
                'speed': speed,
                'mtu': 'none',
                'port_mode': 'none',
                'vlan': 'none',
                'flap': 'none',
                'mac': 'none',
                'interface_for_jquery': interface_for_jquery})
            continue
        # for ID in HTML(jquery).
        interface_for_jquery = interface.replace('/', '-').replace('/', '-')

        edit = 'true'
        if interface in y.config_yml[location][rack]['exclude_ports']:
            edit = 'false'
        flap = d['interface'][interface]['flap']
        flap = flap[flap.find('('):]
        if 'Down' in d['interface'][interface]['status']:
            if 'xe' in interface:
                speed = '10Gbps'
            elif 'ge' in interface:
                speed = '1000mbps'
        else:
            speed = d['interface'][interface]['speed']
        interfaces.append({
            'interface': interface,
            'description': d['interface'][interface]['description'],
            'status': d['interface'][interface]['status'],
            'speed': speed,
            'mtu': d['interface'][interface]['mtu'],
            'port_mode': d['interface'][interface]['port-mode'],
            'vlan': d['interface'][interface]['vlans'],
            'flap': flap,
            'bundle': d['interface'][interface]['bundle'],
            'mac': d['interface'][interface]['mac'],
            'interface_for_jquery': interface_for_jquery,
            'edit': edit})
        if len(d['interface'][interface]['mac']) == 0:
            continue
        mac_table.append({interface: {}})
        all_mac_count = 0
        for vlan in d['interface'][interface]['mac']:
            mac_table[count][interface][vlan] = {'mac_address': {}}
            for mac in d['interface'][interface]['mac'][vlan]:
                if mac in d['arp']:
                    mac_table[count][interface][vlan]['mac_address'][mac] = d['arp'][mac]
                else:
                    mac_table[count][interface][vlan]['mac_address'][mac] = '---'
            count_mac = len(mac_table[count][interface][vlan]['mac_address'])
            mac_table[count][interface][vlan]['count_mac'] = count_mac
            all_mac_count += count_mac
        mac_table[count][interface]['interface_count'] = all_mac_count
        count += 1
    # ports = []
    # for interface in juniper.output_interface(list(d['interface'].keys()), ['ge', 'xe'], port_count, device_count):
    #     if interface in y.config_yml[location][rack]['exclude_ports']:
    #         continue
    #     if interface not in d['interface']:
    #         ports.append(interface)
    #         continue
    #
    #     if d['interface'][interface]['bundle'].find(' ') == -1:
    #         continue
    #     else:
    #         ports.append(interface)

    return render_template('show_tables.html', interfaces=interfaces, mac_table=mac_table, vlan_table=d['vlans'])


if __name__ == '__main__':
    app.run()
