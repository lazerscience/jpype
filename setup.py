import os
import sys
import platform

from distutils.core import setup as distSetup
from distutils.core import Extension


class JPypeSetup(object):
    def __init__(self):
        self.extra_compile_args = []
        self.macros = []

    def setupFiles(self):
        cpp_files = [
                 map(lambda x: "src/native/common/" + x,
                     os.listdir("src/native/common")),
                 map(lambda x: "src/native/python/" + x,
                     os.listdir("src/native/python")),
                 ]

        all_src = []
        for i in cpp_files:
            all_src += i

        self.cpp = filter(lambda x: x[-4:] == '.cpp', all_src)
        self.objc = filter(lambda x: x[-2:] == '.m', all_src)

    def setupWindows(self):
        print 'Choosing the Windows profile'
        self.javaHome = os.getenv("JAVA_HOME")
        if self.javaHome is None:
            print "environment variable JAVA_HOME must be set"
            sys.exit(-1)
        self.jdkInclude = "win32"
        self.libraries = ["Advapi32"]
        self.libraryDir = [self.javaHome + "/lib"]
        self.macros = [("WIN32", 1)]
        self.extra_compile_args = ['/EHsc']

    def setupMacOSX(self):
        # Changes according to:
        # http://stackoverflow.com/questions/8525193/cannot-install-jpype-on-os-x-lion-to-use-with-neo4j
        # and
        # http://blog.y3xz.com/post/5037243230/installing-jpype-on-mac-os-x
        osx = platform.mac_ver()[0][:4]
        javaHome = '/Library/Java/Home'
        if osx == '10.6':
            # I'm not sure if this really works on all 10.6 - confirm please
            # :)
            javaHome = ('/Developer/SDKs/MacOSX10.6.sdk/System/Library/'
                        'Frameworks/JavaVM.framework/Versions/1.6.0/')
        elif osx == '10.7':
            javaHome = ('/System/Library/Frameworks/JavaVM.framework/'
                        'Versions/Current/')
        self.javaHome = javaHome
        self.jdkInclude = ""
        self.libraries = ["dl"]
        self.libraryDir = [self.javaHome + "/Libraries"]
        self.macros = [('MACOSX', 1)]

    def setupLinux(self):
        self.javaHome = os.getenv("JAVA_HOME")
        if self.javaHome is None:
            possibleHomes = ['/usr/lib/jvm/default-java',
                             '/usr/lib/jvm/java-1.5.0-gcj-4.4',
                             '/usr/lib/jvm/jdk1.6.0_30',
                             '/usr/lib/jvm/java-1.5.0-sun-1.5.0.08',
                             '/usr/java/jdk1.5.0_05']
            for home in possibleHomes:
                if os.path.exists(home):
                    self.javaHome = home
                    break
        self.jdkInclude = "linux"
        self.libraries = ["dl"]
        self.libraryDir = [self.javaHome + "/lib"]

    def setupPlatform(self):
        if sys.platform == 'win32':
            self.setupWindows()
        elif sys.platform == 'darwin':
            self.setupMacOSX()
        else:
            self.setupLinux()

    def setupInclusion(self):
        platformdirs = [self.javaHome + "/include",
                        self.javaHome + "/include/" + self.jdkInclude, ]
        if sys.platform == 'darwin':
            platformdirs = [self.javaHome + "/Headers",
                            self.javaHome + "/Headers/" + self.jdkInclude, ]
        self.includeDirs = ["src/native/common/include",
                            "src/native/python/include", ]
        self.includeDirs.extend(platformdirs)

    def setup(self):
        self.setupFiles()
        self.setupPlatform()
        self.setupInclusion()

        jpypeLib = Extension("_jpype",
                             self.cpp,
                             libraries=self.libraries,
                             define_macros=self.macros,
                             include_dirs=self.includeDirs,
                             library_dirs=self.libraryDir,
                             extra_compile_args=self.extra_compile_args
                             )

        distSetup(
            name="JPype",
            version="0.5.4.2",
            description="Python-Java bridge",
            author="Steve Menard",
            author_email="devilwolf@users.sourceforge.net",
            url="http://jpype.sourceforge.net/",
            packages=[
                "jpype", 'jpype.awt', 'jpype.awt.event',
                'jpypex', 'jpypex.swing'],
            package_dir={
                "jpype": "src/python/jpype",
                'jpypex': 'src/python/jpypex',
            },

            ext_modules=[jpypeLib]
        )

JPypeSetup().setup()
