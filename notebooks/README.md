# Available Notebooks

## Inference

* [inference/mask-rcnn.ipynb](inference/mask-rcnn.ipynb) 

  This notebook run Mask-RCNN trained on Coco dataset or either TPU or GPU. 

  Run in [Colab](https://colab.research.google.com/github/nhdchicken/nhd-colab/blob/master/notebooks/inference/mask-rcnn.ipynb)

## Incubation

* [incubation/matterport-mask-rcnn/train_shapes.ipynb](incubation/matterport-mask-rcnn/train_shapes.ipynb)

  This notebook demonstrate how to train Mask R-CNN using synthetic shapes rather 
  than images
  
  Run in [Colab](https://colab.research.google.com/github/nhdchicken/nhd-colab/blob/master/notebooks/incubation/matterport-mask-rcnn/train_shapes.ipynb) 
  
### Yolo V4

[Yolo V4](https://arxiv.org/pdf/2004.10934.pdf) has been published on April 23, 2020 and therefore is brand new. 
Surprisingly has a project (https://github.com/hunglc007/tensorflow-yolov4-tflite) which is quite interesting
as it implement the darknet framework using TensorFlow2 and provides various convertion to go to TFLite, 
of TensorRT (NVidia)

#### Discovery

* [incubation/yolov4/discovery.ipynb](incubation/yolov4/discovery.ipynb) 

  This notebook explore the YoloV4 port to TensorFlow as a darknet backend. 

  Run in [Colab](https://colab.research.google.com/github/nhdchicken/nhd-colab/blob/master/notebooks/incubation/yolov4/discovery.ipynb)
  