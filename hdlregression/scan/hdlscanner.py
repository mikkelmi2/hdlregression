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

from abc import abstractmethod

from ..construct.container import Container
from ..report.logger import Logger


class HDLScanner:
    """
    Base scanner class
    """

    def __init__(self, project, library, filename, hdlfile):
        self.logger = Logger(name=__name__, project=project)
        self.testcase_string = project.settings.get_testcase_identifier_name()
        self.container = Container()
        self.library = library
        self.filename = filename
        self.hdlfile = hdlfile

        # Lists
        self.library_list = []
        self.int_use_list = []
        self.testcase_list = []

        # Assertion
        self.assertion_list = {"note": 0, "warning": 0, "error": 0, "failure": 0}
        self.assertion_count = 0

    def get_library(self) -> str:
        return self.library

    def scan(self, file_content):
        file_content = self._clean_code(file_content)
        self.tokenize(file_content)

    def set_filename(self, filename):
        self.filename = filename

    def get_filename(self) -> str:
        return self.filename

    def add_library_dep(self, library):
        if not (library.lower() in self.library_list):
            self.library_list.append(library.lower())

    def get_library_dep(self) -> list:
        """
        Returns the library list and empties the stored list.
        """
        library_list_copy = [item for item in self.library_list]
        self.library_list = []
        return library_list_copy

    def add_int_dep(self, use_dep):
        if not (use_dep.lower() in self.int_use_list):
            self.int_use_list.append(use_dep.lower())

    def get_int_dep(self) -> list:
        """
        Returns the internal use list and empties the stored list.
        """
        list_copy = [item for item in self.int_use_list]
        self.int_use_list = []
        return list_copy

    def add_testcase(self, testcase):
        if testcase not in self.testcase_list:
            self.testcase_list.append(testcase)

    def get_testcase(self) -> list:
        return self.testcase_list

    def add_module_to_container(self, module):
        module.set_hdlfile(self.hdlfile)
        self.container.add(module)

    def get_module_container(self) -> "Container":
        return self.container

    def increment_assertion_count(self) -> None:
        self.assertion_count += 1

    def get_assertion_count(self) -> int:
        return self.assertion_count

    def export_state(self) -> dict:
        """
        Export scanner state as serializable dict (no object references).
        This allows caching parse results without pickling complex objects.
        """
        modules_data = []
        for module in self.container.get():
            module_data = {
                'name': module.get_name(),
                'type': module.get_type(),
                'is_tb': module.get_is_tb(),
                'int_dep_list': module.get_int_dep().copy(),
                'ext_dep_list': module.get_ext_dep().copy(),
                'filename': module.get_filename(),
            }
            # Add type-specific data
            if module.get_is_architecture():
                module_data['arch_of'] = module.get_arch_of()
                module_data['testcase_list'] = module.get_testcase().copy()
            elif module.get_is_entity():
                module_data['generic_list'] = module.get_generic().copy()
                module_data['arch_list'] = module.get_architecture().copy()
            elif module.get_is_verilog_module():
                module_data['parameter_list'] = module.get_parameter().copy()
                module_data['testcase_list'] = module.get_testcase().copy()
            modules_data.append(module_data)

        return {
            'modules': modules_data,
            'library_list': self.library_list.copy(),
            'int_use_list': self.int_use_list.copy(),
            'testcase_list': self.testcase_list.copy(),
            'assertion_list': self.assertion_list.copy(),
            'assertion_count': self.assertion_count,
        }

    def import_state(self, data: dict):
        """
        Restore scanner state from cached dict.
        Implemented in VHDLScanner/VerilogScanner to create correct module types.
        """
        pass

    @abstractmethod
    def _clean_code(self, file_content_list) -> list:
        pass

    @abstractmethod
    def tokenize(self, file_content_list):
        pass
