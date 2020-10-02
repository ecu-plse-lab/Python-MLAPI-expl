#!/usr/bin/env python
# coding: utf-8

# Kaggle Kernels now provides 5GB worth of output files, increased from 1GB!
# 
# For instance:

# In[ ]:


import os

_FILENAME = "some-output-file"
_ONE_GB = 10**9

_gb_count = 5

with open(_FILENAME, "wb") as f:
    for _ in range(_gb_count):
        f.write(bytearray(_ONE_GB))

print("Resulting file size is %.2fGB" % (os.stat(_FILENAME).st_size / _ONE_GB))


# The actual limit is a bit more than 5GB (we are being extra generous!).  Writing more than that limit gives you the usual `No space left on device` error though:

# In[ ]:


import errno

_gb_count = 6

try:
    with open(_FILENAME, "wb") as f:
        for _ in range(_gb_count):
           f.write(bytearray(_ONE_GB))
except OSError as e:
    if e.errno != errno.ENOSPC:
        raise
    print("Exception: %s" % e)

print("Resulting file size is %.2fGB" % (os.stat(_FILENAME).st_size / _ONE_GB))


# For those of you interested in more details:  Under the covers, the block device created for you is actually 5GiB ([gigibytes](https://en.wikipedia.org/wiki/Gibibyte)).  However, the filesystem overhead means you're getting a bit less than that:

# In[ ]:


_ONE_MIB = 2**20
_ONE_GIB = _ONE_MIB * 2**10
_FILESYSTEM_OVERHEAD = 0.96  # Estimated

_mib_count = int(5 * 2**10 * _FILESYSTEM_OVERHEAD)

with open(_FILENAME, "wb") as f:
    for _ in range(_mib_count):
        f.write(bytearray(_ONE_MIB))

print("Resulting file size is %.2fGiB" % (os.stat(_FILENAME).st_size / _ONE_GIB))


# The full 5GiB is indeed not provided:

# In[ ]:


_mib_count = 5 * 2**10

try:
    with open(_FILENAME, "wb") as f:
        for _ in range(_mib_count):
            f.write(bytearray(_ONE_MIB))
except OSError as e:
    if e.errno != errno.ENOSPC:
        raise
    print("Exception: %s" % e)

print("Resulting file size is %.2fGiB" % (os.stat(_FILENAME).st_size / _ONE_GIB))


# Note that the HTML generated by `Commit & Run` is included in the final output.
# So, before we leave here, let's make sure we're leaving some space for that.  In this case, that extra .2GB will do:

# In[ ]:


_gb_count = 5

with open(_FILENAME, "wb") as f:
    for _ in range(_gb_count):
        f.write(bytearray(_ONE_GB))

print("Resulting file size is %.2fGB" % (os.stat(_FILENAME).st_size / _ONE_GB))


# In[ ]:



