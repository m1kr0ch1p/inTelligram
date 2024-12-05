from setuptools import setup
from setuptools.command.install import install
import subprocess

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        subprocess.check_call(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
        subprocess.check_call(['python', '-m', 'spacy', 'download', 'fr_core_news_sm'])
        subprocess.check_call(['python', '-m', 'spacy', 'download', 'es_core_news_sm'])
        subprocess.check_call(['python', '-m', 'spacy', 'download', 'pt_core_news_sm'])

setup(
    name='seu_pacote',
    version='0.1.0',
    packages=['seu_pacote'],
    install_requires=['spacy'],
    setup_requires=['spacy'],
    cmdclass={
        'install': PostInstallCommand,
    },
)
