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

import hashlib
import pickle
import os


class ParseCache:
    """
    Cache for parsed file results to avoid re-parsing unchanged files.
    Uses content hash to detect file changes.
    """

    def __init__(self, cache_file=None):
        self._cache_file = cache_file
        self._cache = {}
        self._load()

    def _load(self):
        """Load cache from disk if available."""
        if self._cache_file and os.path.exists(self._cache_file):
            try:
                with open(self._cache_file, 'rb') as f:
                    self._cache = pickle.load(f)
            except Exception:
                self._cache = {}

    def save(self):
        """Save cache to disk."""
        if self._cache_file:
            try:
                os.makedirs(os.path.dirname(self._cache_file), exist_ok=True)
                with open(self._cache_file, 'wb') as f:
                    pickle.dump(self._cache, f, pickle.HIGHEST_PROTOCOL)
            except Exception:
                pass

    def get_content_hash(self, content):
        """Calculate hash of file content."""
        if isinstance(content, list):
            content = '\n'.join(content)
        return hashlib.sha1(content.encode('utf-8', errors='replace')).hexdigest()

    def get_cached(self, filename, content):
        """
        Returns cached data if content hash matches, else None.

        :param filename: The file path used as cache key
        :param content: The file content (list of lines or string)
        :return: Cached parse data if valid, None otherwise
        """
        content_hash = self.get_content_hash(content)
        if filename in self._cache:
            cached_hash, cached_data = self._cache[filename]
            if cached_hash == content_hash:
                return cached_data
        return None

    def store(self, filename, content, data):
        """
        Store parse result with content hash.

        :param filename: The file path used as cache key
        :param content: The file content (list of lines or string)
        :param data: The parse result data to cache
        """
        content_hash = self.get_content_hash(content)
        self._cache[filename] = (content_hash, data)

    def clear(self):
        """Clear all cached data."""
        self._cache = {}
