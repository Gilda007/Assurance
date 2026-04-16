# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('addons', 'addons')]
binaries = []
hiddenimports = ['email', 'email.mime', 'email.mime.multipart', 'email.mime.text', 'email.mime.base', 'email.mime.image', 'email.mime.application', 'email.encoders', 'email.utils', 'smtplib', 'cv2', 'opencv-python', 'numpy', 'numpy.core', 'numpy.core._multiarray_umath', 'numpy.random', 'numpy.linalg', 'PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui', 'PySide6.QtNetwork', 'PySide6.QtSvg', 'PySide6.QtPrintSupport', 'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets', 'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets', 'PySide6.QtSql', 'PySide6.QtXml', 'PySide6.QtCharts', 'PySide6.QtCharts.QChart', 'PySide6.QtCharts.QChartView', 'PySide6.QtCharts.QPieSeries', 'PySide6.QtCharts.QBarSeries', 'PySide6.QtCharts.QBarSet', 'PySide6.QtCharts.QLineSeries', 'PySide6.QtCharts.QCategoryAxis', 'PySide6.QtCharts.QValueAxis', 'qrcode', 'qrcode.image.pil', 'qrcode.image.svg', 'qrcode.image.base', 'qrcode.util', 'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont', 'PIL.ImageFilter', 'PIL.ImageEnhance', 'PIL.ImageColor', 'PIL.ImageFile', 'PIL.ImagePalette', 'PIL.ImageMode', 'PIL.ImageSequence', 'PIL.TiffImagePlugin', 'PIL.JpegImagePlugin', 'PIL.PngImagePlugin', 'PIL.GifImagePlugin', 'pandas', 'pandas.core', 'pandas.io', 'pandas.io.sql', 'pandas.io.parsers', 'pandas.io.excel', 'pandas.io.json', 'pandas.io.html', 'sqlalchemy', 'sqlalchemy.dialects.postgresql', 'sqlalchemy.dialects.mysql', 'sqlalchemy.dialects.sqlite', 'sqlalchemy.ext.declarative', 'sqlalchemy.orm', 'psycopg2', 'psycopg2._psycopg', 'psycopg2.extensions', 'psycopg2.extras', 'psycopg2.pool', 'psycopg2.sql', 'psycopg2.errorcodes', 'requests', 'requests.packages', 'requests.packages.urllib3', 'urllib3', 'urllib3.packages', 'certifi', 'idna', 'charset_normalizer', 'flask', 'flask.views', 'flask.json', 'flask_cors', 'reportlab', 'reportlab.lib', 'reportlab.lib.pagesizes', 'reportlab.lib.units', 'reportlab.lib.colors', 'reportlab.lib.utils', 'reportlab.lib.fonts', 'reportlab.lib.sequencer', 'reportlab.pdfbase', 'reportlab.pdfbase.pdfmetrics', 'reportlab.pdfbase.ttfonts', 'reportlab.pdfgen', 'reportlab.pdfgen.canvas', 'reportlab.pdfgen.textobject', 'reportlab.platypus', 'reportlab.platypus.doctemplate', 'reportlab.platypus.flowables', 'reportlab.platypus.paragraph', 'reportlab.platypus.tables', 'reportlab.platypus.frames', 'reportlab.graphics', 'reportlab.graphics.shapes', 'reportlab.graphics.widgets', 'reportlab.graphics.renderPDF', 'reportlab.graphics.charts', 'reportlab.graphics.charts.barcharts', 'reportlab.graphics.charts.linecharts', 'reportlab.graphics.charts.piecharts', 'openpyxl', 'openpyxl.cell', 'openpyxl.reader', 'openpyxl.workbook', 'openpyxl.writer', 'openpyxl.styles', 'openpyxl.formatting', 'openpyxl.chart', 'openpyxl.utils', 'bcrypt', 'PyMySQL', 'mysqlclient', 'pyqtgraph', 'pyqtgraph.Qt', 'pyqtgraph.graphicsItems', 'pyqtgraph.widgets', 'dateutil', 'dateutil.parser', 'dateutil.tz', 'dateutil.relativedelta', 'dotenv', 'greenlet', 'packaging', 'packaging.version', 'packaging.specifiers', 'packaging.requirements', 'typing_extensions', 'six', 'et_xmlfile', 'xlrd', 'altgraph', 'colorama', 'setuptools', 'setuptools._vendor', 'shiboken6', 'shiboken6.shiboken6', 'cffi', 'cryptography', 'cryptography.hazmat', 'cryptography.hazmat.backends', 'cryptography.hazmat.primitives', 'jinja2', 'jinja2.ext', 'markupsafe', 'itsdangerous', 'click', 'werkzeug', 'werkzeug.utils', 'werkzeug.serving', 'werkzeug.wsgi', 'werkzeug.middleware', 'pytz', 'tzdata']
tmp_ret = collect_all('PySide6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PySide6.QtCharts')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('sqlalchemy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('psycopg2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pandas')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('numpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PIL')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('requests')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('qrcode')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('reportlab')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('openpyxl')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('bcrypt')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('flask')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('flask_cors')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PyMySQL')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('mysqlclient')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pyqtgraph')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('python_dateutil')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('dotenv')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('urllib3')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('certifi')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('idna')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('charset_normalizer')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('greenlet')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('packaging')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('typing_extensions')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('six')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('et_xmlfile')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('xlrd')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('altgraph')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('colorama')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('setuptools')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('shiboken6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pytz')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('tzdata')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('markupsafe')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('jinja2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('itsdangerous')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('click')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('werkzeug')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('cffi')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pycparser')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('cryptography')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('opencv_python')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('cv2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('opencv-python')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LOMETA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LOMETA',
)
