
# ===============================================
# Imports and Configuration
# ===============================================
import logging
import re
from pathlib import Path

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('mb52_zsd_dmnd')

PROJECT_FOLDER = 'MB52_ZSD_DMND'
MB52_FILE_NAME = 'MB52_Report.csv'
SD48_FILE_NAME = 'ZSD_DMND_Report.csv'
OUTPUT_FILE_NAME = 'MB52_SD48_Analysis.xlsx'
MB52_SPARK_PATH = f'Files/{PROJECT_FOLDER}/{MB52_FILE_NAME}'
SD48_SPARK_PATH = f'Files/{PROJECT_FOLDER}/{SD48_FILE_NAME}'
DEFAULT_LAKEHOUSE = Path('/lakehouse/default')
DEFAULT_FILES = DEFAULT_LAKEHOUSE / 'Files'
ROOT = DEFAULT_FILES / PROJECT_FOLDER
MB52_PATH = ROOT / MB52_FILE_NAME
SD48_PATH = ROOT / SD48_FILE_NAME
OUTPUT_PATH = ROOT / OUTPUT_FILE_NAME
ANALYSIS_DATE_OVERRIDE = None  # Example: '2026-10-06'
WAREHOUSE_RESUME = 'Almacen'

BASE_ROWS = [
    ('US90','ZLFG','Finished Goods','Finish Good','FG Almacen','Validate'),
    ('US90','ZLD1','Direct Material','Almacen','Almacen','Main'),
    ('US90','ZLMN','Production Mini','Piso Prod','Piso Prod','Validate'),
    ('US90','ZXCU','Production CDU','Piso Prod(CDU)','Piso Prod','Validate'),
    ('US90','ZLIA','Inv. Adjustments','Inv Adjustment','Inv Adjustment','Validate'),
    ('US90',None,None,'Blank','Blank','Validate'),
    ('US90','ZLBL','Blocked Material','Blocked Material','Blocked Material','Validate'),
    ('US90','ZLEW','Ext-Warehouse','External WHS','Ext Almacen','Validate'),
    ('US90','ZLSC','Scrap','Scrap','Scrap','Validate'),
    ('US90','ZLLA','R&D Samples','R&D Samples','R&D Samples','Validate'),
    ('US90','ZLWA','Inv. under anály','Inv Adjustment','Inv Adjustment','Validate'),
    ('US90','ZLMD','Production Midi','Piso Prod(Midi)','Piso Prod','Validate'),
    ('US90','ZLTD','Quality TDAs','Quality','Quality','Validate'),
    ('US90','ZLQA','Quality Samples','Quality Samples','Quality','Validate'),
    ('US90','ZWET','Prd Rotor WET','Piso Prod(Rotor)','Piso Prod','Validate'),
    ('US90','ZFAN','Prd ECM FAN','Piso Prod(Fan)','Piso Prod','Validate'),
    ('US90','ZXEL','Prd Electronicos','Piso Prod(Elect)','Piso Prod','Validate'),
    ('US90',None,'Blank','Blank','Blank','Validate')
]
BASE_COLUMNS = ['Plant','Storage_Location','Storage_Location_Description','Location','Resume','Note']


