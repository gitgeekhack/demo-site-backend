import tabula
from app.constant import PDFAnnotationAndExtraction
from app import logger
import os
import pandas as pd
import numpy as np
import fitz


class TableExtractor:
    def __init__(self, uuid):
        self.uuid = uuid

    @staticmethod
    async def __extract_col_label(table_data):
        file = os.path.join(PDFAnnotationAndExtraction.UPLOAD_FOLDER, table_data['filename'])
        doc = fitz.open(file)
        return doc[table_data['page']].get_textbox(table_data['column'])

    @staticmethod
    async def __extract_column_names(tables):
        file = os.path.join(PDFAnnotationAndExtraction.UPLOAD_FOLDER, tables['filename'])
        table_area = tables['columns']

        table = tabula.read_pdf(file, pages=str(tables['page'] + 1), stream=True,
                                area=[[table_area[1], table_area[0], table_area[3], table_area[2]]])
        df = table[0]
        row_count = len(df)
        df = df.fillna('')
        df = df.T.reset_index().T

        columns = []
        for col in df.columns:
            column_name = ''
            for val in df[col]:
                if val != '' and 'Unnamed' not in val:
                    column_name += val
                    column_name += '\n'
            columns.append(column_name[:-1])

        return columns, row_count

    @staticmethod
    async def __get_start_and_end_label(tables):
        doc = fitz.open(os.path.join(PDFAnnotationAndExtraction.UPLOAD_FOLDER, tables['filename']))
        start_label = doc[tables['page']].get_textbox(tables['start'])
        end_label = doc[tables['page']].get_textbox(tables['end'])
        return [start_label, end_label]

    async def __get_table_coordinates(self, doc, table_data, labels):
        try:
            blocks = doc[table_data['page']].get_text('blocks')

            boxes = []
            for block in blocks:
                for label in labels:
                    if label in block[4]:
                        boxes.append(block[:4])

            dynamic_box = [0, 0, 612.0, 0]
            dynamic_box[0] = min(boxes[0][0], boxes[1][0])
            dynamic_box[1] = max(boxes[0][1], boxes[1][1])
            dynamic_box[3] = min(boxes[0][3], boxes[1][3])
            dynamic_box[3], dynamic_box[1] = dynamic_box[1], dynamic_box[3]
        except IndexError as e:
            logger.error(f'Request ID: [{self.uuid}]  -> {e}')
            return None
        return dynamic_box

    @staticmethod
    async def __generate_table_output_response(result, table_data, table_name, data, bounding_box):
        if table_data['page'] not in result.keys():
            result[table_data['page']] = {}
        result[table_data['page']][table_name] = {}
        result[table_data['page']][table_name]['data'] = data
        result[table_data['page']][table_name]['bbox'] = bounding_box
        return result

    @staticmethod
    async def __extract_from_vectored(file, page_no, dynamic_box):
        table = tabula.read_pdf(
            os.path.join(PDFAnnotationAndExtraction.CONVERTED_PDF_FOLDER, os.path.basename(file)),
            pages=str(page_no), stream=True,
            area=[[dynamic_box[1], dynamic_box[0], dynamic_box[3], dynamic_box[2]]])
        if len(table) == 0:
            return pd.DataFrame()

        df = table[0]
        for col in df.columns:
            df[col] = df[col].astype(str).str.replace('[^a-zA-Z0-9#./ ]', '')
        df = df.replace('nan', np.NaN)

        for col in df.columns:
            for index, val in df[col].items():
                if isinstance(val, str) and len(val) == 0:
                    df[col][index] = np.NaN

        return df

    @staticmethod
    async def __remove_empty_columns(df):
        df.fillna('', inplace=True)
        for col in df.columns:
            if 'Unnamed' in col:
                if len(set(df[col].values)) == 1 and '' in set(df[col].values):
                    df.drop([col], axis=1, inplace=True)
        return df

    async def __parse_extracted_table(self, df, columns, row_count):
        df = await self.__remove_empty_columns(df)

        table_rows = df[row_count:]
        table_rows.columns = columns

        table_rows.reset_index(inplace=True, drop=True)
        delete_idx = []
        for row_index, row in table_rows.iterrows():
            empty_count = list(row.values).count('')
            if empty_count > len(columns) // 2:
                delete_idx.append(row_index)

                for idx, val in enumerate(list(table_rows.loc[row_index].values)):
                    if val != '':
                        table_rows.iloc[[row_index - 1], [idx]] += ' ' + val

        for idx in delete_idx:
            table_rows = table_rows.drop(idx)
        table_rows.reset_index(inplace=True, drop=True)

        return table_rows

    async def extract_table(self, file, page_no, dynamic_box):
        table = tabula.read_pdf(file, pages=str(page_no), stream=True,
                                area=[[dynamic_box[1], dynamic_box[0], dynamic_box[3], dynamic_box[2]]])

        if len(table) == 0:
            df = await self.__extract_from_vectored(file, page_no=page_no,
                                                    dynamic_box=dynamic_box)
        else:
            df = table[0]

        return df

    async def extract(self, tables, doc, file):
        result = {}
        for table_name, table_data in tables.items():
            columns, row_count = await self.__extract_column_names(table_data)
            labels = await self.__get_start_and_end_label(table_data)
            dynamic_box = await self.__get_table_coordinates(doc, table_data, labels)

            try:
                df = await self.extract_table(file, page_no=table_data['page'] + 1, dynamic_box=dynamic_box)
                table_rows = await self.__parse_extracted_table(df, columns, row_count)
                if 'column' in table_data.keys():
                    col_label = await self.__extract_col_label(table_data)
                    data = table_rows.to_html(columns=[col_label]).replace('\n', ' ')[89:]
                else:
                    data = table_rows.to_html().replace('\n', ' ')[89:]

                result = await self.__generate_table_output_response(result, table_data, table_name, data, dynamic_box)
            except (ValueError, TypeError) as e:
                logger.error(f'Request ID: [{self.uuid}]  -> {e}')
                result = await self.__generate_table_output_response(result, table_data, table_name, None, None)

        return result
