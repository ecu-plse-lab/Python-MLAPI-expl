#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('git clone https://github.com/NVlabs/stylegan.git')


# In[ ]:


cd stylegan/


# In[ ]:


get_ipython().system('wget https://www.dropbox.com/s/ucxejhn0xzv4nqi/network-snapshot-007961.pkl')


# In[ ]:


get_ipython().system('mkdir pokemon')


# In[ ]:


from PIL import Image
import os, sys

path ="/kaggle/input/kaggle-one-shot-pokemon/kaggle-one-shot-pokemon/pokemon-a/"
out="/kaggle/working/stylegan/pokemon/"

dirs = os.listdir( path )

n=0
for item in dirs:
        try:
            if os.path.isfile(path+item):
                im = Image.open(path+item)
                longer_side = max(im.size)

                horizontal_padding = (longer_side - im.size[0]) / 2
                vertical_padding = (longer_side - im.size[1]) / 2
                f, e = os.path.splitext(path+item)
                imResize = im.crop(
                (
                    -horizontal_padding,
                    -vertical_padding,
                    im.size[0] + horizontal_padding,
                    im.size[1] + vertical_padding
                )
                )
                RGB = imResize.convert('RGB')
                little = RGB.resize((512,512), Image.ANTIALIAS)

                little.save(out +  str(n) +'resize.jpg', 'JPEG', quality=90)
                n+=1
            
        except Exception as e:
            print(e)


# In[ ]:


import matplotlib.pyplot as plt
import matplotlib.image as mpimg
img=mpimg.imread('/kaggle/working/stylegan/pokemon/900resize.jpg')
imgplot = plt.imshow(img)
plt.show()


# In[ ]:


get_ipython().system('python dataset_tool.py create_from_images datasets/smalls/ /kaggle/working/stylegan/pokemon/')


# In[ ]:


cd training/


# In[ ]:


