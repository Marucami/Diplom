# launcher.spec
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('money_tracker', 'money_tracker'),
        ('PostgreSQL', 'PostgreSQL'),
        ('Redis', 'Redis'),
        ('frontend_build', 'frontend_build'),
    ],
    hiddenimports=['waitress', 'money_tracker.wsgi', 'psycopg', 'pywebview'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='MoneyTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # для отладки можно True
    # icon='icon.ico',
)


import shutil
import os

hiddenimports=[
    'waitress',
    'waitress.server',
    'money_tracker.wsgi',
    'psycopg',
    'psycopg.pq',
    'psycopg._psycopg',
    'pywebview',
    'webview',
    'django',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'jwt_auth',
    'celery',
    'django_celery_beat',
    'django_celery_results',
],

def copy_dir(src, dst):
    if os.path.exists(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"Copied {src} to {dst}")

copy_dir('PostgreSQL', 'dist/MoneyTracker/PostgreSQL')
copy_dir('Redis', 'dist/MoneyTracker/Redis')
copy_dir('frontend_build', 'dist/MoneyTracker/frontend_build')