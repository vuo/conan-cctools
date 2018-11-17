from conans import ConanFile, tools
import shutil

class CctoolsConan(ConanFile):
    name = 'cctools'

    cctools_version = '921'
    package_version = '1'
    version = '%s-%s' % (cctools_version, package_version)

    build_requires = 'llvm/3.3-5@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://opensource.apple.com/'
    license = 'https://opensource.apple.com/source/cctools/cctools-%s/APPLE_LICENSE.auto.html' % cctools_version
    description = 'Various Mach utilities'
    source_dir = 'cctools-%s' % cctools_version

    def source(self):
        tools.get('https://opensource.apple.com/tarballs/cctools/cctools-%s.tar.gz' % self.cctools_version,
                  sha256='53449a7f2e316c7df5e6b94fd04e12b6d0356f2487d77aad3000134e4c010cc5')

        # Use MacOSX10.11.sdk's instead.
        self.run('rm -Rf %s/include/mach/i386' % self.source_dir)

        self.run('mv %s/APPLE_LICENSE %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        with tools.chdir(self.source_dir):
            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
            }
            make_args = '-j9 LTO="" SDK="-isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk"'
            with tools.environment_append(env_vars):
                with tools.chdir('libstuff'):
                    self.run('make %s' % make_args)
                with tools.chdir('misc'):
                    self.run('make codesign_allocate.NEW %s' % make_args)
            shutil.move('misc/codesign_allocate.NEW', 'codesign_allocate')

    def package(self):
        self.copy('codesign_allocate', src=self.source_dir, dst='bin')
        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')
