##
#
# Copyright (C) 2021 Matt Molyneaux
#
# This file is part of Exhibition.
#
# Exhibition is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Exhibition is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Exhibition.  If not, see <https://www.gnu.org/licenses/>.
#
##
"""
A base filter class for class based filters
"""


class BaseFilter:
    """Base filter for class-based filters

    Subclasses must override ``content_filter``, which should return a str.
    """

    def __call__(self, node, content):
        self.node = node
        self.content = content
        return self.content_filter()

    def content_filter(self):
        """Override this method in your subclass"""
        raise NotImplementedError


content_filter = BaseFilter()  # this line is here for completeness sake
