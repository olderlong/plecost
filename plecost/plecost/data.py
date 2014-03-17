#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This file contains data structures of Plecost.
"""

__license__ = """
Copyright (c) 2014:

    Francisco Jesus Gomez aka ffranz | @ffranz - ffranz-[at]-iniqua.com
    Daniel Garcia aka cr0hn | @ggdaniel - cr0hn-[at]-cr0hn.com

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or
promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from sys import stdout
from abc import ABCMeta
from os.path import exists, join
from datetime import datetime

from .utils import get_data_folder
from .wordlist import list_wordlists
from .exceptions import PlecostWordListNotFound


#--------------------------------------------------------------------------
# API caller structure
#--------------------------------------------------------------------------
class PlecostOptions(object):
    """Plecost runner options"""

    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
        """
        :param proxy: Proxy as format: {HOST:PORT}. Default None.
        :type proxy: dict()
        
        :param target: URL target.
        :type target: str

        :param concurrency: maximum number of simultaneous connections. Default 4.
        :type concurrency: int
        
        :param log_function: function to call for display log info. Function format: FUNC(Message::str, Level::int)
        :type log_function: function(str, int)
        
        :param verbosity: verbosity level
        :type verbosity: int
        
        :param report_filename: report filename 
        :type report_filename: str

        :param colorize: Colorize output
        :type colorize: bool

        :param wordlist: Word list path (or embedded) selected find plugins in target.
        :type wordlist: str
        """
        self.__proxy = kwargs.get("proxy", {})
        self.__target = kwargs.get("target", None)
        self.__verbosity = kwargs.get("verbosity", 0)
        self.__concurrency = kwargs.get("concurrency", 4)
        self.__report_filename = kwargs.get("report", None)
        self.__log_function = kwargs.get("log_function", stdout.write)
        self.__colorize = kwargs.get("colorize", True)
        self.__wordlist = kwargs.get("wordlist", None)

        # Check types and default values
        if not isinstance(self.__target, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(self.__target))
        if not isinstance(self.__concurrency, int):
            raise TypeError("Expected int, got '%s' instead" % type(self.__concurrency))
        if self.__log_function is None:
            raise TypeError("Expected function, got '%s' instead" % type(self.__log_function))
        if not isinstance(self.__verbosity, int):
            raise TypeError("Expected int, got '%s' instead" % type(self.__verbosity))

        # Fix target:
        if not self.__target.startswith("http"):
            self.__target = "http://%s" % self.__target

        # Check word list and fix word list path
        if self.__wordlist in list_wordlists():
            self.__wordlist = join(get_data_folder(), self.__wordlist)
        else:
            if self.__wordlist is None:
                self.__wordlist = join(get_data_folder(), "plugin_list_200.txt")
            elif not exists(self.__wordlist):
                raise PlecostWordListNotFound("Word list not found")

    #----------------------------------------------------------------------
    @property
    def target(self):
        """
        :return: Target
        :rtype: basestring
        """
        return self.__target
    
    #----------------------------------------------------------------------
    @property
    def proxy(self):
        """
        :return: Proxy as format {HOST:PORT}
        :rtype: dict
        """
        return self.__proxy 
    
    #----------------------------------------------------------------------
    @property
    def concurrency(self):
        """
        :return: Maximum number of concurrent connections.
        :rtype: int
        """
        return self.__concurrency

    #----------------------------------------------------------------------
    @property
    def log_function(self):
        """
        :return: function to call for display log info. Function format: FUNC(Message::str, Level::int)
        :rtype: function(str, int)
        """
        return self.__log_function

    #----------------------------------------------------------------------
    @property
    def verbosity(self):
        """
        :return: verbosity level.
        :rtype: int
        """
        return self.__verbosity
    
    #----------------------------------------------------------------------
    @property
    def report_filename(self):
        """
        :return: Report filename
        :rtype: basestring
        """
        return self.__report_filename
    
    #----------------------------------------------------------------------
    @property
    def colorize(self):
        """
        :return: 
        :rtype: 
        """
        return self.__colorize
    
    #----------------------------------------------------------------------
    @property
    def wordlist(self):
        """
        :return: path or name (if embedded) wordlist.
        :rtype: basestring
        """
        return self.__wordlist


