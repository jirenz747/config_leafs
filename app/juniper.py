from jnpr.junos import Device
from pprint import pprint


def get_juniper(ip_device, login, password):

    try:
        dev = Device(host=ip_device, user=login, password=password, port='22', timeout=30)
        dev.open(normalize=True)
    except Exception:
        return "Error: Can't connected to device {}. Maybe password or login is wrong?".format(ip_device)

    try:
        config = dev.rpc.get_config( filter_xml='<interfaces></interfaces>', options={'format': 'json'})
        config_interface = config['configuration']['interfaces']['interface']
    except Exception:
        dev.close()
        return 'Error: Version RPC is OLD. Update firmware on your device {}!'.format(ip_device)
    config = dev.rpc.get_config(
        filter_xml='<vlans></vlans>',
        options={'format': 'json'})
    config_vlans = config['configuration']['vlans']['vlan']
    interfaces = dev.rpc.get_interface_information()
    ethernet = dev.rpc.get_ethernet_switching_table_information()
    vlan = dev.rpc.get_vlan_information()
    ver = dev.rpc.get_software_information()
    arp = dev.rpc.get_arp_table_information(no_resolve=True)
    dev.close()
    model = ver.xpath("//product-model/text()")[0]
    d = {'vlans': {}, 'interface': {}, 'arp': {}}
    for i in arp.xpath("//arp-table-entry"):
        mac = i.findtext('mac-address')
        ip_addr = i.findtext('ip-address')
        d['arp'][mac] = ip_addr
    for i in interfaces.xpath("//physical-interface"):
        int_name = i.findtext('name')
        int_mtu = i.findtext('mtu')
        int_status = i.findtext('oper-status')
        int_speed = i.findtext('speed')
        int_flapped = i.findtext('interface-flapped')
        int_description = i.findtext('description')
        bundle = i.xpath('./logical-interface/address-family')
        if len(bundle) > 0:
            bundle = bundle[0].findtext('ae-bundle-name')
        if (bundle is None) or (len(bundle) == 0):
            bundle = ' '
        port_mode = i.xpath('./logical-interface/address-family/address-family-flags/ifff-port-mode-trunk')
        if len(port_mode) > 0:
            port_mode = 'trunk'
        else:
            port_mode = 'access'
        d['interface'][int_name] = {'status': int_status, 'mtu': int_mtu, 'speed': int_speed, 'flap': int_flapped,
                                    'description': int_description, 'vlans': [], 'bundle': bundle, 'port-mode': port_mode,
                                    'mac': {}}
        for j in i.xpath('./logical-interface'):
            irb_name = j.findtext('name')
            irb_ip = j.xpath("./address-family/interface-address/ifa-local/text()")
            if 'irb.' in irb_name:
                if len(irb_ip) == 0:
                    continue
                irb_name = str(irb_name).split('.')[1]
                d['vlans'][irb_name] = {'ip': irb_ip[0]}

    for i in vlan.xpath('//l2ng-l2ald-vlan-instance-group'):
        vland_id = i.findtext('l2ng-l2rtb-vlan-tag')
        if not vland_id in d['vlans']:
            if vland_id != '1':
                d['vlans'][vland_id] = {'ip': 'Not ip address'}

        for j in i.xpath('./l2ng-l2rtb-vlan-member'):
            int = str(j.findtext('l2ng-l2rtb-vlan-member-interface')).replace('*','').replace('.0', '').strip()
            if int in d['interface']:
                d['interface'][int]['vlans'].append(vland_id)

    for i in ethernet.xpath('//l2ng-mac-entry'):
        vlan_name = i.findtext('l2ng-l2-mac-vlan-name')
        mac_address = i.findtext('l2ng-l2-mac-address')
        inter = i.findtext('l2ng-l2-mac-logical-interface')
        inter = inter[:inter.find('.')]
        if vlan_name in d['interface'][inter]['mac']:
            d['interface'][inter]['mac'][vlan_name].append(mac_address)
        else:
            d['interface'][inter]['mac'][vlan_name] = [mac_address]

    for i in config_vlans:
        vlan_id = str(i['vlan-id'])
        if vlan_id == '1':
            continue
        if not 'description' in i:
            vlan_description = 'Empty'
        else:
            vlan_description = i['description']
        d['vlans'][vlan_id]['description'] = vlan_description

    for i in config_interface:
        name = i['name']
        description = i.get('description', '')
        if (not i.get('ether-options') is None) and (not i['ether-options'].get('ieee-802.3ad') is None):
            bundle = i['ether-options']['ieee-802.3ad']['bundle']
            continue
        mtu = i.get('mtu', 'None')
        vlan = ''
        if (not i.get('unit') is None) and (not i['unit'][0].get('family') is None):
            if not i['unit'][0]['family'].get('ethernet-switching') is None:
                if not i['unit'][0]['family']['ethernet-switching'].get('vlan') is None:
                    vlan = i['unit'][0]['family']['ethernet-switching']['vlan']['members']
                interface_mode = i['unit'][0]['family']['ethernet-switching'].get('interface-mode', 'None')
                if not name in d['interface']:
                    d['interface'][name] = {'status': 'Down', 'mtu': mtu, 'speed': 'None',
                                                'flap': '',
                                                'description': description, 'vlans': vlan, 'bundle': ' ',
                                                'port-mode': interface_mode,
                                                'mac': {}}
    return d


# function for sort interfaces
def output_interface(interface, str_p, port_count=0, device_count=1):
    l = []
    if 'ae' in str_p:
        for i in interface:
            if 'ae' in i:
                temp = int(i.replace('ae', ''))
                l.append(temp)
        l.sort()
        for i in range(0, len(l)):
            l[i] = 'ae{}'.format(l[i])
        return l

    exist_int = []
    for i in interface:
        if 'xe' in i or 'ge' in i:
            exist_int.append(i)
    pref_link = []
    temp = 0

    for count in range(0, device_count):
        for i in range(0, port_count):
            for j in exist_int:
                new_int = '{}/0/{}'.format(count, i)
                if j[3:] in new_int and len(j[3:]) == len(new_int):
                    pref_link.append(j)
                    temp = 1
                    break
            if temp == 1:
                temp = 0
                continue
            pref_link.append('xe-{}/0/{}'.format(count, i))
    return pref_link


if __name__ == '__main__':
    d = get_juniper('192.168.1.1', login='admin', password='admin')
    # pprint(d)
    # interface = list(d['interface'].keys())
    # pprint(d['vlans'])




    """
    'xe-0/0/3': {'bundle': None,
                            'description': None,
                            'flap': '2018-09-04 19:32:22 MSK (1w6d 17:59 ago)',
                            'mtu': '1514',
                            'speed': '10Gbps',
                            'status': 'up',
                            'vlans': ['1516']},
    """