get_ipython().run_cell_magic('writefile', 'training_loop.py ', '# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.\n#\n# This work is licensed under the Creative Commons Attribution-NonCommercial\n# 4.0 International License. To view a copy of this license, visit\n# http://creativecommons.org/licenses/by-nc/4.0/ or send a letter to\n# Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.\n\n"""Main training script."""\n\nimport os\nimport numpy as np\nimport tensorflow as tf\nimport dnnlib\nimport dnnlib.tflib as tflib\nfrom dnnlib.tflib.autosummary import autosummary\n\nimport config\nimport train\nfrom training import dataset\nfrom training import misc\nfrom metrics import metric_base\n\n#----------------------------------------------------------------------------\n# Just-in-time processing of training images before feeding them to the networks.\n\ndef process_reals(x, lod, mirror_augment, drange_data, drange_net):\n    with tf.name_scope(\'ProcessReals\'):\n        with tf.name_scope(\'DynamicRange\'):\n            x = tf.cast(x, tf.float32)\n            x = misc.adjust_dynamic_range(x, drange_data, drange_net)\n        if mirror_augment:\n            with tf.name_scope(\'MirrorAugment\'):\n                s = tf.shape(x)\n                mask = tf.random_uniform([s[0], 1, 1, 1], 0.0, 1.0)\n                mask = tf.tile(mask, [1, s[1], s[2], s[3]])\n                x = tf.where(mask < 0.5, x, tf.reverse(x, axis=[3]))\n        with tf.name_scope(\'FadeLOD\'): # Smooth crossfade between consecutive levels-of-detail.\n            s = tf.shape(x)\n            y = tf.reshape(x, [-1, s[1], s[2]//2, 2, s[3]//2, 2])\n            y = tf.reduce_mean(y, axis=[3, 5], keepdims=True)\n            y = tf.tile(y, [1, 1, 1, 2, 1, 2])\n            y = tf.reshape(y, [-1, s[1], s[2], s[3]])\n            x = tflib.lerp(x, y, lod - tf.floor(lod))\n        with tf.name_scope(\'UpscaleLOD\'): # Upscale to match the expected input/output size of the networks.\n            s = tf.shape(x)\n            factor = tf.cast(2 ** tf.floor(lod), tf.int32)\n            x = tf.reshape(x, [-1, s[1], s[2], 1, s[3], 1])\n            x = tf.tile(x, [1, 1, 1, factor, 1, factor])\n            x = tf.reshape(x, [-1, s[1], s[2] * factor, s[3] * factor])\n        return x\n\n#----------------------------------------------------------------------------\n# Evaluate time-varying training parameters.\n\ndef training_schedule(\n    cur_nimg,\n    training_set,\n    num_gpus,\n    lod_initial_resolution  = 4,        # Image resolution used at the beginning.\n    lod_training_kimg       = 600,      # Thousands of real images to show before doubling the resolution.\n    lod_transition_kimg     = 600,      # Thousands of real images to show when fading in new layers.\n    minibatch_base          = 16,       # Maximum minibatch size, divided evenly among GPUs.\n    minibatch_dict          = {},       # Resolution-specific overrides.\n    max_minibatch_per_gpu   = {},       # Resolution-specific maximum minibatch size per GPU.\n    G_lrate_base            = 0.001,    # Learning rate for the generator.\n    G_lrate_dict            = {},       # Resolution-specific overrides.\n    D_lrate_base            = 0.001,    # Learning rate for the discriminator.\n    D_lrate_dict            = {},       # Resolution-specific overrides.\n    lrate_rampup_kimg       = 0,        # Duration of learning rate ramp-up.\n    tick_kimg_base          = 160,      # Default interval of progress snapshots.\n    tick_kimg_dict          = {4: 160, 8:140, 16:120, 32:100, 64:80, 128:60, 256:40, 512:30, 1024:20}): # Resolution-specific overrides.\n\n    # Initialize result dict.\n    s = dnnlib.EasyDict()\n    s.kimg = cur_nimg / 1000.0\n\n    # Training phase.\n    phase_dur = lod_training_kimg + lod_transition_kimg\n    phase_idx = int(np.floor(s.kimg / phase_dur)) if phase_dur > 0 else 0\n    phase_kimg = s.kimg - phase_idx * phase_dur\n\n    # Level-of-detail and resolution.\n    s.lod = training_set.resolution_log2\n    s.lod -= np.floor(np.log2(lod_initial_resolution))\n    s.lod -= phase_idx\n    if lod_transition_kimg > 0:\n        s.lod -= max(phase_kimg - lod_training_kimg, 0.0) / lod_transition_kimg\n    s.lod = max(s.lod, 0.0)\n    s.resolution = 2 ** (training_set.resolution_log2 - int(np.floor(s.lod)))\n\n    # Minibatch size.\n    s.minibatch = minibatch_dict.get(s.resolution, minibatch_base)\n    s.minibatch -= s.minibatch % num_gpus\n    if s.resolution in max_minibatch_per_gpu:\n        s.minibatch = min(s.minibatch, max_minibatch_per_gpu[s.resolution] * num_gpus)\n\n    # Learning rate.\n    s.G_lrate = G_lrate_dict.get(s.resolution, G_lrate_base)\n    s.D_lrate = D_lrate_dict.get(s.resolution, D_lrate_base)\n    if lrate_rampup_kimg > 0:\n        rampup = min(s.kimg / lrate_rampup_kimg, 1.0)\n        s.G_lrate *= rampup\n        s.D_lrate *= rampup\n\n    # Other parameters.\n    s.tick_kimg = tick_kimg_dict.get(s.resolution, tick_kimg_base)\n    return s\n\n#----------------------------------------------------------------------------\n# Main training script.\n\ndef training_loop(\n    submit_config,\n    G_args                  = {},       # Options for generator network.\n    D_args                  = {},       # Options for discriminator network.\n    G_opt_args              = {},       # Options for generator optimizer.\n    D_opt_args              = {},       # Options for discriminator optimizer.\n    G_loss_args             = {},       # Options for generator loss.\n    D_loss_args             = {},       # Options for discriminator loss.\n    dataset_args            = {},       # Options for dataset.load_dataset().\n    sched_args              = {},       # Options for train.TrainingSchedule.\n    grid_args               = {},       # Options for train.setup_snapshot_image_grid().\n    metric_arg_list         = [],       # Options for MetricGroup.\n    tf_config               = {},       # Options for tflib.init_tf().\n    G_smoothing_kimg        = 10.0,     # Half-life of the running average of generator weights.\n    D_repeats               = 1,        # How many times the discriminator is trained per G iteration.\n    minibatch_repeats       = 4,        # Number of minibatches to run before adjusting training parameters.\n    reset_opt_for_new_lod   = True,     # Reset optimizer internal state (e.g. Adam moments) when new layers are introduced?\n    total_kimg              = 7991,    # Total length of the training, measured in thousands of real images.\n    mirror_augment          = False,    # Enable mirror augment?\n    drange_net              = [-1,1],   # Dynamic range used when feeding image data to the networks.\n    image_snapshot_ticks    = 1,        # How often to export image snapshots?\n    network_snapshot_ticks  = 1,       # How often to export network snapshots?\n    save_tf_graph           = False,    # Include full TensorFlow computation graph in the tfevents file?\n    save_weight_histograms  = False,    # Include weight histograms in the tfevents file?\n    resume_run_id           = "/kaggle/working/stylegan/network-snapshot-007961.pkl",     # Run ID or network pkl to resume training from, None = start from scratch.\n    resume_snapshot         = None,     # Snapshot index to resume training from, None = autodetect.\n    resume_kimg             = 7961,      # Assumed training progress at the beginning. Affects reporting and training schedule.\n    resume_time             = 0.0):     # Assumed wallclock time at the beginning. Affects reporting.\n\n    # Initialize dnnlib and TensorFlow.\n    ctx = dnnlib.RunContext(submit_config, train)\n    tflib.init_tf(tf_config)\n\n    # Load training set.\n    training_set = dataset.load_dataset(data_dir=config.data_dir, verbose=True, **dataset_args)\n\n    # Construct networks.\n    with tf.device(\'/gpu:0\'):\n        if resume_run_id is not None:\n            network_pkl = misc.locate_network_pkl(resume_run_id, resume_snapshot)\n            print(\'Loading networks from "%s"...\' % network_pkl)\n            G, D, Gs = misc.load_pkl(network_pkl)\n        else:\n            print(\'Constructing networks...\')\n            G = tflib.Network(\'G\', num_channels=training_set.shape[0], resolution=training_set.shape[1], label_size=training_set.label_size, **G_args)\n            D = tflib.Network(\'D\', num_channels=training_set.shape[0], resolution=training_set.shape[1], label_size=training_set.label_size, **D_args)\n            Gs = G.clone(\'Gs\')\n    G.print_layers(); D.print_layers()\n\n    print(\'Building TensorFlow graph...\')\n    with tf.name_scope(\'Inputs\'), tf.device(\'/cpu:0\'):\n        lod_in          = tf.placeholder(tf.float32, name=\'lod_in\', shape=[])\n        lrate_in        = tf.placeholder(tf.float32, name=\'lrate_in\', shape=[])\n        minibatch_in    = tf.placeholder(tf.int32, name=\'minibatch_in\', shape=[])\n        minibatch_split = minibatch_in // submit_config.num_gpus\n        Gs_beta         = 0.5 ** tf.div(tf.cast(minibatch_in, tf.float32), G_smoothing_kimg * 1000.0) if G_smoothing_kimg > 0.0 else 0.0\n\n    G_opt = tflib.Optimizer(name=\'TrainG\', learning_rate=lrate_in, **G_opt_args)\n    D_opt = tflib.Optimizer(name=\'TrainD\', learning_rate=lrate_in, **D_opt_args)\n    for gpu in range(submit_config.num_gpus):\n        with tf.name_scope(\'GPU%d\' % gpu), tf.device(\'/gpu:%d\' % gpu):\n            G_gpu = G if gpu == 0 else G.clone(G.name + \'_shadow\')\n            D_gpu = D if gpu == 0 else D.clone(D.name + \'_shadow\')\n            lod_assign_ops = [tf.assign(G_gpu.find_var(\'lod\'), lod_in), tf.assign(D_gpu.find_var(\'lod\'), lod_in)]\n            reals, labels = training_set.get_minibatch_tf()\n            reals = process_reals(reals, lod_in, mirror_augment, training_set.dynamic_range, drange_net)\n            with tf.name_scope(\'G_loss\'), tf.control_dependencies(lod_assign_ops):\n                G_loss = dnnlib.util.call_func_by_name(G=G_gpu, D=D_gpu, opt=G_opt, training_set=training_set, minibatch_size=minibatch_split, **G_loss_args)\n            with tf.name_scope(\'D_loss\'), tf.control_dependencies(lod_assign_ops):\n                D_loss = dnnlib.util.call_func_by_name(G=G_gpu, D=D_gpu, opt=D_opt, training_set=training_set, minibatch_size=minibatch_split, reals=reals, labels=labels, **D_loss_args)\n            G_opt.register_gradients(tf.reduce_mean(G_loss), G_gpu.trainables)\n            D_opt.register_gradients(tf.reduce_mean(D_loss), D_gpu.trainables)\n    G_train_op = G_opt.apply_updates()\n    D_train_op = D_opt.apply_updates()\n\n    Gs_update_op = Gs.setup_as_moving_average_of(G, beta=Gs_beta)\n    with tf.device(\'/gpu:0\'):\n        try:\n            peak_gpu_mem_op = tf.contrib.memory_stats.MaxBytesInUse()\n        except tf.errors.NotFoundError:\n            peak_gpu_mem_op = tf.constant(0)\n\n    print(\'Setting up snapshot image grid...\')\n    grid_size, grid_reals, grid_labels, grid_latents = misc.setup_snapshot_image_grid(G, training_set, **grid_args)\n    sched = training_schedule(cur_nimg=total_kimg*1000, training_set=training_set, num_gpus=submit_config.num_gpus, **sched_args)\n    grid_fakes = Gs.run(grid_latents, grid_labels, is_validation=True, minibatch_size=sched.minibatch//submit_config.num_gpus)\n\n    print(\'Setting up run dir...\')\n    misc.save_image_grid(grid_reals, os.path.join(submit_config.run_dir, \'reals.png\'), drange=training_set.dynamic_range, grid_size=grid_size)\n    misc.save_image_grid(grid_fakes, os.path.join(submit_config.run_dir, \'fakes%06d.png\' % resume_kimg), drange=drange_net, grid_size=grid_size)\n    summary_log = tf.summary.FileWriter(submit_config.run_dir)\n    if save_tf_graph:\n        summary_log.add_graph(tf.get_default_graph())\n    if save_weight_histograms:\n        G.setup_weight_histograms(); D.setup_weight_histograms()\n    metrics = metric_base.MetricGroup(metric_arg_list)\n\n    print(\'Training...\\n\')\n    ctx.update(\'\', cur_epoch=resume_kimg, max_epoch=total_kimg)\n    maintenance_time = ctx.get_last_update_interval()\n    cur_nimg = int(resume_kimg * 1000)\n    cur_tick = 0\n    tick_start_nimg = cur_nimg\n    prev_lod = -1.0\n    while cur_nimg < total_kimg * 1000:\n        if ctx.should_stop(): break\n\n        # Choose training parameters and configure training ops.\n        sched = training_schedule(cur_nimg=cur_nimg, training_set=training_set, num_gpus=submit_config.num_gpus, **sched_args)\n        training_set.configure(sched.minibatch // submit_config.num_gpus, sched.lod)\n        if reset_opt_for_new_lod:\n            if np.floor(sched.lod) != np.floor(prev_lod) or np.ceil(sched.lod) != np.ceil(prev_lod):\n                G_opt.reset_optimizer_state(); D_opt.reset_optimizer_state()\n        prev_lod = sched.lod\n\n        # Run training ops.\n        for _mb_repeat in range(minibatch_repeats):\n            for _D_repeat in range(D_repeats):\n                tflib.run([D_train_op, Gs_update_op], {lod_in: sched.lod, lrate_in: sched.D_lrate, minibatch_in: sched.minibatch})\n                cur_nimg += sched.minibatch\n            tflib.run([G_train_op], {lod_in: sched.lod, lrate_in: sched.G_lrate, minibatch_in: sched.minibatch})\n\n        # Perform maintenance tasks once per tick.\n        done = (cur_nimg >= total_kimg * 1000)\n        if cur_nimg >= tick_start_nimg + sched.tick_kimg * 1000 or done:\n            cur_tick += 1\n            tick_kimg = (cur_nimg - tick_start_nimg) / 1000.0\n            tick_start_nimg = cur_nimg\n            tick_time = ctx.get_time_since_last_update()\n            total_time = ctx.get_time_since_start() + resume_time\n\n            # Report progress.\n            print(\'tick %-5d kimg %-8.1f lod %-5.2f minibatch %-4d time %-12s sec/tick %-7.1f sec/kimg %-7.2f maintenance %-6.1f gpumem %-4.1f\' % (\n                autosummary(\'Progress/tick\', cur_tick),\n                autosummary(\'Progress/kimg\', cur_nimg / 1000.0),\n                autosummary(\'Progress/lod\', sched.lod),\n                autosummary(\'Progress/minibatch\', sched.minibatch),\n                dnnlib.util.format_time(autosummary(\'Timing/total_sec\', total_time)),\n                autosummary(\'Timing/sec_per_tick\', tick_time),\n                autosummary(\'Timing/sec_per_kimg\', tick_time / tick_kimg),\n                autosummary(\'Timing/maintenance_sec\', maintenance_time),\n                autosummary(\'Resources/peak_gpu_mem_gb\', peak_gpu_mem_op.eval() / 2**30)))\n            autosummary(\'Timing/total_hours\', total_time / (60.0 * 60.0))\n            autosummary(\'Timing/total_days\', total_time / (24.0 * 60.0 * 60.0))\n\n            # Save snapshots.\n            if cur_tick % image_snapshot_ticks == 0 or done:\n                grid_fakes = Gs.run(grid_latents, grid_labels, is_validation=True, minibatch_size=sched.minibatch//submit_config.num_gpus)\n                misc.save_image_grid(grid_fakes, os.path.join(submit_config.run_dir, \'fakes%06d.png\' % (cur_nimg // 1000)), drange=drange_net, grid_size=grid_size)\n            if cur_tick % network_snapshot_ticks == 0 or done or cur_tick == 1:\n                pkl = os.path.join(submit_config.run_dir, \'network-snapshot-%06d.pkl\' % (cur_nimg // 1000))\n                misc.save_pkl((G, D, Gs), pkl)\n                metrics.run(pkl, run_dir=submit_config.run_dir, num_gpus=submit_config.num_gpus, tf_config=tf_config)\n\n            # Update summaries and RunContext.\n            metrics.update_autosummaries()\n            tflib.autosummary.save_summaries(summary_log, cur_nimg)\n            ctx.update(\'%.2f\' % sched.lod, cur_epoch=cur_nimg // 1000, max_epoch=total_kimg)\n            maintenance_time = ctx.get_last_update_interval() - tick_time\n\n    # Write final results.\n    misc.save_pkl((G, D, Gs), os.path.join(submit_config.run_dir, \'network-final.pkl\'))\n    summary_log.close()\n\n    ctx.close()\n\n#----------------------------------------------------------------------------')


