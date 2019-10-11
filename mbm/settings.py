import os

SHARED_DIR = os.path.dirname(os.path.realpath(__file__))+"/../../"
DOCKERFILES_LOCATION = SHARED_DIR + "/openfluid-devtools/docker/Dockerfiles/"
OUTPUT_DIR = "_out/"

# Where docker images will be stored. Depends on the machine, may be in /var/lib/docker
TARGET_VOLUME = "/"
MAX_IMAGE_SIZE = 5000000
# ~ 5G # observed max size for built docker images. Should never be underestimated
