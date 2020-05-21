# NHD Colab

This repository is used to experiment with various models on 
[Colab Research](https://colab.research.google.com/). 

It is **IMPORTANT** to note that no code written proprietary code or IP
(other than small modifications required to make existing/open source code work)
is added to this repository.

## Cloning the repos

Because this repos uses sub-modules, sub-modules need to be fetched
with the --recurse-submodules

```shell script
    git clone --recurse-submodules https://github.com/nhdchicken/nhd-colab.git
```
    

## NoteBooks

The notebooks are stored under [notebooks](notebooks). Those notebooks 
are intended to be executed on [Colab Research](https://colab.research.google.com/)

### Editing Notebooks locally

- install jupyter

    ```shell script
    $ pip install pip install jupyter
    $ cd nhd-colab # be in the root of the repository
    $ jupyter notebook
    ```

Simply navigate to the notebook of interest    

### Installing the Environment for a NoteBook

The first cell in the notebook will clone the repository if not already
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
pip install utils/colab_install/ || exit 1;
echo "use the colab-install command"
colab --help || exit 1;
echo "Great Success!"
```

This script is responsible for initializing any required git sub-modules, 
apply patches to the code and final perform installation.

### Configure The Sub-Modules

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

The init command are contained in the [install.yml](install.yml). To initialize 
those modules type

```shell script
$ colab init <component 1> ... <component n>
```
Here is an example of what such a cell should look like

```shell script
%%bash
cd /content/nhd-colab/
colab init mp-mask-rcnn
```

## Structure

To be determined