# In[ ]:


cd ..


# In[ ]:


# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution-NonCommercial
# 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc/4.0/ or send a letter to
# Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

"""Main entry point for training StyleGAN and ProGAN networks."""

import copy
import dnnlib
from dnnlib import EasyDict

import config
from metrics import metric_base

#----------------------------------------------------------------------------
# Official training configs for StyleGAN, targeted mainly for FFHQ.

if 1:
    desc          = 'sgan'                                                                 # Description string included in result subdir name.
    train         = EasyDict(run_func_name='training.training_loop.training_loop')         # Options for training loop.
    G             = EasyDict(func_name='training.networks_stylegan.G_style')               # Options for generator network.
    D             = EasyDict(func_name='training.networks_stylegan.D_basic')               # Options for discriminator network.
    G_opt         = EasyDict(beta1=0.0, beta2=0.99, epsilon=1e-8)                          # Options for generator optimizer.
    D_opt         = EasyDict(beta1=0.0, beta2=0.99, epsilon=1e-8)                          # Options for discriminator optimizer.
    G_loss        = EasyDict(func_name='training.loss.G_logistic_nonsaturating')           # Options for generator loss.
    D_loss        = EasyDict(func_name='training.loss.D_logistic_simplegp', r1_gamma=10.0) # Options for discriminator loss.
    dataset       = EasyDict()                                                             # Options for load_dataset().
    sched         = EasyDict()                                                             # Options for TrainingSchedule.
    grid          = EasyDict(size='4k', layout='random')                                   # Options for setup_snapshot_image_grid().
    #metrics       = [metric_base.fid50k]                                                   # Options for MetricGroup.
    submit_config = dnnlib.SubmitConfig()                                                  # Options for dnnlib.submit_run().
    tf_config     = {'rnd.np_random_seed': 1000}                                           # Options for tflib.init_tf().

    # Dataset.
    desc += '-custom';     dataset = EasyDict(tfrecord_dir='smalls', resolution=512);              train.mirror_augment = True
    #desc += '-celebahq'; dataset = EasyDict(tfrecord_dir='celebahq');          train.mirror_augment = True
    #desc += '-bedroom';  dataset = EasyDict(tfrecord_dir='lsun-bedroom-full'); train.mirror_augment = False
    #desc += '-car';      dataset = EasyDict(tfrecord_dir='lsun-car-512x384');  train.mirror_augment = False
    #desc += '-cat';      dataset = EasyDict(tfrecord_dir='lsun-cat-full');     train.mirror_augment = False

    # Number of GPUs.
    desc += '-1gpu'; submit_config.num_gpus = 1; sched.minibatch_base = 4; sched.minibatch_dict = {4: 128, 8: 128, 16: 128, 32: 64, 64: 32, 128: 16, 256: 8, 512: 4}
    #desc += '-2gpu'; submit_config.num_gpus = 2; sched.minibatch_base = 8; sched.minibatch_dict = {4: 256, 8: 256, 16: 128, 32: 64, 64: 32, 128: 16, 256: 8}
    #desc += '-4gpu'; submit_config.num_gpus = 4; sched.minibatch_base = 16; sched.minibatch_dict = {4: 512, 8: 256, 16: 128, 32: 64, 64: 32, 128: 16}
    #desc += '-8gpu'; submit_config.num_gpus = 8; sched.minibatch_base = 32; sched.minibatch_dict = {4: 512, 8: 256, 16: 128, 32: 64, 64: 32}

    # Default options.
    train.total_kimg = 7991
    sched.lod_initial_resolution = 8
    sched.G_lrate_dict = {128: 0.0015, 256: 0.002, 512: 0.003, 1024: 0.003}
    sched.D_lrate_dict = EasyDict(sched.G_lrate_dict)

    # WGAN-GP loss for CelebA-HQ.
    #desc += '-wgangp'; G_loss = EasyDict(func_name='training.loss.G_wgan'); D_loss = EasyDict(func_name='training.loss.D_wgan_gp'); sched.G_lrate_dict = {k: min(v, 0.002) for k, v in sched.G_lrate_dict.items()}; sched.D_lrate_dict = EasyDict(sched.G_lrate_dict)

    # Table 1.
    #desc += '-tuned-baseline'; G.use_styles = False; G.use_pixel_norm = True; G.use_instance_norm = False; G.mapping_layers = 0; G.truncation_psi = None; G.const_input_layer = False; G.style_mixing_prob = 0.0; G.use_noise = False
    #desc += '-add-mapping-and-styles'; G.const_input_layer = False; G.style_mixing_prob = 0.0; G.use_noise = False
    #desc += '-remove-traditional-input'; G.style_mixing_prob = 0.0; G.use_noise = False
    #desc += '-add-noise-inputs'; G.style_mixing_prob = 0.0
    #desc += '-mixing-regularization' # default

    # Table 2.
    #desc += '-mix0'; G.style_mixing_prob = 0.0
    #desc += '-mix50'; G.style_mixing_prob = 0.5
    #desc += '-mix90'; G.style_mixing_prob = 0.9 # default
    #desc += '-mix100'; G.style_mixing_prob = 1.0

    # Table 4.
    #desc += '-traditional-0'; G.use_styles = False; G.use_pixel_norm = True; G.use_instance_norm = False; G.mapping_layers = 0; G.truncation_psi = None; G.const_input_layer = False; G.style_mixing_prob = 0.0; G.use_noise = False
    #desc += '-traditional-8'; G.use_styles = False; G.use_pixel_norm = True; G.use_instance_norm = False; G.mapping_layers = 8; G.truncation_psi = None; G.const_input_layer = False; G.style_mixing_prob = 0.0; G.use_noise = False
    #desc += '-stylebased-0'; G.mapping_layers = 0
    #desc += '-stylebased-1'; G.mapping_layers = 1
    #desc += '-stylebased-2'; G.mapping_layers = 2
    #desc += '-stylebased-8'; G.mapping_layers = 8 # default

