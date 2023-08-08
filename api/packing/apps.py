from django.apps import AppConfig
from django.core.management import call_command
# from django.contrib.auth.models import User
#
# from rest_framework.authtoken.models import Token

import MySQLdb

import os

import traceback


class PackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'packing'

    def create_db(self):
        db = MySQLdb.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
        )
        cursor = db.cursor()

        db_name = os.getenv('DB_NAME')

        if not db_name:
            return

        cursor.execute(f'CREATE DATABASE IF NOT EXISTS {db_name};')

    def ready(self):
        try:
            self.create_db()
        except:
            print('packing.apps.PackingConfig.ready: Failed to create db')

        try:
            call_command('create_pallete_types')
        except:
            print('packing.apps.PackingConfig.ready: Failed to call command create_pallete_types')

        try:
            call_command('create_token', silent=True)
        except:
            print('packing.apps.PackingConfig.ready: Failed to call command create_token')

