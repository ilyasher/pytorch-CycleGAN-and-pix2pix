"""General-purpose test script for image-to-image translation.

Once you have trained your model with train.py, you can use this script to test the model.
It will load a saved model from '--checkpoints_dir' and save the results to '--results_dir'.

It first creates model and dataset given the option. It will hard-code some parameters.
It then runs inference for '--num_test' images and save results to an HTML file.

Example (You need to train models first or download pre-trained models from our website):
    Test a CycleGAN model (both sides):
        python test.py --dataroot ./datasets/maps --name maps_cyclegan --model cycle_gan

    Test a CycleGAN model (one side only):
        python test.py --dataroot datasets/horse2zebra/testA --name horse2zebra_pretrained --model test --no_dropout

    The option '--model test' is used for generating CycleGAN results only for one side.
    This option will automatically set '--dataset_mode single', which only loads the images from one set.
    On the contrary, using '--model cycle_gan' requires loading and generating results in both directions,
    which is sometimes unnecessary. The results will be saved at ./results/.
    Use '--results_dir <directory_path_to_save_result>' to specify the results directory.

    Test a pix2pix model:
        python test.py --dataroot ./datasets/facades --name facades_pix2pix --model pix2pix --direction BtoA

See options/base_options.py and options/test_options.py for more test options.
See training and test tips at: https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/docs/tips.md
See frequently asked questions at: https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/docs/qa.md
"""
from pix2pix.options.test_options import TestOptions
from pix2pix.data import create_dataset
from pix2pix.models import create_model
from pix2pix.util import util

import os
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter
import torchvision.transforms as transforms

def trim_img(img, margin=2):
    w, h = img.size
    return img.crop((margin, margin, w-margin, h-margin))

class Model():

    def __init__(self):

        args = '--dataroot /tmp/full.png --name mountains_pix2pix --model pix2pix --checkpoints_dir ./model_weights/ --dataset_mode single_image --num_test 1'
        args = args.split()

        opt = TestOptions().parse(args)  # get test options
        # hard-code some parameters for test
        opt.num_threads = 0   # test code only supports num_threads = 1
        opt.batch_size = 1    # test code only supports batch_size = 1
        opt.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
        opt.no_flip = True    # no flip; comment this line if results on flipped images are needed.
        opt.display_id = -1   # no visdom display; the test code saves the results to a HTML file.

        dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
        model = create_model(opt)      # create a model given opt.model and other options
        model.setup(opt)               # regular setup: load and print networks; create schedulers

        self.model = model
        self.dataset = dataset
        self.heights = np.zeros(shape=(252,252), dtype=np.float64)

    def apply(self):


        model = self.model
        data = None
        for d in self.dataset:
            data = d

        model.eval()
        model.set_input(data)  # unpack data from data loader


        model.test()           # run inference
        visuals = model.get_current_visuals()  # get image results


        # Get heightmap as RGB image from model
        heightmap_img = util.tensor2im(visuals['fake_B']).astype(np.float64)

        heightmap_img = Image.fromarray(heightmap_img.astype(np.uint8))
        heightmap_img = trim_img(heightmap_img)

        heightmap_img.convert('L').save('/tmp/heightmap.png') # Save greyscale image


        return heightmap_img

    def get_heightmap(self):
        heightmap_img = np.array(self.apply()).astype(np.float64)

        # Convert from RGB heightmap to heights in meters
        # Red   = min(255, height/64)
        # Green = min(255, height/8)
        # Blue  = min(255, height)
        red   = heightmap_img[:, :, 0]
        green = heightmap_img[:, :, 1]
        blue  = heightmap_img[:, :, 2]
        heightmap = red*64 + green*8 + blue # Approximation
        # heightmap = np.maximum(red*64, np.maximum(green*8, blue))

        # Smooth out rough edges
        heightmap = gaussian_filter(heightmap, sigma=0.8)

        # Convert from meters to pixels
        heightmap = heightmap / 70

        self.heights = heightmap

    def heights_list(self):
        return self.heights.flatten().tolist()
