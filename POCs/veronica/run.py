import os

import fitz

path = "./files/"
files = os.listdir(path)


def get_payment_date(data):
    x = []
    for i in data:
        for j in i['spans']:
            x.append(j['text'].strip())
    keys = x[::2]
    values = x[1::2]
    result = {}
    if len(keys) == len(values):
        for key, value in zip(keys, values):
            result[key] = value
    try:
        r = result['Invoice Date:']
        return r
    except Exception as e:
        print(e)


def get_name(x):
    name = x[0]['spans'][0]['text'].strip()
    return name


def get_add(x):
    lines = [x[7]['lines'], x[8]['lines']]

    address = []
    for line in lines:
        address.append(line[0]['spans'][0]['text'].strip())
    return " ".join(address)


def get_payment_notes(x):
    lines = [x[-2]['lines'], x[-1]['lines']]

    address = []
    for line in lines:
        address.append(line[0]['spans'][0]['text'].strip())
    keys = address[::2]
    values = address[1::2]
    result = {}
    if len(keys) == len(values):
        for key, value in zip(keys, values):
            result[key] = value
    try:
        r = result['Payment Notes']
        return r
    except Exception as e:
        print(e)


def extract_data(x, file_name):
    result = {}
    result['payment_date'] = get_payment_date(x[4]['lines'])
    result['name'] = get_name(x[6]['lines'])
    result['address'] = get_add(x)
    policy_number, line_of_business, bf, vr_fee, nb_eft, total_paid, total_due = extacrt_tables(file_name)
    result['policy_number'] = policy_number
    result['line_of_business'] = line_of_business
    result['bf'] = bf
    result['vr_fee'] = vr_fee
    result['nb_eft'] = nb_eft
    result['amount_paid'] = total_paid
    result['amount_left_to_pay'] = float(total_due.replace('$', '')) - float(total_paid.replace('$', ''))
    result['payment_notes'] = get_payment_notes(x)
    return result


import tabula
import numpy as np


def extacrt_tables(x):
    tables = tabula.read_pdf(x, pages="all")
    df = tables[0]
    df['Amounts Billed'] = df['Amounts Billed'].replace(np.nan, 'Total')
    df.index = df['Amounts Billed']
    df = df.astype(object).replace(np.nan, 'None')
    try:
        policy_number = df['Policy Number'].tolist()[0]
    except Exception as e:
        # print(e)
        policy_number = None

    try:
        line_of_business = df['Line Of Business'].tolist()[0]
    except Exception as e:
        # print(e)
        line_of_business = None
    try:
        bf = df.loc['BF']['Amount Due']
    except Exception as e:
        # print(e)
        bf = None
    try:
        vr_fee = df.loc['VR FEE']['Amount Due']
    except Exception as e:
        # print(e)
        vr_fee = None
    try:
        nb_eft = df.loc['NB EFT TO COMPANY']['Amount Due']
    except Exception as e:
        # print(e)
        nb_eft = None
    try:
        total_paid = df.loc['Total']['Amount Paid']
    except Exception as e:
        # print(e)
        total_paid = None
    try:
        total_due = df.loc['Total']['Amount Due']
    except Exception as e:
        # print(e)
        total_due = None
    return policy_number, line_of_business, bf, vr_fee, nb_eft, total_paid, total_due


for filepath in files:
    with fitz.open(os.path.join(path, filepath)) as doc:
        nblocks = []
        for page in doc:
            nblocks.extend(page.getText("dict")['blocks'])
            for block in page.getText("dict")['blocks']:
                highlight = page.addRectAnnot(block["bbox"])
                highlight.setBlendMode(fitz.PDF_BM_Multiply)
                highlight.update()

        data = extract_data(nblocks, os.path.join(path, filepath))
        print('*' * 100)
        print(f'Document: [{filepath}]')
        print('*' * 100)
        for k, v in data.items():
            print(f'{k:<30} => {v}')
        print()
        print()
        # doc.save(f'./out/out_{filepath}.pdf')