#----------------------------------------------------------------------------
# Official training configs for Progressive GAN, targeted mainly for CelebA-HQ.

if 0:
    desc          = 'pgan'                                                         # Description string included in result subdir name.
    train         = EasyDict(run_func_name='training.training_loop.training_loop') # Options for training loop.
    G             = EasyDict(func_name='training.networks_progan.G_paper')         # Options for generator network.
    D             = EasyDict(func_name='training.networks_progan.D_paper')         # Options for discriminator network.
    G_opt         = EasyDict(beta1=0.0, beta2=0.99, epsilon=1e-8)                  # Options for generator optimizer.
    D_opt         = EasyDict(beta1=0.0, beta2=0.99, epsilon=1e-8)                  # Options for discriminator optimizer.
    G_loss        = EasyDict(func_name='training.loss.G_wgan')                     # Options for generator loss.
    D_loss        = EasyDict(func_name='training.loss.D_wgan_gp')                  # Options for discriminator loss.
    dataset       = EasyDict()                                                     # Options for load_dataset().
    sched         = EasyDict()                                                     # Options for TrainingSchedule.
    grid          = EasyDict(size='1080p', layout='random')                        # Options for setup_snapshot_image_grid().
    #metrics       = [metric_base.fid50k]                                           # Options for MetricGroup.
    submit_config = dnnlib.SubmitConfig()                                          # Options for dnnlib.submit_run().
    tf_config     = {'rnd.np_random_seed': 1000}                                   # Options for tflib.init_tf().

    # Dataset (choose one).
    #desc += '-celebahq';            dataset = EasyDict(tfrecord_dir='celebahq'); train.mirror_augment = True
    #desc += '-celeba';              dataset = EasyDict(tfrecord_dir='celeba'); train.mirror_augment = True
    #desc += '-cifar10';             dataset = EasyDict(tfrecord_dir='cifar10')
    #desc += '-cifar100';            dataset = EasyDict(tfrecord_dir='cifar100')
    #desc += '-svhn';                dataset = EasyDict(tfrecord_dir='svhn')
    #desc += '-mnist';               dataset = EasyDict(tfrecord_dir='mnist')
    #desc += '-mnistrgb';            dataset = EasyDict(tfrecord_dir='mnistrgb')
    #desc += '-syn1024rgb';          dataset = EasyDict(class_name='training.dataset.SyntheticDataset', resolution=1024, num_channels=3)
    #desc += '-lsun-airplane';       dataset = EasyDict(tfrecord_dir='lsun-airplane-100k');       train.mirror_augment = True
    #desc += '-lsun-bedroom';        dataset = EasyDict(tfrecord_dir='lsun-bedroom-100k');        train.mirror_augment = True
    #desc += '-lsun-bicycle';        dataset = EasyDict(tfrecord_dir='lsun-bicycle-100k');        train.mirror_augment = True
    #desc += '-lsun-bird';           dataset = EasyDict(tfrecord_dir='lsun-bird-100k');           train.mirror_augment = True
    #desc += '-lsun-boat';           dataset = EasyDict(tfrecord_dir='lsun-boat-100k');           train.mirror_augment = True
    #desc += '-lsun-bottle';         dataset = EasyDict(tfrecord_dir='lsun-bottle-100k');         train.mirror_augment = True
    #desc += '-lsun-bridge';         dataset = EasyDict(tfrecord_dir='lsun-bridge-100k');         train.mirror_augment = True
    #desc += '-lsun-bus';            dataset = EasyDict(tfrecord_dir='lsun-bus-100k');            train.mirror_augment = True
    #desc += '-lsun-car';            dataset = EasyDict(tfrecord_dir='lsun-car-100k');            train.mirror_augment = True
    #desc += '-lsun-cat';            dataset = EasyDict(tfrecord_dir='lsun-cat-100k');            train.mirror_augment = True
    #desc += '-lsun-chair';          dataset = EasyDict(tfrecord_dir='lsun-chair-100k');          train.mirror_augment = True
    #desc += '-lsun-churchoutdoor';  dataset = EasyDict(tfrecord_dir='lsun-churchoutdoor-100k');  train.mirror_augment = True
    #desc += '-lsun-classroom';      dataset = EasyDict(tfrecord_dir='lsun-classroom-100k');      train.mirror_augment = True
    #desc += '-lsun-conferenceroom'; dataset = EasyDict(tfrecord_dir='lsun-conferenceroom-100k'); train.mirror_augment = True
    #desc += '-lsun-cow';            dataset = EasyDict(tfrecord_dir='lsun-cow-100k');            train.mirror_augment = True
    #desc += '-lsun-diningroom';     dataset = EasyDict(tfrecord_dir='lsun-diningroom-100k');     train.mirror_augment = True
    #desc += '-lsun-diningtable';    dataset = EasyDict(tfrecord_dir='lsun-diningtable-100k');    train.mirror_augment = True
    #desc += '-lsun-dog';            dataset = EasyDict(tfrecord_dir='lsun-dog-100k');            train.mirror_augment = True
    #desc += '-lsun-horse';          dataset = EasyDict(tfrecord_dir='lsun-horse-100k');          train.mirror_augment = True
    #desc += '-lsun-kitchen';        dataset = EasyDict(tfrecord_dir='lsun-kitchen-100k');        train.mirror_augment = True
    #desc += '-lsun-livingroom';     dataset = EasyDict(tfrecord_dir='lsun-livingroom-100k');     train.mirror_augment = True
    #desc += '-lsun-motorbike';      dataset = EasyDict(tfrecord_dir='lsun-motorbike-100k');      train.mirror_augment = True
    #desc += '-lsun-person';         dataset = EasyDict(tfrecord_dir='lsun-person-100k');         train.mirror_augment = True
    #desc += '-lsun-pottedplant';    dataset = EasyDict(tfrecord_dir='lsun-pottedplant-100k');    train.mirror_augment = True
    #desc += '-lsun-restaurant';     dataset = EasyDict(tfrecord_dir='lsun-restaurant-100k');     train.mirror_augment = True
    #desc += '-lsun-sheep';          dataset = EasyDict(tfrecord_dir='lsun-sheep-100k');          train.mirror_augment = True
    #desc += '-lsun-sofa';           dataset = EasyDict(tfrecord_dir='lsun-sofa-100k');           train.mirror_augment = True
    #desc += '-lsun-tower';          dataset = EasyDict(tfrecord_dir='lsun-tower-100k');          train.mirror_augment = True
    #desc += '-lsun-train';          dataset = EasyDict(tfrecord_dir='lsun-train-100k');          train.mirror_augment = True
    #desc += '-lsun-tvmonitor';      dataset = EasyDict(tfrecord_dir='lsun-tvmonitor-100k');      train.mirror_augment = True

    # Conditioning & snapshot options.
    #desc += '-cond'; dataset.max_label_size = 'full' # conditioned on full label
    #desc += '-cond1'; dataset.max_label_size = 1 # conditioned on first component of the label
    #desc += '-g4k'; grid.size = '4k'
    #desc += '-grpc'; grid.layout = 'row_per_class'

    # Config presets (choose one).
    #desc += '-preset-v1-1gpu'; submit_config.num_gpus = 1; D.mbstd_group_size = 16; sched.minibatch_base = 16; sched.minibatch_dict = {256: 14, 512: 6, 1024: 3}; sched.lod_training_kimg = 800; sched.lod_transition_kimg = 800; train.total_kimg = 19000
    #desc += '-preset-v2-1gpu'; submit_config.num_gpus = 1; sched.minibatch_base = 4; sched.minibatch_dict = {4: 128, 8: 128, 16: 128, 32: 64, 64: 32, 128: 16, 256: 8, 512: 4}; sched.G_lrate_dict = {1024: 0.0015}; sched.D_lrate_dict = EasyDict(sched.G_lrate_dict); train.total_kimg = 12000
    #desc += '-preset-v2-2gpus'; submit_config.num_gpus = 2; sched.minibatch_base = 8; sched.minibatch_dict = {4: 256, 8: 256, 16: 128, 32: 64, 64: 32, 128: 16, 256: 8}; sched.G_lrate_dict = {512: 0.0015, 1024: 0.002}; sched.D_lrate_dict = EasyDict(sched.G_lrate_dict); train.total_kimg = 12000
    #desc += '-preset-v2-4gpus'; submit_config.num_gpus = 4; sched.minibatch_base = 16; sched.minibatch_dict = {4: 512, 8: 256, 16: 128, 32: 64, 64: 32, 128: 16}; sched.G_lrate_dict = {256: 0.0015, 512: 0.002, 1024: 0.003}; sched.D_lrate_dict = EasyDict(sched.G_lrate_dict); train.total_kimg = 12000
    #desc += '-preset-v2-8gpus'; submit_config.num_gpus = 8; sched.minibatch_base = 32; sched.minibatch_dict = {4: 512, 8: 256, 16: 128, 32: 64, 64: 32}; sched.G_lrate_dict = {128: 0.0015, 256: 0.002, 512: 0.003, 1024: 0.003}; sched.D_lrate_dict = EasyDict(sched.G_lrate_dict); train.total_kimg = 12000

    # Numerical precision (choose one).
    #desc += '-fp32'; sched.max_minibatch_per_gpu = {256: 16, 512: 8, 1024: 4}
    #desc += '-fp16'; G.dtype = 'float16'; D.dtype = 'float16'; G.pixelnorm_epsilon=1e-4; G_opt.use_loss_scaling = True; D_opt.use_loss_scaling = True; sched.max_minibatch_per_gpu = {512: 16, 1024: 8}

    # Disable individual features.
    #desc += '-nogrowing'; sched.lod_initial_resolution = 1024; sched.lod_training_kimg = 0; sched.lod_transition_kimg = 0; train.total_kimg = 10000
    #desc += '-nopixelnorm'; G.use_pixelnorm = False
    #desc += '-nowscale'; G.use_wscale = False; D.use_wscale = False
    #desc += '-noleakyrelu'; G.use_leakyrelu = False
    #desc += '-nosmoothing'; train.G_smoothing_kimg = 0.0
    #desc += '-norepeat'; train.minibatch_repeats = 1
    #desc += '-noreset'; train.reset_opt_for_new_lod = False

    # Special modes.
    #desc += '-BENCHMARK'; sched.lod_initial_resolution = 4; sched.lod_training_kimg = 3; sched.lod_transition_kimg = 3; train.total_kimg = (8*2+1)*3; sched.tick_kimg_base = 1; sched.tick_kimg_dict = {}; train.image_snapshot_ticks = 1000; train.network_snapshot_ticks = 1000
    #desc += '-BENCHMARK0'; sched.lod_initial_resolution = 1024; train.total_kimg = 10; sched.tick_kimg_base = 1; sched.tick_kimg_dict = {}; train.image_snapshot_ticks = 1000; train.network_snapshot_ticks = 1000
    #desc += '-VERBOSE'; sched.tick_kimg_base = 1; sched.tick_kimg_dict = {}; train.image_snapshot_ticks = 1; train.network_snapshot_ticks = 100
    #desc += '-GRAPH'; train.save_tf_graph = True
    #desc += '-HIST'; train.save_weight_histograms = True

