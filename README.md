# NHD Colab

This repository is used to experiment with various models on 
[Colab Research](https://colab.research.google.com/). 

It is **IMPORTANT** to note that proprietary code or IP
(other than small modifications required to make existing/open source code work)
is added to this repository.

```bash
$ rsync -arv --exclude=.* drive/nhddrive ~/Box/GTI/NHD/nhddrive
```

## Cloning the repos

Because this repos uses sub-modules, sub-modules need to be fetched
with the --recurse-submodules

```shell script
    git clone --recurse-submodules https://github.com/nhdchicken/nhd-colab.git
```

## Using NoteBooks 

The notebooks are stored under [notebooks](notebooks). Those notebooks 
are intended to be executed on [Colab Research](https://colab.research.google.com/)

There are two options

1. If there is a link for the notebook, simply click on it, this will copy
   the notebook to the colab sandbox and you are ready to go

    ![Run In Colab](images/run-in-colab.png)

2. Alternatively got to https://colab.research.google.com. Then you will have this dialog box

    ![Open from GitHub](images/colab-opennd-dialog.png)
    
Once the notebook is opened, follow the instructions.

## Editing Notebooks locally

- install jupyter

    ```shell script
    $ pip install jupyter
    $ cd nhd-colab # be in the root of the repository
    $ jupyter notebook
    ```

Simply navigate to the notebook of interest    

### Installing the Environment for a NoteBook

**Note**:

* check the [template notebook](notebooks/template.ipynb) which provides
all the boiler plate stuff to setup the environment (the following 
is just for your reference). 
* Want to try it out? Run in [Colab](https://colab.research.google.com/github/nhdchicken/nhd-colab/blob/master/notebooks/template.ipynb) 

You basically need 3 code cells at the beginning of your notebook

#### Cell 1 - Cloning Repos

```shell script
%%bash
# This is some boiler plate code that clones the repository on Colab
if [  -d "/content/nhd-colab" ]
then
   echo "Environment already initialized"
elif [ -d "/content" ] && [ ! -d "/content/nhd-colab" ]
then
    cd /content || exit 1;
    echo "Installing https://github.com/nhdchicken/nhd-colab.git"
    git clone --recurse-submodules https://github.com/nhdchicken/nhd-colab.git || exit 1;
    cd nhd-colab || exit 1;
else
    echo "Not running in Colab - going to root of repos"
    cd `git rev-parse --show-toplevel` || exit 1;
fi
echo "Installing colab installer (which will run in the next cell)"
pip install utils/colab_install/ > /dev/null 2>&1 || exit 1;
echo "Checkin that Colab is available"
colab > /dev/null 2>&1 || exit 1;
echo "Great Success!"
```

#### Cell 2 - Initializing the repos

The next code cell should be used to initialize any of the sub module (a.k.a. components)

The ``nhdcolab init`` command is responsible for initializing any required git sub-modules, 
apply patches to the code and finally perform installation. This is the topic 
of the next section.

To initialize those component, create a new cell and enter the following

```shell script
! nhdcolab init <component 1> ... <component n>
```

for the list of components

```shell script
$ nhdcolab show 
...
list of components
mp-mask-rcnn
yolov4-tf
```

By default, all patch groups are applied (see below for an explanation of patch group)

You need to be within the ``nhd-colab`` git repository when invoking ``nhdcolab``
as it automatically tries to go to the root of the repository to execute.

Here is an example of what such a cell should look like

```shell script
! nhdcolab init mp-mask-rcnn
```

This command also patches all the code for tensorflow 2. To disable patching

```shell script
! nhdcolab init mp-mask-rcnn --no-patch
```

Or you can selective install patch groups

```shell script
! nhdcolab init mp-mask-rcnn --patch-group tensorflow_2 --patch-group mygroup ...
```

To view the list of patch groups

```shell script
$ nhdcolab patch -l
NHD_COLAB_REPOS_ROOT=~/nhd/nhd-colab OK!
Google Drive not mounted
going to repos root dir ~/nhd/nhd-colab
loading install config ~/nhd/nhd-colab/install.yml
Component mp-mask-rcnn
>>> processing patch group tensorflow_2
        requirements
                original ~/nhd/nhd-colab/mask-rcnn/matterport/requirements.txt
                modified ~/nhd/nhd-colab/patches/matterport-mrcnn/requirements.txt
        model
                original ~/nhd/nhd-colab/mask-rcnn/matterport/mrcnn/model.py
                modified ~/nhd/nhd-colab/patches/matterport-mrcnn/model.py
        utils
                original ~/nhd/nhd-colab/mask-rcnn/matterport/mrcnn/utils.py
                modified ~/nhd/nhd-colab/patches/matterport-mrcnn/utils.py

```

#### Cell 3 - Loading the environment

This is done through the [NHDEnvironment](utils/nhdcolab/src/nhdcolab/environment.py) class.
Once loaded as a global environment variables it provides access to pre-defined locations
in the enviroment. 

```python
from nhdcolab.environment import NHDEnvironment
NHD_ENV = NHDEnvironment(gdrive_mount=True)
```

### Configuring Sub-Modules (Components)

The submodules are listed in [.gitmodules](.gitmodules). Those are cloned
automatically when cloning the nhd-colab repos. 

The ``colab`` command allows you to list and init/install those modules 

```shell script
    $nhdcolab show -d
    going to repos root dir ~/nhd/nhd-colab
    loading install config ~/nhd/nhd-colab/install.yml

    list of components

    mp-mask-rcnn
       installs the Mask-RCNN which is a sub-module under nhd-colab/mask-rcnn/matterport
       the original repository is https://github.com/matterport/Mask_RCNN
```

The initialization commands are contained in the [install.yml](install.yml). A component 
definition looks like this 

```yaml
  mp-mask-rcnn :
      doc: |
        installs the Mask-RCNN which is a sub-module under nhd-colab/mask-rcnn/matterport
        the original repository is https://github.com/matterport/Mask_RCNN

      patches:
        model:
            ori: mask-rcnn/matterport/mrcnn/model.py
            new: patches/matterport-mrcnn/model.py
        utils:
            ori: mask-rcnn/matterport/mrcnn/utils.py
            new: patches/matterport-mrcnn/utils.py

      commands:
        - pip install -r mask-rcnn/matterport/requirements.txt
        - pip install -e mask-rcnn/matterport/
```

Where **doc** is a description of the component to be initialized (normally a sub-module)
and **commands** is a simple list of commands to executed (always from the root of the 
repos.)

In this case we do the following

1. Patch the model and utils files
1. install the mask-rcnn python requirements
2. install the mask-rcnn which is used the notebook

See below for more information about patching. 

### Adding New Sub-Modules  

In this example we add https://github.com/matterport/Mask_RCNN under 
[mask-rcnn/matterport](mask-rcnn/matterport)

from the root of the repos

```shell script
  $ git submodule add https://github.com/matterport/Mask_RCNN mask-rcnn/matterport
````
this will add a new entry to [.gitmodules](.gitmodules). On Colab, this module 
will be automatically cloned. 

When working locally type

```shell script
$ git submodule init
$ git submodule update
```

### Patching Files in a Sub Module

Sometimes you will come across bugs when running a notebook. You can fix the code directly 
in colab by clicking on the link, then restart the notebook. 

Once the code is working, download the file and check it in under the [patches](patches)
folder. Check the [patches/matterport-mrcnn](patches/matterport-mrcnn) for an example. 
This folder contains 2 files, [model.py](patches/matterport-mrcnn/model.py) and 
[utils.py](patches/matterport-mrcnn/utils.py). The edit the [install.yml](install.yml)
file to add the following (as an exmaple):

```yaml
  patches:
    
    tensorflow_2

        model:
            ori: mask-rcnn/matterport/mrcnn/model.py
            new: patches/matterport-mrcnn/model.py
        utils:
            ori: mask-rcnn/matterport/mrcnn/utils.py
            new: patches/matterport-mrcnn/utils.py
```

Under patches, create a group name. The group name, as it says, creates groups of patches that
can be applied selectively by name.

Under the group name create a fileid (e.g. **model**) with two entries. *ori* is the relative
path (from the git root) to the file that needs to be patched, and *new* is the 
relative path to the file you just fixed and checked-in.

When installing the component, patches will be created automatically and applied.

- [utils](utils) A bunch of small utilies including the colab script
- [patches](patches) Where all the code patches for sub-modules should exist
- [notebooks](notebooks) Where our own notebooks are 