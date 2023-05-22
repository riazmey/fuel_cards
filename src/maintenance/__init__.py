"""
    Script to import data from .csv files and credential files to Model Database DJango
    To execute this script run:
                                1) python manage.py shell
                                2) import maintenance
                                3) maintenance.do_filling()
                                3) exit()
"""

from maintenance.main import do_filling
