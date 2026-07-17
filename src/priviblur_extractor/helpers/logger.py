import logging

LOGGER = logging.getLogger("priviblur-extractor")
LOGGER.addHandler(logging.NullHandler())
LOGGER.propagate = False
