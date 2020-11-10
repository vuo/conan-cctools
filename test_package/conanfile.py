from conans import ConanFile

class CctoolsTestConan(ConanFile):
    requires = 'llvm/5.0.2-1@vuo/stable'

    def imports(self):
        self.copy('*', dst='bin', src='bin')

    def test(self):
        self.run('bin/codesign_allocate -i bin/codesign_allocate -r -o codesign_allocate2')
        self.run('ls -l bin/codesign_allocate codesign_allocate2')
        self.run('file codesign_allocate2')
        self.run('./codesign_allocate2 -i codesign_allocate2 -r -o codesign_allocate3')
        self.run('ls -l codesign_allocate3')
        self.run('file codesign_allocate3')

        self.run('bin/lipo -info bin/lipo')

        self.run('bin/install_name_tool -add_rpath test codesign_allocate3')
