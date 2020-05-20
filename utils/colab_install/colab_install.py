import click

@click.group()
def cli_main(log_level):
    """ This command prepares the notebook environment.

    """
    print("Hi")