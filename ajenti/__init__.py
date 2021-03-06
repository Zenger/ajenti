import build
import subprocess
import os
import platform as pyplatform
import random
import signal


# Global state

config = None
""" Loaded config, is a `reconfigure.items.ajenti.AjentiData` """

version = None
""" Ajenti version """

platform = None
""" Current platform """

platform_unmapped = None
""" Current platform without "Ubuntu is Debian"-like mapping """

platform_string = None
""" Human-friendly platform name """

installation_uid = None
""" Unique installation ID """

server = None
""" Web server """

debug = False
""" Debug mode """


__all__ = ['config', 'platform', 'platform_string', 'platform_unmapped', 'installation_uid', 'version', 'server', 'debug', 'init', 'exit', 'restart']


def detect_version():
    p = subprocess.Popen('git describe --tags 2> /dev/null',
            shell=True,
            stdout=subprocess.PIPE)
    if p.wait() != 0:
        return build.version
    return p.stdout.read().strip('\n ')


def detect_platform():
    base_mapping = {
        'gentoo base system': 'gentoo',
        'centos linux': 'centos',
        'mandriva linux': 'mandriva',
        'elementary os': 'ubuntu',
        'trisquel': 'ubuntu',
        'linuxmint': 'ubuntu',
        'redhat enterprise linux': 'rhel',
        'red hat enterprise linux server': 'rhel',
    }

    platform_mapping = {
        'ubuntu': 'debian',
        'rhel': 'centos',
    }

    if pyplatform.system() != 'Linux':
        res = pyplatform.system().lower()
        return res, res

    dist = ''
    (maj, min, patch) = pyplatform.python_version_tuple()
    if (maj * 10 + min) >= 26:
        dist = pyplatform.linux_distribution()[0]
    else:
        dist = pyplatform.dist()[0]

    if dist == '':
        try:
            dist = subprocess.check_output(['strings', '-4', '/etc/issue']).split()[0]
        except:
            dist = 'unknown'

    res = dist.strip(' \'"\t\n\r').lower()
    if res in base_mapping:
        res = base_mapping[res]

    res_mapped = res
    if res in platform_mapping:
        res_mapped = platform_mapping[res]
    return res, res_mapped


def detect_platform_string():
    try:
        return subprocess.check_output(['lsb_release',  '-sd'])
    except:
        return subprocess.check_output(['uname', '-mrs'])


def check_uid():
    file = '/var/lib/ajenti/installation-uid'
    if not os.path.exists(file):
        uid = str(random.randint(1, 9000 * 9000))
        try:
            open(file, 'w').write(uid)
        except:
            uid = '0'
    else:
        uid = open(file).read()
    return uid


def init():
    import ajenti
    ajenti.version = detect_version()
    ajenti.platform_unmapped, ajenti.platform = detect_platform()
    ajenti.platform_string = detect_platform_string()
    ajenti.installation_uid = check_uid()


def exit():
    os.kill(os.getpid(), signal.SIGQUIT)


def restart():
    server.restart_marker = True
    server.stop()