#----------------------------------------------------------------------------
# Main entry point for training.
# Calls the function indicated by 'train' using the selected options.

def main():
    kwargs = EasyDict(train)
    kwargs.update(G_args=G, D_args=D, G_opt_args=G_opt, D_opt_args=D_opt, G_loss_args=G_loss, D_loss_args=D_loss)
    kwargs.update(dataset_args=dataset, sched_args=sched, grid_args=grid, tf_config=tf_config)
    kwargs.submit_config = copy.deepcopy(submit_config)
    kwargs.submit_config.run_dir_root = dnnlib.submission.submit.get_template_from_path(config.result_dir)
    kwargs.submit_config.run_dir_ignore += config.run_dir_ignore
    kwargs.submit_config.run_desc = desc
    dnnlib.submit_run(**kwargs)

#----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

#----------------------------------------------------------------------------


# In[ ]:


import os
import pickle
import numpy as np
import math
import random
import matplotlib.pyplot as plt
import PIL.Image
import dnnlib
import dnnlib.tflib as tflib
import config
from tqdm import tqdm_notebook as tqdm

tflib.init_tf()


# In[ ]:


model = '/kaggle/working/stylegan/results/00000-sgan-custom-1gpu/network-snapshot-007991.pkl'

with open(model, 'rb') as f:
    _G, _D, Gs = pickle.load(f)

