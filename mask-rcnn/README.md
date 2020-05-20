# Mask RCNN

The following contains source of various implementation of the mask-rcnn model. 

[matterport](matterport) come from [Mask_RCNN from Matterport](https://github.com/matterport/Mask_RCNN)
which is distributed under the [MIT License](matterport/LICENSE).

[The NVidia TensorRT](https://github.com/NVIDIA/TensorRT/tree/master/samples/opensource/sampleUffMaskRCNN)
is a patched version of the model which has been compiled for the TensorRT framework.

[submodule "matterport-mask-rcnn"]
	path = mask-rcnn
	url = https://github.com/matterport/Mask_RCNN

[submodule "nvidia-mask-rcnn-tf"]
	path = mask-rcnn
	url = https://github.com/NVIDIA/TensorRT/tree/master/samples/opensource/sampleUffMaskRCNN