import click
import matplotlib.pyplot
from PIL import Image

class DisplayImage:

    def __init__(self, prompt=False, in_jupyter=False):
        global NHD_ENV
        self.prompt = prompt
        self.in_jupyter = in_jupyter


    def show(self, frame):
        title = f"{frame.filename} # {frame.count}"

        if self.in_jupyter:
            matplotlib.pyplot.imshow(frame.original)
        else:
            if self.prompt:
                image = Image.fromarray(frame.original)
                image.show(title)
                value = click.prompt('Do you want to continue?', default='y')
                if not value.lower().startswith('y'):
                    raise click.Abort("aborted by user")
