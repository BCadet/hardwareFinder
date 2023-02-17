=============================================================================
pyHardwareFinder: a Python usb device identifier for docker container sharing
=============================================================================

:Authors:   - Bryan CADET <BCadet>
:Date:     Febuary 2023

This is a PYthon class that takes a yaml file as input and use pyudev to identify an USB hardware based on the VendorID/ProductID/Serial to identify the corresponding /dev.
Once identified, the path is exported dict with the corresponding hardware as key.

My main usage of this is to export the path to a .env fole to be used with docker compose.
By this, I only share the device I want to use and avoid the usage of the privileged option.


Installation
============

Install using pip:

.. code:: python

    pip install git+https://github.com/BCadet/pyHardwareFinder

Usage
=====

.. code:: python

    from pyHardwareFinder import HWFinder

    if __name__ == "__main__":
        finder = HWFinder()
        
        finder.parse_yaml(yml_fileName)

        with open(output_fileName,'w') as f:
            for device, path in finder.path_dict.items():
                f.write(f'{device}_PATH={path}\n')

Limitations
===========

- It only suport USB device for now