fmt = dict(func=tflib.convert_images_to_uint8, nchw_to_nhwc=True)
synthesis_kwargs = dict(output_transform=dict(func=tflib.convert_images_to_uint8, nchw_to_nhwc=True), minibatch_size=8)


# In[ ]:


truncation = 0.5


def bookmark(latents, new_faves):
    for f in new_faves:
        faves.append(latents[f])

def show_faves(faves):
    latents = np.array(faves)
    labels = np.zeros([latents.shape[0]] + Gs.input_shapes[1][1:])
    n = len(faves)
    nr, nc = math.ceil(n / 6), 6
    for r in range(nr):
        images = Gs.run(latents[6*r:min(n-1, 6*(r+1))], None, truncation_psi=truncation, randomize_noise=False, output_transform=fmt)
        img1 = np.concatenate([img for img in images], axis=1)
        plt.figure(figsize=(24,4))
        plt.imshow(img1)
        
def random_sample(num_images, scale):
    latents = np.random.RandomState(int(1000*random.random())).randn(num_images, *Gs.input_shapes[0][1:])
    labels = np.zeros([latents.shape[0]] + Gs.input_shapes[1][1:])
    images = Gs.run(latents, None, truncation_psi=truncation, randomize_noise=False, output_transform=fmt)
    images_ct = np.concatenate([img for img in images], axis=1)
    plt.figure(figsize=(scale*num_images, scale))
    plt.imshow(images_ct)
    return images, latents

