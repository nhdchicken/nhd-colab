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
    repos_root = pathlib.Path("/content/nhd-colab")
    if not repos_root.is_dir():
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

    def create_patches(self, component_name):
        component_config = self.get_component_config(component_name=component_name)
        if 'patches' not in component_config:
            LOGGER.debug(f"component has no patches {component_name}")
            return
        patch_list = component_config['patches']
        for fileid, patch_info in patch_list.items():
            original = pathlib.Path(patch_info['ori']).absolute()
            newfile = pathlib.Path(patch_info['new']).absolute()
            click.secho(f"{component_name}:{fileid} creating patch {original} ", fg='cyan', nl=False)
            if not original.is_file():
                click.ClickException(f"original file {original} to patch not found")
            if not newfile.is_file():
                click.ClickException(f"new file {newfile} to patch not found")
            patch_file = newfile.parent / (str(newfile.name) + ".patch")
            patch_info['patch_file'] = patch_file
            patch_cmd = f"diff -u {original} {newfile} > {patch_file}"
            self.sub_process(cmd=patch_cmd, returncode=1)  # Diff returns 1

    def install_patches(self, component_name):
        component_config = self.get_component_config(component_name=component_name)
        if 'patches' not in component_config:
            LOGGER.debug(f"component has no patches {component_name}")
            return
        patch_list = component_config['patches']
        for fileid, patch_info in patch_list.items():
            patch_file = patch_info.get('patch_file')
            original = pathlib.Path(patch_info['ori']).absolute()
            if not patch_file:
                click.secho(f"[{fileid}] has not patch file")
                continue
            patch_file = pathlib.Path(patch_file).absolute()
            click.secho(f"{component_name}:{fileid} installing patch {patch_file} on {original} ", fg='cyan', nl=False)
            if patch_file.is_file() is False:
                click.ClickException(f"{component_name}:{fileid} patch file not found {patch_file}")
            patch_cmd = f"patch --verbose {original} < {patch_file}"
            self.sub_process(cmd=patch_cmd, returncode=0)



    def sub_process(self, cmd, returncode=0):
        if isinstance(cmd, list):
            cmd = " ".join(cmd)
        result = subprocess.run(
            cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True
        )
        if result.returncode == returncode:
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
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="force initialization",
)

@click.argument('components', nargs=-1)
def init(install_config, dry_run, force, components):
    """ Initializes an patches the component

        This command should be used in a notebook when initializing
        sub components. The components are defined in the
        install.yml file located at the root of the git repos.

        Alternatively you can change the location of that file
        using the --install-config option.

        When specifying --dry-run, the commands to be executed
        will be echoed without being actually executed

        if a component was initialized, it is skipped unless you
        use the --force option

        Running this command without positional arguments will install
        all components in the install.yml.

        You can selectively install some by listing them by name on the
        command line

        $ colab init mp-mask-rcnn component2 ...

    """
    init_flag=pathlib.Path(os.getcwd()) / ".init.yml"
    init_info = {}
    if init_flag.is_file():
        with open(init_flag, 'r') as fh:
            init_info = yaml.load(stream=fh, Loader=yaml.SafeLoader)
    if install_config:
        install_config = pathlib.Path(install_config)
    else:
        install_config = pathlib.Path(os.getcwd()) / 'install.yml'
    comps = Components(install_config)
    click.secho("installing components", fg='cyan')
    for comp_name in comps.component_list.keys():
        if components and comp_name not in components:
            continue
        if comp_name in init_info:
            if force:
                click.secho(f"{comp_name} already installed - forcing", fg='yellow')
            else:
                click.secho(f"{comp_name} already installed - skipping", fg='green')
                continue
        comps.install(component_name=comp_name, dry_run=dry_run)
        comps.create_patches(component_name=comp_name)
        comps.install_patches(component_name=comp_name)
        init_info[comp_name] = True
        with open(init_flag, 'w') as fh:
            yaml.dump(data=init_info, stream=fh, Dumper=yaml.SafeDumper)



@cli_main.command()
@click.option(
    "-c", "--install-config", type=click.STRING, help="path to the configuration yaml file",
)
@click.argument('components', nargs=-1)
def patch(install_config, components):
    """ Patches the components

        Note that this is performed automatically when the init command is called.
    """
    if install_config:
        install_config = pathlib.Path(install_config)
    else:
        install_config = pathlib.Path(os.getcwd()) / 'install.yml'
    comps = Components(install_config)
    click.secho("creating patches", fg='cyan')
    for comp_name in comps.component_list.keys():
        if components and comp_name not in components:
            continue
        comps.create_patches(component_name=comp_name)
        comps.install_patches(component_name=comp_name)