#--------------------------------------------------------------------------
# Results data structures
#--------------------------------------------------------------------------
class _PlecostBase(object):
    """Abstract class for all Plecost types"""
    __metaclass__ = ABCMeta

    #----------------------------------------------------------------------
    def __init__(self, ver1, ver2):
        """
        :param ver1: current version of software to compare to.
        :type ver1: basestring
        
        :param ver2: latest version of software to compare to.
        :type ver2: basestring
        """
        if ver1 is None or ver1 is None:
            self._outdated = False
        else:
            if not isinstance(ver1, basestring):
                raise TypeError("Expected basestring, got '%s' instead" % type(ver1))
            if not isinstance(ver2, basestring):
                raise TypeError("Expected basestring, got '%s' instead" % type(ver2))

            # Is outdated?
            if self.__version_cmp(ver1, ver2) == -1:
                self._outdated = True
            else:
                self._outdated = False

    #----------------------------------------------------------------------
    def __version_cmp(self, version1, version2):
        """
        Compare two software versions.

        :param version1: string with version number.
        :type version1: str

        :param version2: string with version number.
        :type version2: str

        :return: 1 if version 1 is greater. -1 if version2 if greater.
        :rtype: int
        """
        tup = lambda x: [int(y) for y in (x+'.0.0.0.0').split('.')][:4]

        if version1.lower() == "trunk":
            return 1
        elif version2.lower() == "trunk":
            return -1
        else:
            return cmp(tup(version1), tup(version2))


    #----------------------------------------------------------------------
    @property
    def is_outdated(self):
        """
        :return: True if that software is outdated. None if unknown.
        :rtype: bool|None.
        """
        return self._outdated


#----------------------------------------------------------------------
class PlecostWordPressInfo(_PlecostBase):
    """WordPress installation information"""

    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
        """
        :param current_version: Current version number as format: x.x.x.
        :type current_version: str

        :param last_version: Last version availble as format: x.x.x
        :type last_version: str
        """
        self.__current_version = kwargs.get("current_version", None)
        self.__last_version_available = kwargs.get("last_version", None)

        if not isinstance(self.__current_version, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(self.__current_version))
        if not isinstance(self.__last_version_available, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(self.__last_version_available))

        super(PlecostWordPressInfo, self).__init__(self.__current_version, self.__last_version_available)

    #----------------------------------------------------------------------
    @property
    def latest_version(self):
        """
        :return: Last version of WordPress available as format: x.x.x
        :rtype: basestring
        """
        return self.__last_version_available
    
    #----------------------------------------------------------------------
    @property
    def current_version(self):
        """
        :return: Current version installed in target as format: x.x.x
        :rtype: basestring
        """
        return self.__current_version