def get_latent_interpolation(endpoints, num_frames_per, mode, shuffle):
    if shuffle:
        random.shuffle(endpoints)
    num_endpoints, dim = len(endpoints), len(endpoints[0])
    num_frames = num_frames_per * num_endpoints
    endpoints = np.array(endpoints)
    latents = np.zeros((num_frames, dim))
    for e in range(num_endpoints):
        e1, e2 = e, (e+1)%num_endpoints
        for t in range(num_frames_per):
            frame = e * num_frames_per + t
            r = 0.5 - 0.5 * np.cos(np.pi*t/(num_frames_per-1)) if mode == 'ease' else float(t) / num_frames_per
            latents[frame, :] = (1.0-r) * endpoints[e1,:] + r * endpoints[e2,:]
    return latents

def get_latent_interpolation_bspline(endpoints, nf, k, s, shuffle):
    if shuffle:
        random.shuffle(endpoints)
    x = np.array(endpoints)
    x = np.append(x, x[0,:].reshape(1, x.shape[1]), axis=0)
    nd = x.shape[1]
    latents = np.zeros((nd, nf))
    nss = list(range(1, 10)) + [10]*(nd-19) + list(range(10,0,-1))
    for i in tqdm(range(nd-9)):
        idx = list(range(i,i+10))
        tck, u = interpolate.splprep([x[:,j] for j in range(i,i+10)], k=k, s=s)
        out = interpolate.splev(np.linspace(0, 1, num=nf, endpoint=True), tck)
        latents[i:i+10,:] += np.array(out)
    latents = latents / np.array(nss).reshape((512,1))
    return latents.T


