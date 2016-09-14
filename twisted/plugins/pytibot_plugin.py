# PyTIBot - IRC Bot using python and the twisted library
# Copyright (C) <2016>  <Sebastian Schmidt>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from zope.interface import implementer

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker, MultiService
from twisted.application import internet

from configmanager import ConfigManager

from pytibotfactory import PyTIBotFactory
from twisted.conch import manhole_tap


mandatory_settings = [("Connection", "server"), ("Connection", "port"),
                      ("Connection", "nickname"), ("Connection", "admins")]


class Options(usage.Options):
    optParameters = [["config", "c", "pytibot.ini", "The config file to use"]]


@implementer(IServiceMaker, IPlugin)
class PyTIBotServiceMaker(object):
    tapname = "PyTIBot"
    description = "IRC Bot"
    options = Options

    def makeService(self, options):
        """
        Create an instance of PyTIBot
        """
        cm = ConfigManager(options["config"], delimiters=("="))
        if not all([cm.option_set(sec, opt) for sec, opt in mandatory_settings]):
            raise EnvironmentError("Reading config file failed, mandatory"
                                   " fields not set!\nPlease reconfigure")

        mService = MultiService()

        # irc client
        ircserver = cm.get("Connection", "server")
        ircport = cm.getint("Connection", "port")
        ircbotfactory = PyTIBotFactory(cm)
        irc_cl = internet.TCPClient(ircserver, ircport, ircbotfactory)
        irc_cl.setServiceParent(mService)

        # manhole for debugging
        open_manhole = False
        if cm.option_set("Connection", "open_manhole"):
            open_manhole = cm.getboolean("Connection", "open_manhole")

        if open_manhole:
            if cm.option_set("Manhole", "telnetPort"):
                telnetPort = cm.get("Manhole", "telnetPort")
            else:
                telnetPort = None
            if cm.option_set("Manhole", "sshPort"):
                sshPort = cm.get("Manhole", "sshPort")
            else:
                sshPort = None
            options = {'namespace': {'get_bot': ircbotfactory.get_bot},
                       'passwd': 'manhole_cred',
                       'sshPort': sshPort,
                       'telnetPort': telnetPort}
            tn_sv = manhole_tap.makeService(options)
            tn_sv.setServiceParent(mService)

        return mService


serviceMaker = PyTIBotServiceMaker()