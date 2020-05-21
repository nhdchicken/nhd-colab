import os
import pathlib
import logging
import subprocess
import click
import yaml
import yaml.scanner


LEVEL_NAMES = list(map(str.lower, logging._nameToLevel.keys()))
LOGGER = logging.getLogger("nhd-colab")

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
LOGGER.addHandler(ch)


@click.group()
@click.option(
    "-ll",
    "--log-level",
    type=click.Choice(LEVEL_NAMES, case_sensitive=False),
    default="WARNING",
    help="log level",
)
def cli_main(log_level):
    """ This command prepares the notebook environment.

    """
    global LOGGER
    LOGGER.setLevel(log_level.upper())
    repos_root = subprocess.check_output('git rev-parse --show-toplevel', shell=True).decode('utf-8').strip()
    click.secho(f"going to repos root dir {repos_root}", fg='yellow')
    repos_root = pathlib.Path(repos_root).absolute()
    os.chdir(repos_root)
    if pathlib.Path(os.getcwd()).absolute() != repos_root:
        raise click.ClickException(f"Failed to set cwd to {repos_root} - current {os.getcwd()}")


class Components:

    def __init__(self, config_path):
        click.secho(f"loading install config {config_path}")
        self.config = None
        try:
            with open(config_path, "r") as config_fh:
                self.config = yaml.load(config_fh, Loader=yaml.SafeLoader)
        except (FileNotFoundError, yaml.scanner.ScannerError) as load_exception:
            if LOGGER.level == logging.DEBUG:
                LOGGER.exception(f"Failed to load config {config_path}")
            raise click.ClickException(f"Failed to load config {config_path} --> {load_exception}")
        LOGGER.debug(f"Configuration Content:\n{yaml.dump(self.config, Dumper=yaml.SafeDumper)}")
        self.component_list = self.config['components']

    def get_component_config(self, component_name):
        try:
            return self.component_list[component_name]
        except KeyError:
            raise click.ClickException(f"component {component_name} unknown")

    def show(self, component_name, doc=False):
        component_config = self.get_component_config(component_name=component_name)
        click.secho(f"{component_name}", fg='green')
        if doc:
            content = component_config.get('doc')
            if content:
                click.secho(content, fg='cyan')
            else:
                click.secho('\tdocumentation not available', fg='yellow')

    def install(self, component_name, dry_run=False):
        component_config = self.get_component_config(component_name=component_name)
        click.secho(f"installing component {component_name}", fg='cyan')
        if 'commands' not in component_config:
            raise click.ClickException(f"Component {component_name} has no commands"
                                       f"\nYAML\n {yaml.dump(component_config, Dumper=yaml.SafeDumper)}")
        command_list = component_config['commands']
        if not isinstance(command_list, list):
            command_list = [command_list] # String literal
            print(command_list)
        for command in command_list:
            if dry_run:
                click.secho(f"[dry-run]", nl=False, fg='yellow', bold=True)
                click.secho(f"{command}")
            else:
                click.secho(f"[running]", nl=False, fg='cyan', bold=True)
                click.secho(f"{command}", nl=False)
                self.sub_process(command)

    def sub_process(self, cmd):
        if isinstance(cmd, list):
            cmd = " ".join(cmd)
        result = subprocess.run(
            cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True
        )
        if result.returncode == 0:
            click.secho(" OK!", fg="green")
        else:
            LOGGER.debug(result.stdout.decode('utf-8'))
            click.secho(result.stderr.decode('utf-8'), fg='yellow')
            click.secho(" FAILED", fg="red")
            raise click.ClickException(f"subprocess {cmd} failed {result.stderr.decode('utf-8')}")



@cli_main.command()
@click.option(
    "-c", "--install-config", type=click.STRING, help="path to the configuration yaml file",
)
@click.option(
    "-d",
    "--doc",
    is_flag=True,
    help="shows the documentation",
)
@click.argument('components', nargs=-1)
def show(install_config, doc, components):
    """ Shows the list of components that can be initialized.

        use the --doc option for more details.

    """
    if install_config:
        install_config = pathlib.Path(install_config)
    else:
        install_config = pathlib.Path(os.getcwd()) / 'install.yml'
    comps = Components(install_config)
    click.secho("list of components", fg='cyan')
    for comp_name in comps.component_list.keys():
        if components and comp_name not in components:
            continue
        comps.show(component_name=comp_name, doc=doc)

@cli_main.command()
@click.option(
    "-c", "--install-config", type=click.STRING, help="path to the configuration yaml file",
)
@click.option(
    "-d",
    "--dry-run",
    is_flag=True,
    help="execute the installation in dry run more",
)

@click.argument('components', nargs=-1)
def init(install_config, dry_run, components):
    """ Initializes the component

        This command should be used in a notebook when initializing
        sub components. The components are defined in the
        install.yml file located at the root of the git repos.

        Alternatively you can change the location of that file
        using the --install-config option.

        When specifying --dry-run, the commands to be executed
        will be echoed without being actually executed

        Running this command without positional arguments will install
        all components in the install.yml.

        You can selectively install some by listing them by name on the
        command line

        $ colab init mp-mask-rcnn component2 ...

    """
    if install_config:
        install_config = pathlib.Path(install_config)
    else:
        install_config = pathlib.Path(os.getcwd()) / 'install.yml'
    comps = Components(install_config)
    click.secho("installing components", fg='cyan')
    for comp_name in comps.component_list.keys():
        if components and comp_name not in components:
            continue
        comps.install(component_name=comp_name, dry_run=dry_run)
