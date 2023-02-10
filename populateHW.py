#!/usr/bin/python3
import logging

class HWFinder():
    
    def find_hid(self, hw_name, hw):
        from os import listdir
        self.log.debug(f'finding HID {hw_name}')
        hidraws = listdir('/sys/class/hidraw/')
        for hidraw in hidraws:
            with open(f'/sys/class/hidraw/{hidraw}/device/uevent') as f:
                lines = f.readlines()
                for row in lines:
                    if row.find('HID_UNIQ') != -1:
                        hid_serial = row.strip().split('=')[1]
                        if hid_serial == hw['serial']:
                            path = f'/dev/{hidraw}'
                            self.log.info(f'Found device {hw_name} at address {path}')
                            return path
        raise Exception(f'Device {hw_name} of type HID with serial {hw["serial"]} not found')
     
    def find_usb(self, hw_name, hw):
        import usb
        self.log.debug(f'finding USB {hw_name}')
        vendor = hw['usb_vendor']
        product = hw['usb_product']
        devices = usb.core.find(find_all=True, idVendor=vendor, idProduct=product)
        serial = hw['usb_serial']
        for device in devices:
            usb_serial = usb.util.get_string(device, device.iSerialNumber)
            if usb_serial is None:
                usb_serial = 0
            if serial == usb_serial:
                device_bus = str(device.bus).zfill(3)
                device_address = str(device.address).zfill(3)
                path = f'/dev/bus/usb/{device_bus}/{device_address}'
                self.log.info(f'Found device {hw_name} at address {path}')
                return path
        raise Exception(f'Device {hw_name} of type USB with serial {hw["usb_serial"]} not found')
        
    
    def find_tty(self, hw_name, hw):
        import usb
        self.log.debug(f'finding TTY {hw_name}')
        vendor = hw['usb_vendor']
        product = hw['usb_product']
        devices = usb.core.find(find_all=True, idVendor=vendor, idProduct=product)
        serial = hw['usb_serial']
        for device in devices:
            usb_serial = usb.util.get_string(device, device.iSerialNumber)
            if serial == usb_serial:
                usb_manufacturer = usb.util.get_string(device, device.iManufacturer)
                usb_product = usb.util.get_string(device, device.iProduct).replace(' ', '_')
                path = f'/dev/serial/by-id/usb-{usb_manufacturer}_{usb_product}_{usb_serial}-if00-port0'
                self.log.info(f'Found device {hw_name} at address {path}')
                name_in_container = hw.get('name_in_container')
                if name_in_container is not None:
                    self.log.info(f'name in container is defined. renaming the device to /dev/{name_in_container}')
                    path += f':/dev/{name_in_container}'
                return path
        raise Exception(f'Device {hw_name} of type TTY with serial {hw["usb_serial"]} not found')
            
    def __init__(self, config_file, log_level=logging.INFO):
        hardwareDefinitionFields = ['device_type']
        deviceTypes = {'HID': self.find_hid, 'USB': self.find_usb, 'TTY': self.find_tty}
        import yaml
        
        self.log = logging.getLogger('HWFinder')
        self.log.setLevel(log_level)
        
        self.config_file = config_file
        with open(self.config_file, 'r') as file:
            config = yaml.safe_load(file)
        self.log.debug(f'loaded config from {config_file}: {config}')
        
        hardware = config['hardware']
        self.path_dict = {}
            
        for hw_name, hw in hardware.items():
            if not set(hardwareDefinitionFields).issubset(set(hw.keys())):
                missing_content = set(hardwareDefinitionFields).difference(set(hw.keys()))
                raise Exception(f'Missing mandatory hw definition field for {service_name}.{hw_name}: {missing_content}')
            
            device_type = hw['device_type']
            
            if device_type not in deviceTypes.keys():
                raise Exception(f'Unknown device type {device_type}. Possible values are : {deviceTypes.keys()}')
            
            self.path_dict[hw_name] = deviceTypes[device_type](hw_name, hw)
        
        self.log.debug(self.path_dict)
            
                        

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='HW finder for vscode devcontainer generic-cmake-env')
    parser.add_argument('-c', '--config',  help='Hardware declaration file TOML', type=str, metavar="FILE")
    # parser.add_argument('-p', '--path',  help='add manual device path to docker . usage: service_name:path_to_device', type=str)
    parser.add_argument('-o', '--output',  help='fiel to export the pathes', type=str, default="./.env")
    parser.add_argument('-a', '--append',  help='do not erase the output file', action='store_true')
    parser.add_argument('-d', '--debug',  help='print debug infos', type=bool, default=False)
    args = parser.parse_args()
    
    logging.basicConfig(format="[%(asctime)s] %(name)8s [%(levelname)8s] --- %(message)s")
    log = logging.getLogger(__file__)
    log.setLevel(logging.DEBUG if args.debug else logging.INFO)
    
    finder = HWFinder(args.config, logging.DEBUG if args.debug else logging.INFO)

    log.info(f'Output results in file {args.output}')
    with open(args.output, 'a' if args.append else 'w') as f:
        for device, path in finder.path_dict.items():
            f.write(f'{device}_PATH={path}\n')

    log.info('Done')