#--------------------------------------------------------------------------
class PlecostPluginInfo(_PlecostBase):
    """Plugin information in remote host"""

    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
        """
        :param current_version: Current version number as format: x.x.x.
        :type current_version: str

        :param last_version: Last version available as format: x.x.x
        :type last_version: str
        
        :param plugin_name: Plugin long name description. 
        :type plugin_name: basestring
        
        :param plugin_uri: Plugin URI 
        :type plugin_uri: basestring
        
        :param cves: list with CVEs related 
        :type cves: list(str)
        
        :param exploits: list with url to related exploits.
        :type exploits: list(str)
        """
        self.__plugin_name = kwargs.get("plugin_name", None)
        self.__plugin_uri = kwargs.get("plugin_uri", None)
        self.__current_version = kwargs.get("current_version", None)
        self.__last_version = kwargs.get("last_version", None)
        self.__cves = kwargs.get("cves", [])
        self.__exploits = kwargs.get("exploits", [])

        if not isinstance(self.__plugin_uri, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(self.__plugin_uri))

        super(PlecostPluginInfo, self).__init__(self.__current_version, self.__last_version)

    #----------------------------------------------------------------------
    @property
    def plugin_name(self):
        """
        :return: Plugin name.
        :rtype: basestring
        """
        return self.__plugin_name if self.__plugin_name else self.__plugin_uri

    #----------------------------------------------------------------------
    @property
    def plugin_uri(self):
        """
        :return: Plugin URI
        :rtype: basestring
        """
        return self.__plugin_uri   
    
    #----------------------------------------------------------------------
    @property
    def current_version(self):
        """
        :return: current version installed as format: x.x.x
        :rtype: basestring|None
        """
        return self.__current_version

    #----------------------------------------------------------------------
    @property
    def latest_version(self):
        """
        :return: Latest version installed, if available, as format: x.x.x.
        :rtype: basestring|None
        """
        return self.__last_version
    
    #----------------------------------------------------------------------
    @property
    def cves(self):
        """
        :return: CVEs associated to this plugin.
        :rtype: list(str)
        """
        return self.__cves
    
    #----------------------------------------------------------------------
    @property
    def exploits(self):
        """
        :return: Exploits available for this plugin
        :rtype: list(str)
        """
        return self.__exploits


#--------------------------------------------------------------------------
class PlecostResults(object):
    """Plecost results"""

    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
        """
        :param target: tested target
        :type target: basestring

        :param start_time: start time of testing
        :type start_time: datetime

        :param end_time: end time of testing
        :type end_time: datetime

        :param wordpress_info: remote wordpress information. 
        :type wordpress_info: `PlecostWordPressInfo`
        
        :param plugins: plugins available in remote target.
        :type plugins: `list(PlecostPluginInfo)
        """
        self.__target = kwargs.get("target", None)
        self.__start_time = kwargs.get("start_time", datetime.now())
        self.__end_time = kwargs.get("end_time", datetime.now())
        self.__wordpress_info = kwargs.get("wordpress_info", None)
        self.__plugins = kwargs.get("plugins", None)

        if not isinstance(self.__target, basestring):
            raise TypeError("Expected basestring, got '%s' instead" % type(self.__target))
        if not isinstance(self.__wordpress_info, PlecostWordPressInfo):
            raise TypeError("Expected PlecostWordPressInfo, got '%s' instead" % type(self.__wordpress_info))
        if not isinstance(self.__plugins, list):
            raise TypeError("Expected list, got '%s' instead" % type(self.__plugins))
        else:
            for plugin in self.__plugins:
                if not isinstance(plugin, PlecostPluginInfo):
                    raise TypeError("Expected PlecostPluginInfo, got '%s' instead" % type(plugin))

        # Filter outdated plugins
        self.__outdated_plugins = []
        for plugin in self.__plugins:
            if plugin.is_outdated is True:
                self.__outdated_plugins.append(plugin)

    #----------------------------------------------------------------------
    # Properties
    #----------------------------------------------------------------------
    @property
    def target(self):
        """
        :return: tested target
        :rtype: basestring
        """
        return self.__target

    #----------------------------------------------------------------------
    @property
    def wordpress_info(self):
        """
        :return: WordPress information object
        :rtype: `PlecostWordPressInfo`
        """
        return self.__wordpress_info
        
    #----------------------------------------------------------------------
    @property
    def plugins(self):
        """
        :return: installed plugins found in target.
        :rtype: `list(PlecostPluginInfo)`
        """
        return self.__plugins

    #----------------------------------------------------------------------
    @property
    def start_time(self):
        """
        :return: start time of testing
        :rtype: datetime
        """
        return self.__start_time

    #----------------------------------------------------------------------
    @property
    def end_time(self):
        """
        :return: end time of testing
        :rtype: datetime
        """
        return self.__end_time

    #----------------------------------------------------------------------
    @property
    def outdated_plugins(self):
        """
        :return: Only outdated plugins
        :rtype: `list(PlecostPluginInfo)`
        """
        return self.__outdated_plugins


__all__ = [x for x in dir() if x.startswith("Plecost")]