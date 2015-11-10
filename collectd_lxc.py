
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
                cpuUserVal = int(re.search('user\s(?P<user>[0-9]+)', cpu).group('user'))
                cpuSysVal = int(re.search('system\s(?P<sys>[0-9]+)', cpu).group('sys'))
            except AttributeError:
                cpuUserVal = 0
                cpuSysVal = 0
            
            # cpu - user
            cpuUser = collectd.Values()
            cpuUser.plugin = "lxc_cpu"
            cpuUser.plugin_instance = container
            cpuUser.type_instance = 'user'
            cpuUser.type = 'cpu'
            cpuUser.values = [cpuUserVal]
            cpuUser.host = hostname
            cpuUser.dispatch()
            
            # cpu - system
            cpuSys = collectd.Values()
            cpuSys.plugin = "lxc_cpu"
            cpuSys.plugin_instance = container
            cpuSys.type_instance = 'system'
            cpuSys.type = 'cpu'
            cpuSys.values = [cpuSysVal]
            cpuSys.host = hostname
            cpuSys.dispatch()
            
            # cpu - total
            cpuSys = collectd.Values()
            cpuSys.plugin = "lxc_cpu"
            cpuSys.plugin_instance = container
            cpuSys.type_instance = 'total'
            cpuSys.type = 'cpu'
            cpuSys.values = [cpuUserVal + cpuSysVal]
            cpuSys.host = hostname
            cpuSys.dispatch()
                        
            ## Memrory
            mem = c.get_cgroup_item('memory.stat')
            try:
                memRssVal = int(re.search('rss\s(?P<rss>[0-9]+)', mem).group('rss'))
                memCacheVal = int(re.search('cache\s(?P<cache>[0-9]+)', mem).group('cache'))
                memSwapVal = int(re.search('swap\s(?P<swap>[0-9]+)', mem).group('swap'))
            except AttributeError:
                memRssVal = 0
                memCacheVal = 0
                memSwapVal = 0
            
            # memory - rss
            memRss = collectd.Values()
            memRss.plugin = "lxc_memory"
            memRss.plugin_instance = container
            memRss.type_instance = 'rss'
            memRss.type = 'memory'
            memRss.values = [memRssVal]
            memRss.host = hostname
            memRss.dispatch()
            
            # memory - cache
            memCache = collectd.Values()
            memCache.plugin = "lxc_memory"
            memCache.plugin_instance = container
            memCache.type_instance = 'cache'
            memCache.type = 'memory'
            memCache.values = [memCacheVal]
            memCache.host = hostname
            memCache.dispatch()           
            
            # memory - swap
            memSwap = collectd.Values()
            memSwap.plugin = "lxc_memory"
            memSwap.plugin_instance = container
            memSwap.type_instance = 'swap'
            memSwap.type = 'memory'
            memSwap.values = [memSwapVal]
            memSwap.host = hostname
            memSwap.dispatch()
            
            
            ## Disk
            blkioBytes = c.get_cgroup_item('blkio.throttle.io_service_bytes')
            blkioIo = c.get_cgroup_item('blkio.throttle.io_serviced')
            try:
                blkioBytesReadVal = int(re.search("Read\s+(?P<read>[0-9]+)", blkioBytes).group('read'))
                blkioBytesWriteVal = int(re.search("Write\s+(?P<write>[0-9]+)", blkioBytes).group('write'))
                blkioIoReadVal = int(re.search("Read\s+(?P<read>[0-9]+)", blkioIo).group('read'))
                blkioIoWriteVal = int(re.search("Write\s+(?P<write>[0-9]+)", blkioIo).group('write'))
            except AttributeError:
                blkioBytesReadVal = 0
                blkioBytesWriteVal = 0
                blkioIoReadVal = 0
                blkioIoWriteVal = 0
            
            # blkio - bytes read
            blkioBytesRead = collectd.Values()
            blkioBytesRead.plugin = "lxc_blkio"
            blkioBytesRead.plugin_instance = container
            blkioBytesRead.type_instance = 'bytes_read'
            blkioBytesRead.type = 'total_bytes'
            blkioBytesRead.values = [blkioBytesReadVal]
            blkioBytesRead.host = hostname
            blkioBytesRead.dispatch()
            
            # blkio - bytes write
            blkioBytesWrite = collectd.Values()
            blkioBytesWrite.plugin = "lxc_blkio"
            blkioBytesWrite.plugin_instance = container
            blkioBytesWrite.type_instance = 'bytes_write'
            blkioBytesWrite.type = 'total_bytes'
            blkioBytesWrite.values = [blkioBytesWriteVal]
            blkioBytesWrite.host = hostname
            blkioBytesWrite.dispatch()
            
            # blkio - io read
            blkioIoRead = collectd.Values()
            blkioIoRead.plugin = "lxc_blkio"
            blkioIoRead.plugin_instance = container
            blkioIoRead.type_instance = 'ops_read'
            blkioIoRead.type = 'total_operations'
            blkioIoRead.values = [blkioIoReadVal]
            blkioIoRead.host = hostname
            blkioIoRead.dispatch()
            
            # blkio - io write
            blkioIoWrite = collectd.Values()
            blkioIoWrite.plugin = "lxc_blkio"
            blkioIoWrite.plugin_instance = container
            blkioIoWrite.type_instance = 'ops_write'
            blkioIoWrite.type = 'total_operations'
            blkioIoWrite.values = [blkioIoWriteVal]
            blkioIoWrite.host = hostname
            blkioIoWrite.dispatch()
            

collectd.register_config(configure)
collectd.register_init(initialize)
collectd.register_read(reader)
