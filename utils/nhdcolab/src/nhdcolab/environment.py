import os
import platform
import pathlib
import click

class NHDEnvironment:
    def __init__(self, gdrive_mount=True):
        self._IN_COLAB = False

        # Determine the colab root directory
        self._NHD_COLAB_REPOS_ROOT = pathlib.Path(os.getcwd())
        if os.getcwd() == '/content':
            self._IN_COLAB = True
            print("Running in Colab")
            self._NHD_COLAB_REPOS_ROOT = self._NHD_COLAB_REPOS_ROOT / 'nhd-colab'
        else:
            while self._NHD_COLAB_REPOS_ROOT.name.lower() != 'nhd-colab' and str(self._NHD_COLAB_REPOS_ROOT) != self._NHD_COLAB_REPOS_ROOT.root:
                self._NHD_COLAB_REPOS_ROOT = self._NHD_COLAB_REPOS_ROOT.parent

        assert self._NHD_COLAB_REPOS_ROOT.name == 'nhd-colab', f"could not fine nhd-colab in {self._NHD_COLAB_REPOS_ROOT}"
        os.chdir(self._NHD_COLAB_REPOS_ROOT)
        assert os.getcwd() == str(self._NHD_COLAB_REPOS_ROOT.cwd())

        click.secho(f"NHD_COLAB_REPOS_ROOT={self._NHD_COLAB_REPOS_ROOT} OK!", fg='green')

        self._IS_JETSON = True if platform.machine() == "aarch64" and "tegra" in platform.release() else False

        if gdrive_mount:
            # Determine the location of the Colab Drive
            self._NHD_COLAB_DRIVE = pathlib.Path("/content/drive/My Drive")
            try:
                from google.colab import drive
                drive.mount('/content/drive/')
            except ModuleNotFoundError:
                self._NHD_COLAB_DRIVE = pathlib.Path(os.environ.get('NHD_COLAB_DRIVE', self._NHD_COLAB_REPOS_ROOT / 'drive' / 'nhddrive'))
                print(f"Google drive not mounted since not running in Colab - using {self._NHD_COLAB_DRIVE}")
                if not self._NHD_COLAB_DRIVE.is_dir():
                    self._NHD_COLAB_DRIVE.mkdir(parents=True, exist_ok=True)
            assert self._NHD_COLAB_DRIVE.is_dir(), f"{self._NHD_COLAB_DRIVE} not found"
    
            self._NHD_COLAB_TEST_MATERIAL = self._NHD_COLAB_DRIVE / 'test_material'
            assert self._NHD_COLAB_TEST_MATERIAL.is_dir(), f"{self._NHD_COLAB_TEST_MATERIAL} not found"
        else:
            click.secho("Google Drive not mounted", fg='yellow')



    @property
    def IN_COLAB(self):
        '''Returns True if running in Colab'''
        return self._IN_COLAB
    
    @property
    def NHD_COLAB_REPOS_ROOT(self):
        '''Returns the root location of the colab repository (as pathlib.Path)'''
        return self._NHD_COLAB_REPOS_ROOT
    
    @property
    def NHD_COLAB_DRIVE(self):
        '''Returns the location of the google drive location (as pathlib.Path)'''
        return self._NHD_COLAB_DRIVE

    @property
    def NHD_COLAB_TEST_MATERIAL(self):
        '''Returns the location of the test material (as pathlib.Path)'''
        return self._NHD_COLAB_TEST_MATERIAL

    @property
    def IS_JETSON(self):
        """ Return True if running on Jetson board, false otherwise."""
        return self._IS_JETSON
