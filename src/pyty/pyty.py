import os
import click
import sre_yield
import tempfile
import subprocess
from pathlib import Path
import shutil

try:
    from pkg_resources import get_distribution, DistributionNotFound
    _dist = get_distribution('pyty')
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(_dist.location)
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc,'pyty')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
except (ImportError,DistributionNotFound):
    __version__ = None
else:
    __version__ = _dist.version


class FirmwareUploader(object):
    '''
    Uploads firmware to multiple embedded devices.

    Example Usage:

    fu -e teensy40 -d https://github.com/janelia-arduino/YArenaValveController "(/dev/ttyACM)[0-2]"
    # Environment: teensy40
    # Dry Run: True
    # Firmware URL: https://github.com/janelia-arduino/YArenaValveController
    # Upload ports: ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2']
    # Do you want to continue? [y/N]: y
    # Cloning into 'YArenaValveController'...
    #remote: Enumerating objects: 118, done.
    # remote: Counting objects: 100% (118/118), done.
    # remote: Compressing objects: 100% (78/78), done.
    # remote: Total 118 (delta 65), reused 88 (delta 35), pack-reused 0
    # Receiving objects: 100% (118/118), 19.79 KiB | 2.47 MiB/s, done.
    # Resolving deltas: 100% (65/65), done.
    # ['stty', '-F', '/dev/ttyACM0', '134']
    # ['pio', 'run', '-e', 'teensy40', '--target', 'upload', '--upload-port', '/dev/ttyACM0']
    # ['stty', '-F', '/dev/ttyACM1', '134']
    # ['pio', 'run', '-e', 'teensy40', '--target', 'upload', '--upload-port', '/dev/ttyACM1']
    # ['stty', '-F', '/dev/ttyACM2', '134']
    # ['pio', 'run', '-e', 'teensy40', '--target', 'upload', '--upload-port', '/dev/ttyACM2']

    fu -e teensy40 https://github.com/janelia-arduino/YArenaValveController "(/dev/ttyACM)[0-2]"
    # Environment: teensy40
    # Dry Run: False
    # Firmware URL: https://github.com/janelia-arduino/YArenaValveController
    # Upload ports: ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2']
    # Do you want to continue? [y/N]:

    fu -e teensy40 ./git/arduino/YArenaValveController/ "(/dev/ttyACM)[0-2]"
    # Environment: teensy40
    # Dry Run: False
    # Firmware URL: ./git/arduino/YArenaValveController/
    # Upload ports: ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2']
    # Do you want to continue? [y/N]:
    '''

    def __init__(self,environment,dry_run,firmware_url,upload_ports,*args,**kwargs):
        self.environment = environment
        self.dry_run = dry_run
        self.firmware_url = firmware_url
        self.upload_ports = upload_ports
        if isinstance(self.upload_ports,str):
            self.upload_ports = list(sre_yield.AllStrings(self.upload_ports))

    def _output(self,args):
        if not self.dry_run:
            subprocess.run(args)
        else:
            print(os.getcwd())
            print(args)

    def _upload(self):
        for upload_port in self.upload_ports:
            if self.environment is not None:
                if 'teensy' in self.environment:
                    # teensy loader ignores --upload-port, so must manually
                    # put into bootloader mode by setting baud of port
                    # before uploading
                    self._output(['stty','-F',upload_port,'134'])
                self._output(['pio','run','-e',self.environment,'--target','upload','--upload-port',upload_port])
            else:
                self._output(['pio','run','--target','upload','--upload-port',upload_port])

    def run(self):
        if Path(self.firmware_url).exists():
            os.chdir(self.firmware_url)
            self._upload()
        else:
            with tempfile.TemporaryDirectory() as tmpdirname:
                tmpdirpath = Path(tmpdirname)
                os.chdir(tmpdirpath)
                subprocess.run(['git','clone',self.firmware_url],check=True)
                repository_name = Path(self.firmware_url).name
                tmpdirpath /= repository_name
                os.chdir(tmpdirpath)
                self._upload()


@click.command()
@click.option('-e','--environment')
@click.option('-d','--dry-run', is_flag=True)
@click.argument('firmware_url')
@click.argument('upload_ports_re')
def cli(environment,dry_run,firmware_url,upload_ports_re):
    upload_ports = list(sre_yield.AllStrings(upload_ports_re))

    print('Environment: {0}'.format(environment))
    print('Dry Run: {0}'.format(dry_run))
    print('Firmware URL: {0}'.format(firmware_url))
    print('Upload ports: {0}'.format(upload_ports))

    if click.confirm('Do you want to continue?', abort=True):
        fu = FirmwareUploader(environment,dry_run,firmware_url,upload_ports)
        fu.run()

# -----------------------------------------------------------------------------------------
if __name__ == '__main__':
    cli()
