# Get values from run.csv
from decimal import Decimal

import pandas as pd
from openpyxl import load_workbook
import os
from docxtpl import DocxTemplate, InlineImage
import datetime
import pythoncom
from docx.shared import Mm
import xlwings as xw
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


# ---EXCEL---
def get_raw_values(filename):
    df = pd.read_csv(filename, engine='python')
    data_dict = {}
    for row in range(0, 18):
        rd = df.iloc[row]
        data_dict[df.iloc[row][0]] = [rd[1], rd[2], rd[3], rd[4], rd[5], rd[6], rd[7], rd[8]]
    data_dict['rh'] = df.iloc[19][1]
    data_dict['temp'] = df.iloc[19][2]
    data_dict['pressure'] = df.iloc[19][3]
    return data_dict


def update_excel(file):
    # open Excel app in the background
    pythoncom.CoInitialize()
    app_excel = xw.App(visible=False)
    print('app excel')
    wbk = xw.Book(file)
    print('book')
    wbk.api.RefreshAll()
    print('ref')
    wbk.save()
    print('save')
    # # kill Excel process
    app_excel.kill()
    print('kill')
    del app_excel
    print('del')
    # office = win32.Dispatch("Excel.Application")
    # wb = office.Workbooks.Open(file)
    # wb.RefreshAll()
    # wb.Save()
    # wb.Close()


def to_excel(file, data):
    workbook = load_workbook(filename=file, read_only=False, keep_vba=True)
    print('loaded Workbook')
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
    print('Paste Values')
    # Env Variables
    ws['B43'] = data['rh']
    ws['C43'] = data['temp']
    ws['D43'] = data['pressure']
    workbook.save(file)
    print('Save Values')
    workbook.close()
    print('Close')
    return


def get_excel(file):
    workbook = load_workbook(filename=file, data_only=True)
    ws = workbook.worksheets[0]
    value_range = list(range(20, 38))
    result_list = []
    for value in value_range:
        s = str(value)
        result_list.append((ws['L' + s].value, ws['M' + s].value))
    workbook.close()
    return result_list


# Complete entire csv data transaction.
def full_values(csv):
    file = ROOT_DIR + "\\ReportFiles\\rt_calc.xlsm"
    print(file)
    data = get_raw_values(csv)
    print('data')
    to_excel(file, data)
    print('to_excel')
    update_excel(file)
    print('update_excel')
    values = get_excel(file)
    print('values')
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
def changeValues(save_location, bracket_type, values):
    # Import Template
    template = DocxTemplate(ROOT_DIR + '\\ReportFiles\\Templates\\' + bracket_type + '.docx')
    # Date
    x = datetime.datetime.now()
    hz_table, psac, wsac, snr = report_output(ROOT_DIR + "\\ReportFiles\\rt_calc.xlsm")
    # TODO: Gather actual values.
    context = {
        'report_number': values[0],
        'issue_date': str(x.day) + '/' + str(x.month) + '/' + str(x.year),
        'test_date': str(x.day) + '/' + str(x.month) + '/' + str(x.year),
        'client': values[1],
        'specimen_name': values[2],
        'specimen_desc': values[3],
        'A': values[4],
        'B': values[5],
        'C': values[6],
        'temperature': values[7],
        'humidity': values[8],
        'pressure': values[9],
        'hz': hz_table,
        'psac': psac,
        'wsac': wsac,
        'snr': snr,
        'chart': InlineImage(template, ROOT_DIR + '\\ReportFiles\\chartImage.png', width=Mm(105))
    }
    print(context)
    # Apply Values
    template.render(context)
    # Save Template
    template.save(save_location + '\\Report.docx')

# full_values(ROOT_DIR + "/ReportFiles/NO_SAMPLE.csv")
# update_excel(ROOT_DIR + "\\ReportFiles\\rt_calc.xlsm")
# values = get_excel(ROOT_DIR + "\\ReportFiles\\rt_calc.xlsm")
# print(values)