# Get values from run.csv
from decimal import Decimal

import pandas as pd
from openpyxl import load_workbook
import win32com.client as win32
import os
import pythoncom
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---EXCEL---

def get_raw_values(filename):
    df = pd.read_csv(filename)[1:41:2]
    data_dict = {}
    for row in range(0, 18):
        rd = df.iloc[row]
        data_dict[df.iloc[row][0]] = [rd[1], rd[2], rd[3], rd[4], rd[5], rd[6], rd[7], rd[8]]
    data_dict['rh'] = df.iloc[19][1]
    data_dict['temp'] = df.iloc[19][2]
    data_dict['pressure'] = df.iloc[19][3]
    return data_dict


def update_excel(file):
    pythoncom.CoInitialize()
    excel = win32.Dispatch('Excel.Application')
    workbook = excel.Workbooks.Open(ROOT_DIR + '/' + file)
    workbook.Save()
    workbook.Close()
    excel.Quit()


def to_excel(file, data):
    workbook = load_workbook(filename=file, read_only=False, keep_vba=True)
    ws = workbook.worksheets[0]
    list_of_rows = list(range(5,40,2))
    # Main Values
    for i in list_of_rows:
        freq = str(ws['A' + str(i)].value)
        entry = data[freq]
        ws['B' + str(i)] = float(entry[0])
        ws['C' + str(i)] = float(entry[1])
        ws['D' + str(i)] = float(entry[2])
        ws['E' + str(i)] = float(entry[3])
        ws['F' + str(i)] = float(entry[4])
        ws['G' + str(i)] = float(entry[5])
        ws['H' + str(i)] = float(entry[6])
        ws['I' + str(i)] = float(entry[7])
    # Env Variables
    ws['B43'] = data['rh']
    ws['C43'] = data['temp']
    ws['D43'] = data['pressure']
    workbook.save(file)
    workbook.close()


def get_excel(file):
    workbook = load_workbook(filename=file, data_only=True)
    ws = workbook.worksheets[0]
    value_range = list(range(20, 38))
    result_list = []
    for value in value_range:
        s = str(value)
        result_list.append((ws['L' + s].value, ws['M' + s].value))
    return result_list


def full_values():
    csv = "ReportFiles/run.csv"
    file = "ReportFiles/rt_calc.xlsm"
    data = get_raw_values(csv)
    to_excel(file, data)
    update_excel(file)
    values = get_excel(file)
    return values


def report_output(file):
    workbook = load_workbook(filename=file, data_only=True)
    ws = workbook.worksheets[3]
    hz_table = {}
    for value in list(range(16, 34)):
        s = str(value)
        hz_table[ws['A' + s].value] = {'t1': "%0.2f" % ws['B' + s].value, 't2': "%0.2f" % ws['C' + s].value,
                                       'oto': "%0.2f" % ws['D' + s].value}
    # Practical sound absorption coefficient
    psac = ["%0.2f" % ws['B39'].value, "%0.2f" % ws['C39'].value, "%0.2f" % ws['D39'].value, "%0.2f" % ws['E39'].value,
            "%0.2f" % ws['F39'].value, "%0.2f" % ws['G39'].value]
    # Weighted sound absorption coefficient
    wsac = ["%0.2f" % ws['C43'].value, ws['C44'].value, ws['C45'].value]
    # Single number ratings
    snr = ["%0.2f" % ws['B49'].value, "%0.2f" % ws['B50'].value]

    return hz_table, psac, wsac, snr

# ---WORD---
from docx.shared import Cm
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Cm, Inches, Mm, Emu
import random
import datetime


def changeValues(file):
    # Import Template
    template = DocxTemplate('ReportFiles/WordTemplate.docx')

    # Date
    x = datetime.datetime.now()
    hz_table, psac, wsac, snr = report_output("ReportFiles/rt_calc.xlsm")
    # TODO: Gather actual values.
    context = {
        'report_number': 'X',
        'issue_date': str(x.day) + '/' + str(x.month) + '/' + str(x.year),
        'test_date': str(x.day) + '/' + str(x.month) + '/' + str(x.year),
        'temperature': '25',
        'humidity': '50',
        'pressure': '1000',
        'hz': hz_table,
        'psac': psac,
        'wsac': wsac,
        'snr': snr
    }
    # Apply Values
    template.render(context)
    # Save Template
    template.save(file + '.docx')