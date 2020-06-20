import pathlib
import click
import cv2
from PIL import Image

class Frame:
    def __init__(self, image_data, file_name="", frame_count=1):
        self.filename = file_name
        self.count = frame_count
        self.original = image_data
        self.original_size = image_data.shape[:2]
        self.model_input_size = 0
        self.bboxes = None


class FrameSource:

    def __init__(self, sources):
        self.sources = []
        if isinstance(sources, list):
            for source in sources:
                source = pathlib.Path(source).absolute()
                if not source.exists():
                    click.secho(f"{source} not found")
                    continue
                self.sources.append(source)
        else:
            source = pathlib.Path(sources).absolute()
            assert source, f"{self.source} not found"
            self.sources.append(source)


    def _extract_frame(self, file):
        """ Extracts one or more frame from the specified file (if any)

        :param file:
        :return:
        """
        click.secho(f"extracting frames from {file.name}", fg='cyan')
        try:
            if file.suffix.lower() in ['.avi', '.mp4', '.h264']:
                vid = cv2.VideoCapture(str(file))
                return_value = True
                frame_count = 0
                while return_value:
                    frame_count += 1
                    return_value, frame = vid.read()
                    if return_value:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        yield Frame(Image.fromarray(frame), file_name=file.name, frame_count=frame_count)
                vid.release()
            else:
                yield Frame(cv2.cvtColor(cv2.imread(str(file)), cv2.COLOR_BGR2RGB), file_name=file.name)
        except Exception as process_exception:
            click.secho(f"Failed to process {file} {process_exception}", fg='yellow')

    def next_frame(self):
        for source in self.sources:
            if source.is_file():
                for frame in self._extract_frame(source):
                    yield frame
            else:
                for file in source.iterdir():
                    for frame in self._extract_frame(file):
                        yield frame