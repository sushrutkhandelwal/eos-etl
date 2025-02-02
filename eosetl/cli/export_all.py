# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev evge.medvedev@gmail.com
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


import click
import re

from datetime import datetime, timedelta
from eosetl.jobs.export_all import export_all as do_export_all
from eosetl.service.eos_block_range_service import EosBlockRangeService
from eosetl.rpc.eos_rpc import EosRpc
from blockchainetl_common.thread_local_proxy import ThreadLocalProxy


def is_date_range(start, end):
    """Checks for YYYY-MM-DD date format."""
    return bool(re.match('^2[0-9]{3}-[0-9]{2}-[0-9]{2}$', start) and
                re.match('^2[0-9]{3}-[0-9]{2}-[0-9]{2}$', end))


def is_block_range(start, end):
    """Checks for a valid block number."""
    return (start.isdigit() and 0 <= int(start) <= 999999999
            and end.isdigit() and 0 <= int(end) <= 999999999)


def get_partitions(start, end, partition_batch_size, provider_uri):
    """Yield partitions based on input data type."""
    if is_date_range(start, end):
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()

        day = timedelta(days=1)

        eos_service = EosBlockRangeService(
            eos_rpc=ThreadLocalProxy(lambda: EosRpc(provider_uri))
        )

        while start_date <= end_date:
            batch_start_block, batch_end_block = eos_service.get_block_range_for_date(start_date)
            partition_dir = '/date={start_date!s}/'.format(start_date=start_date)
            yield batch_start_block, batch_end_block, partition_dir, start_date
            start_date += day

    elif is_block_range(start, end):
        start_block = int(start)
        end_block = int(end)

        for batch_start_block in range(start_block, end_block + 1, partition_batch_size):
            batch_end_block = batch_start_block + partition_batch_size - 1
            if batch_end_block > end_block:
                batch_end_block = end_block

            padded_batch_start_block = str(batch_start_block).zfill(8)
            padded_batch_end_block = str(batch_end_block).zfill(8)
            partition_dir = '/start_block={padded_batch_start_block}/end_block={padded_batch_end_block}'.format(
                padded_batch_start_block=padded_batch_start_block,
                padded_batch_end_block=padded_batch_end_block,
            )
            yield batch_start_block, batch_end_block, partition_dir

    else:
        raise ValueError('start and end must be either block numbers or ISO dates')


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-s', '--start', required=True, type=str, help='Start block/ISO date')
@click.option('-e', '--end', required=True, type=str, help='End block/ISO date')
@click.option('-b', '--partition-batch-size', default=10000, type=int,
              help='The number of blocks to export in partition.')
@click.option('-p', '--provider-uri', default='http://api.main.alohaeos.com', type=str,
              help='The URI of the remote EOS node')
@click.option('-o', '--output-dir', default='output', type=str, help='Output directory, partitioned in Hive style.')
@click.option('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
@click.option('-B', '--export-batch-size', default=1, type=int, help='The number of requests in JSON RPC batches.')
def export_all(start, end, partition_batch_size, provider_uri, output_dir, max_workers, export_batch_size):
    """Exports all data for a range of blocks."""
    do_export_all(get_partitions(start, end, partition_batch_size, provider_uri),
                  output_dir, provider_uri, max_workers, export_batch_size)
