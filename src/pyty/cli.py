from pyty import Pyty
import click

@click.command()
@click.option('-e','--environment')
@click.option('-d','--dry-run', is_flag=True)
@click.argument('firmware_url')
@click.argument('upload_ports_re')
def cli(environment,
         dry_run,
         firmware_url,
         upload_ports_re):
    print('in cli.py')
    _pyty = Pyty(environment,dry_run,firmware_url,upload_ports)

    print('Environment: {0}'.format(_pyty.environment))
    print('Dry Run: {0}'.format(_pyty.dry_run))
    print('Firmware URL: {0}'.format(_pyty.firmware_url))
    print('Upload ports: {0}'.format(_pyty.upload_ports))

    if click.confirm('Do you want to continue?', abort=True):
        _pyty.run()