def generate_images(latents, labels):
    batch_size = 8
    num_frames = latents.shape[0]
    num_batches = int(np.ceil(num_frames/batch_size))
    images = []
    for b in tqdm(range(num_batches)):
        new_images = Gs.run(latents[b*batch_size:min((b+1)*batch_size, num_frames-1), :], None, truncation_psi=truncation, randomize_noise=False, output_transform=fmt)
        for img in new_images:
            images.append(img)
    return images

def make_movie(images, out_dir, out_name):
    temp_dir = 'frames%06d'%int(1000000*random.random())
    os.system('mkdir %s'%temp_dir)
    for idx in tqdm(range(len(images))):
        PIL.Image.fromarray(images[idx], 'RGB').save('%s/frame%05d.png' % (temp_dir, idx))
    cmd = 'ffmpeg -i %s/frame%%05d.png -c:v libx264 -pix_fmt yuv420p %s/%s.mp4' % (temp_dir, out_dir, out_name)
    print(cmd)
    os.system(cmd)
    os.system('rm -rf %s'%temp_dir)


# In[ ]:



def random_sample(num_images, scale):
    latents = np.random.RandomState(int(1000*random.random())).randn(num_images, *Gs.input_shapes[0][1:])
    labels = np.zeros([latents.shape[0]] + Gs.input_shapes[1][1:])
    images = Gs.run(latents, None, truncation_psi=truncation, randomize_noise=False, output_transform=fmt)
    images_ct = np.concatenate([img for img in images], axis=1)
    plt.figure(figsize=(scale*num_images, scale))
    plt.imshow(images_ct)
    plt.axis('off')
    #plt.savefig('download.png')
    return images, latents

images, latents = random_sample(1, scale=10)
