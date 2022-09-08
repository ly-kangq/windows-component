from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import logger

datas, binaries, hiddenimports = collect_all('engineio', include_py_files=False)

logger.info('Collecting engineio: {}'.format(hiddenimports))
