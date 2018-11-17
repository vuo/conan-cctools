from conans import ConanFile

class CctoolsTestConan(ConanFile):
    requires = 'llvm/3.3-5@vuo/stable'
    generators = 'qbs'

    def imports(self):
        self.copy('*', dst='bin', src='bin')

    def test(self):
        self.run('bin/codesign_allocate -i bin/codesign_allocate -r -o codesign_allocate2')
        self.run('ls -l bin/codesign_allocate codesign_allocate2')
        self.run('file codesign_allocate2')
        self.run('./codesign_allocate2 -i codesign_allocate2 -r -o codesign_allocate3')
        self.run('ls -l codesign_allocate3')
        self.run('file codesign_allocate3')
