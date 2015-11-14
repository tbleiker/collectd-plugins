
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
    data.plugin_instance = plugin_instance
    data.type = type_values
    data.type_instance = type_instance
    data.values = values
    data.host = hostname
    data.dispatch()


def reader(input_data=None):
    # get hostname
    hostname = str(socket.getfqdn())
    
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
            
            # cpu - user
            dispatch('lxc_cpu', container, 'user', 'cpu', [cpuUser], hostname)
            # cpu - system
            dispatch('lxc_cpu', container, 'system', 'cpu', [cpuSys], hostname)
            # cpu - total
            dispatch('lxc_cpu', container, 'total', 'cpu', [cpuUser + cpuSys], hostname)
                        
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
            
            # memory - rss
            dispatch('lxc_memory', container, 'rss', 'memory', [memRss], hostname)
            # memory - cache
            dispatch('lxc_memory', container, 'cache', 'memory', [memCache], hostname)
            # memory - swap
            dispatch('lxc_memory', container, 'swap', 'memory', [memSwap], hostname)
            
            
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
            
            # blkio - bytes read
            dispatch('lxc_blkio', container, 'bytes_read', 'total_bytes', [blkioBytesRead], hostname)
            # blkio - bytes write
            dispatch('lxc_blkio', container, 'bytes_write', 'total_bytes', [blkioBytesWrite], hostname)
            # blkio - io read
            dispatch('lxc_blkio', container, 'ops_read', 'total_operations', [blkioIoRead], hostname)
            # blkio - io write
            dispatch('lxc_blkio', container, 'ops_write', 'total_operations', [blkioIoWrite], hostname)
            

collectd.register_config(configure)
collectd.register_init(initialize)
collectd.register_read(reader)
