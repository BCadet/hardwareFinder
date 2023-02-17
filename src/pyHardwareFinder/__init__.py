#!/usr/bin/python3
import logging

class HWFinder():
    def find(self, hw_name, hw):
        import pyudev

        udev_context = pyudev.Context()
        
        for device in udev_context.list_devices(SUBSYSTEM='usb'):
            usb_vendor = int(device.get('ID_VENDOR_ID','0'), 16)
            usb_product = int(device.get('ID_MODEL_ID','0'), 16)
            devnames = (child.get('DEVNAME', None) if child.get('SUBSYSTEM') == hw['device_type'].lower() else None for child in device.children)
                
            if usb_vendor == hw['usb_vendor'] and usb_product == hw['usb_product']:
                usb_serial = device.get('ID_SERIAL_SHORT', int(device.get('ID_REVISION'), 16))
                if usb_serial == hw.get('usb_serial', hw.get('device_id', 0)):
                    devname = next((devname for devname in devnames if devname is not None), device.get('DEVNAME', None))
                    return f"{devname}:{hw.get('name_in_container')}" if hw.get('name_in_container') is not None else devname
        raise Exception(f'Device {hw_name} not found')
    
    def parse_yaml(self, config_file):
        hardwareDefinitionFields = ['device_type']
        import yaml
        
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
            self.path_dict[hw_name] = self.find(hw_name, hw)
        
        self.log.debug(self.path_dict)
            
    def __init__(self, config_file, log_level=logging.INFO):
        self.log = logging.getLogger('HWFinder')
        self.log.setLevel(log_level)

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
    
    finder = HWFinder(logging.DEBUG if args.debug else logging.INFO)
    
    finder.parse_yaml(args.config)

    log.info(f'Output results in file {args.output}')
    with open(args.output, 'a' if args.append else 'w') as f:
        for device, path in finder.path_dict.items():
            f.write(f'{device}_PATH={path}\n')

    log.info('Done')