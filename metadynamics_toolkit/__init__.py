"""A toolkit for data analysis of metadynamics"""

# Add imports here
from .metadynamics_toolkit import *

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
