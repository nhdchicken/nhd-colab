# NHD Colab

This repository is used to experiment with various models on 
[Colab Research](https://colab.research.google.com/). 

It is **IMPORTANT** to note that proprietary code or IP
(other than small modifications required to make existing/open source code work)
is added to this repository.

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
    $ pip install pip install jupyter
    $ cd nhd-colab # be in the root of the repository
    $ jupyter notebook
    ```

Simply navigate to the notebook of interest    

### Installing the Environment for a NoteBook

The first **code** cell in the notebook should be this boiler plate 
code. This will clone the repository if not already
cloned and install the colab installer script.

```shell script
%%bash
if [ -d "/content" ] && [ ! -d "/content/nhd-colab" ]
then
    cd /content || exit 1;
    echo "Installing https://github.com/nhdchicken/nhd-colab.git"
    git clone --recurse-submodules https://github.com/nhdchicken/nhd-colab.git || exit 1;
    cd nhd-colab || exit 1;
else
    echo "Not running in Colab - going to root of repos"
    cd `git rev-parse --show-toplevel` || exit 1;
fi
pwd
pip install utils/colab_install/ > /dev/null 2>&1 || exit 1;
colab > /dev/null 2>&1 || exit 1;
echo "Great Success!"
```

The next code cell should be used to initialize any of the sub module (a.k.a. components)

The ``colab`` is responsible for initializing any required git sub-modules, 
apply patches to the code and finally perform installation. This is the topic 
of the next section.

### Configuring Sub-Modules (Components)

The submodules are listed in [.gitmodules](.gitmodules). Those are cloned
automatically when cloning the nhd-colab repos. 

The ``colab`` command allows you to list and init/install those modules 

```shell script
    $ colab show -d
    going to repos root dir /Users/lpbrac/gitlab/pyops/nhd/nhd-colab
    loading install config /Users/lpbrac/gitlab/pyops/nhd/nhd-colab/install.yml

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

      commands:
        - patch --verbose mask-rcnn/matterport/mrcnn/model.py < patches/mask-rcnn-matterport-mrcnn-model.py.patch
        - pip install -r mask-rcnn/matterport/requirements.txt
        - pip install -e mask-rcnn/matterport/
```

Where **doc** is a description of the component to be initialized (normally a sub-module)
and **commands** is a simple list of commands to executed (always from the root of the 
repos.)

In this case we do the following

1. patch the _model.py_ file with changes to make it compatible with the TensorFlow 
   version on Colab
2. install the mask-rcnn python requirements
3. install the mask-rcnn which is used the notebook

### Initializing Components

To initialize those component, create a new cell and enter the following

```shell script
%%bash
cd /content/nhd-colab/
$ colab init <component 1> ... <component n>
```

You need to be within the ``nhd-colab`` git repository when invoking ``colab``
as it automatically tries to go to the root of the repository to execute.

Here is an example of what such a cell should look like

```shell script
%%bash
cd /content/nhd-colab/
colab init mp-mask-rcnn
```

The beginning of your notebook should look like this on Colab

![sample notebook on colab](images/notebook-init.png)

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

# Creating a Patch

Here is a simple example for a single file (assuming you are at the root
of the repos)

```shell script

$ diff -u mask-rcnn/matterport/mrcnn/model.py ../old_colab/mask-rcnn/matterport/mrcnn/model.py > patches/mask-rcnn-matterport-mrcnn-model.py.patch

```

The to apply the patch, add a command to the [install.yml](install.yml), 
e.g. ```patch --verbose mask-rcnn/matterport/mrcnn/model.py < patches/mask-rcnn-matterport-mrcnn-model.py.patch```

For more complex scenarios check this [Link about creating patches](https://www.thegeekstuff.com/2014/12/patch-command-examples/)

## Structure

- [utils](utils) A bunch of small utilies including the colab script
- [patches](patches) Where all the code patches for sub-modules should exist
- [notebooks](notebooks) Where our own notebooks are 