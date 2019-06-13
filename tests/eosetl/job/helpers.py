# MIT License
#
# Copyright (c) 2018 Omidiora Samuel, samparsky@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os

from eosetl.rpc.eos_rpc import EosRpc
from tests.eosetl.job.mock_eos_rpc import MockEosRpc


def get_eos_rpc(provider_type, read_resource_lambda=None, chain='bitcoin'):
    if provider_type == "mock":
        if read_resource_lambda is None:
            raise ValueError('read_resource_lambda must not be None for provider type {}'.format(provider_type))
        rpc = MockEosRpc(read_resource_lambda)

    elif provider_type == "online":

        env_variable_name = "eosetl_{}_PROVIDER_URI".format(chain.upper())
        provider_uri = os.environ.get(env_variable_name)
        if provider_uri is None or len(provider_uri) == 0:
            raise ValueError('{} is required environment variable'.format(env_variable_name))

        rpc = EosRpc(provider_uri)
    return rpc