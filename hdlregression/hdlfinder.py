#
# Copyright (c) 2022 by HDLRegression Authors.  All rights reserved.
# Licensed under the MIT License; you may not use this file except in compliance with the License.
# You may obtain a copy of the License at https://opensource.org/licenses/MIT.
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.
#
# HDLRegression AND ANY PART THEREOF ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH UVVM OR THE USE OR OTHER DEALINGS IN HDLRegression.
#


import os
import glob
from .report.logger import Logger


class HDLFinder(object):
    """
    Class for locating files and creating hdlregression file objects.
    """

    def __init__(self, project, filename=None):
        self.logger = Logger(name=__name__, project=project)
        self.project = project
        self.file_list = []
        self._seen = set()

        if filename:
            if os.path.isdir(filename):
                self.logger.warning("Filename is directory: %s" % filename)
            else:
                self.find_files(filename)

    def find_files(self, filename, recursive=False):
        """
        Find all files matching 'filename' (case-insensitive).
        Adds matched file paths to self.file_list if not already present.
        Supports wildcards in directory segments.
        Uses glob for efficient file matching.
        """
        script_path = (
            self.project.settings.get_script_path()
            if not self.project.settings.get_is_gui_mode()
            else ""
        )

        # Normalize separators to current OS (accept / and \)
        filename = filename.replace("\\", os.sep).replace("/", os.sep)

        search_path = os.path.normpath(os.path.join(script_path, filename))

        # For recursive search, insert ** if not already present
        if recursive and "**" not in search_path:
            dir_part = os.path.dirname(search_path)
            file_part = os.path.basename(search_path)
            search_path = os.path.join(dir_part, "**", file_part)

        # Use glob to find matching files
        try:
            matches = glob.glob(search_path, recursive=recursive)
        except OSError as e:
            self.logger.debug("Glob failed for '{}': {}".format(search_path, e))
            return

        # Filter for files only and deduplicate
        for match in matches:
            if os.path.isfile(match) and match not in self._seen:
                self._seen.add(match)
                self.file_list.append(match)

    def get_file_list(self):
        """
        Return list of all files found.
        """
        return self.file_list
