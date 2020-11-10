from conans import ConanFile, tools
import shutil

class CctoolsConan(ConanFile):
    name = 'cctools'

    cctools_version = '949.0.1'
    package_version = '1'
    version = '%s-%s' % (cctools_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://opensource.apple.com/'
    license = 'https://opensource.apple.com/source/cctools/cctools-%s/APPLE_LICENSE.auto.html' % cctools_version
    description = 'Various Mach utilities'
    source_dir = 'cctools-%s' % cctools_version
    exports_sources = '*.patch'

    install_x86_dir = '_install_x86'
    install_arm_dir = '_install_arm'
    install_universal_dir = '_install_universal'

    def source(self):
        tools.get('https://opensource.apple.com/tarballs/cctools/cctools-%s.tar.gz' % self.cctools_version,
                  sha256='830485ac7c563cd55331f643952caab2f0690dfbd01e92eb432c45098b28a5d0')
        with tools.chdir(self.source_dir):
            tools.patch(patch_file='../cctools-arm.patch')
            tools.replace_in_file('libstuff/writeout.c', '__builtin_available(macOS 10.12, *)', '0')
            tools.replace_in_file('misc/lipo.c',         '__builtin_available(macOS 10.12, *)', '0')

        # Use the Conan-packaged SDK instead.
        self.run('rm -Rf %s/include/mach/i386' % self.source_dir)

        self.run('mv %s/APPLE_LICENSE %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        tools.mkdir(self.install_x86_dir)
        tools.mkdir(self.install_arm_dir)
        with tools.chdir(self.source_dir):
            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
            }


            self.output.info("=== Build cctools for x86_64 ===")
            make_args = '-j9 LTO="" SDK="-isysroot %s -mmacosx-version-min=10.11 -target x86_64-apple-macos10.11.0"' % self.deps_cpp_info['macos-sdk'].rootpath
            with tools.environment_append(env_vars):
                with tools.chdir('libstuff'):
                    self.run('make %s' % make_args)
                with tools.chdir('misc'):
                    self.run('make codesign_allocate.NEW lipo.NEW install_name_tool.NEW %s' % make_args)
            self.run('strip misc/codesign_allocate.NEW')
            self.run('strip misc/lipo.NEW')
            self.run('strip misc/install_name_tool.NEW')
            shutil.move('misc/codesign_allocate.NEW', '../%s/codesign_allocate' % self.install_x86_dir)
            shutil.move('misc/lipo.NEW', '../%s/lipo' % self.install_x86_dir)
            shutil.move('misc/install_name_tool.NEW', '../%s/install_name_tool' % self.install_x86_dir)


            self.output.info("=== Build cctools for arm64 ===")
            make_args = '-j9 LTO="" SDK="-isysroot %s -mmacosx-version-min=10.11 -target arm64-apple-macos10.11.0"' % self.deps_cpp_info['macos-sdk'].rootpath
            make_args += ' RC_CFLAGS="-mmacosx-version-min=10.11 -target arm64-apple-macos10.11.0"'
            with tools.environment_append(env_vars):
                with tools.chdir('libstuff'):
                    self.run('make clean')
                    self.run('make %s' % make_args)
                with tools.chdir('misc'):
                    self.run('make clean')
                    self.run('make codesign_allocate.NEW lipo.NEW install_name_tool.NEW %s' % make_args)
            self.run('strip misc/codesign_allocate.NEW')
            self.run('strip misc/lipo.NEW')
            self.run('strip misc/install_name_tool.NEW')
            shutil.move('misc/codesign_allocate.NEW', '../%s/codesign_allocate' % self.install_arm_dir)
            shutil.move('misc/lipo.NEW', '../%s/lipo' % self.install_arm_dir)
            shutil.move('misc/install_name_tool.NEW', '../%s/install_name_tool' % self.install_arm_dir)


        self.output.info("=== Merge x86_64 + arm64 ===")
        tools.mkdir(self.install_universal_dir)
        with tools.chdir(self.install_universal_dir):
            self.run('lipo -create ../%s/codesign_allocate ../%s/codesign_allocate -output codesign_allocate' % (self.install_x86_dir, self.install_arm_dir))
            self.run('lipo -create ../%s/lipo ../%s/lipo -output lipo' % (self.install_x86_dir, self.install_arm_dir))
            self.run('lipo -create ../%s/install_name_tool ../%s/install_name_tool -output install_name_tool' % (self.install_x86_dir, self.install_arm_dir))


    def package(self):
        self.copy('codesign_allocate', src=self.install_universal_dir, dst='bin')
        self.copy('lipo', src=self.install_universal_dir, dst='bin')
        self.copy('install_name_tool', src=self.install_universal_dir, dst='bin')
        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')
