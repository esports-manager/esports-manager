import logging

from esm.definitions import DEBUG
from esm.core.esm import ESMMobaController


logging.basicConfig(
    filename="esm.log",
    encoding="utf-8",
    format="%(levelname)s %(asctime)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p ",
)
logger = logging.getLogger(__name__)

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.ERROR)


esm = ESMMobaController()
esm.app()
