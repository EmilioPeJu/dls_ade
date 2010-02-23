# Author: Diamond Light Source, Copyright 2008
#
# License: This file is part of 'dls.environment'
# 
# 'dls.environment' is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# 'dls.environment' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with 'dls.environment'.  If not, see <http://www.gnu.org/licenses/>.

"""A module containing settings for the dls software environment, a custom
installer for setuptools, and a basic tool for stripping documentation from
module docstrings"""
from env import environment
from install import dls_install
__all__=["environment","dls_install"]
