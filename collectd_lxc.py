
import collectd
import sys
import lxc
import os
import re
import socket


def configure(ObjConfiguration):
    collectd.debug('Configuring lxc collectd.')


def initialize():
    collectd.debug('Initializing lxc collectd.')


def dispatch(plugin, plugin_instance, type_instance, type_values, values, hostname):
    data = collectd.Values()
    data.plugin = plugin
    if plugin_instance is not None:
        data.plugin_instance = plugin_instance
    data.type = type_values
    data.type_instance = type_instance
    data.values = values
    data.host = hostname
    data.dispatch()


def reader(input_data=None):
    # get hostname
    hostname = str(socket.getfqdn())
    
    # total values
    total_cpuUser = 0
    total_cpuSys = 0
    total_memRss = 0
    total_memCache = 0
    total_memSwap = 0
    total_blkioBytesRead = 0
    total_blkioBytesWrite = 0
    total_blkioIoRead = 0
    total_blkioIoWrite = 0
     
    # iterate over all containers
    for container in lxc.list_containers():
        c = lxc.Container(container)
        
        # get values if the container is running
        if c.running:
            
            ## CPU
            cpu = c.get_cgroup_item('cpuacct.stat')
            try:
                cpuUser = int(re.search('user\s(?P<user>[0-9]+)', cpu).group('user'))
                cpuSys = int(re.search('system\s(?P<sys>[0-9]+)', cpu).group('sys'))
            except AttributeError:
                cpuUser = 0
                cpuSys = 0
            
            # dispatch values
            dispatch('lxc_cpu', container, 'user', 'cpu', [cpuUser], hostname)
            dispatch('lxc_cpu', container, 'system', 'cpu', [cpuSys], hostname)
            dispatch('lxc_cpu', container, 'total', 'cpu', [cpuUser + cpuSys], hostname)
            
            # sum values up for a total
            total_cpuUser = total_cpuUser + cpuUser
            total_cpuSys = total_cpuSys + cpuSys
            
            ## Memrory
            mem = c.get_cgroup_item('memory.stat')
            try:
                memRss = int(re.search('rss\s(?P<rss>[0-9]+)', mem).group('rss'))
                memCache = int(re.search('cache\s(?P<cache>[0-9]+)', mem).group('cache'))
                memSwap = int(re.search('swap\s(?P<swap>[0-9]+)', mem).group('swap'))
            except AttributeError:
                memRss = 0
                memCache = 0
                memSwap = 0
            
            # dispatch values
            dispatch('lxc_memory', container, 'rss', 'memory', [memRss], hostname)
            dispatch('lxc_memory', container, 'cache', 'memory', [memCache], hostname)
            dispatch('lxc_memory', container, 'swap', 'memory', [memSwap], hostname)
            
            # sum values up for a total
            total_memRss = total_memRss + memRss
            total_memCache = total_memCache + memCache
            total_memSwap = total_memSwap + memSwap
            
            
            ## Disk
            blkioBytes = c.get_cgroup_item('blkio.throttle.io_service_bytes')
            blkioIo = c.get_cgroup_item('blkio.throttle.io_serviced')
            try:
                blkioBytesRead = int(re.search("Read\s+(?P<read>[0-9]+)", blkioBytes).group('read'))
                blkioBytesWrite = int(re.search("Write\s+(?P<write>[0-9]+)", blkioBytes).group('write'))
                blkioIoRead = int(re.search("Read\s+(?P<read>[0-9]+)", blkioIo).group('read'))
                blkioIoWrite = int(re.search("Write\s+(?P<write>[0-9]+)", blkioIo).group('write'))
            except AttributeError:
                blkioBytesRead = 0
                blkioBytesWrite = 0
                blkioIoRead = 0
                blkioIoWrite = 0
            
            # dispatch values
            dispatch('lxc_blkio', container, 'bytes_read', 'total_bytes', [blkioBytesRead], hostname)
            dispatch('lxc_blkio', container, 'bytes_write', 'total_bytes', [blkioBytesWrite], hostname)
            dispatch('lxc_blkio', container, 'ops_read', 'total_operations', [blkioIoRead], hostname)
            dispatch('lxc_blkio', container, 'ops_write', 'total_operations', [blkioIoWrite], hostname)
            
            # sum values up for a total
            total_blkioBytesRead = total_blkioBytesRead + blkioBytesRead
            total_blkioBytesWrite = total_blkioBytesWrite + blkioBytesWrite
            total_blkioIoRead = total_blkioIoRead + blkioIoRead
            total_blkioIoWrite = total_blkioIoWrite + blkioIoWrite


    # dispatch total values
    dispatch('lxc_total_cpu', None, 'user', 'cpu', [total_cpuUser], hostname)
    dispatch('lxc_total_cpu', None, 'system', 'cpu', [total_cpuSys], hostname)
    dispatch('lxc_total_cpu', None, 'total', 'cpu', [total_cpuUser + total_cpuSys], hostname)
    dispatch('lxc_total_memory', None, 'rss', 'memory', [total_memRss], hostname)
    dispatch('lxc_total_memory', None, 'cache', 'memory', [total_memCache], hostname)
    dispatch('lxc_total_memory', None, 'swap', 'memory', [total_memSwap], hostname)
    dispatch('lxc_total_blkio', None, 'bytes_read', 'total_bytes', [total_blkioBytesRead], hostname)
    dispatch('lxc_total_blkio', None, 'bytes_write', 'total_bytes', [total_blkioBytesWrite], hostname)
    dispatch('lxc_total_blkio', None, 'ops_read', 'total_operations', [total_blkioIoRead], hostname)
    dispatch('lxc_total_blkio', None, 'ops_write', 'total_operations', [total_blkioIoWrite], hostname)


collectd.register_config(configure)
collectd.register_init(initialize)
collectd.register_read(reader)
