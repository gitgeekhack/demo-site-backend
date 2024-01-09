import time
import boto3


class TextractHelper:
    def __init__(self):
        self.client = boto3.client('textract', region_name='us-east-1')

    def get_textract_response(self, image_path):
        img = open(image_path, 'rb')
        image_bytes = bytearray(img.read())
        response = self.client.analyze_document(Document={'Bytes': image_bytes}, FeatureTypes=['FORMS'])
        return response

    def __get_kv_map(self, response):
        """
        The method finds keys, values, blocks, words from textract response
        """
        blocks = response['Blocks']
        key_map = {}
        value_map = {}
        block_map = {}
        for block in blocks:
            block_id = block['Id']
            block_map[block_id] = block
            if block['BlockType'] == "KEY_VALUE_SET":
                if 'KEY' in block['EntityTypes']:
                    key_map[block_id] = block
                else:
                    value_map[block_id] = block

        return key_map, value_map, block_map

    def __find_value_block(self, key_block, value_map):
        """
        The method finds Value block for given Key block using Key-Value Relationships
        """
        for relationship in key_block['Relationships']:
            if relationship['Type'] == 'VALUE':
                for value_id in relationship['Ids']:
                    value_block = value_map[value_id]
        return value_block

    def __get_text(self, result, blocks_map):
        """
        The method finds text words with its area and coordinates using WORD blocks from textract response
        """
        items = []
        if 'Relationships' in result:
            for relationship in result['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        word = blocks_map[child_id]
                        if word['BlockType'] == 'WORD':
                            area = word['Geometry']['BoundingBox']['Width'] * word['Geometry']['BoundingBox']['Height']
                            y_1, y_2, x_1, x_2 = word['Geometry']['BoundingBox']['Top'], \
                                word['Geometry']['BoundingBox']['Top'] + word['Geometry']['BoundingBox']['Height'], \
                                word['Geometry']['BoundingBox']['Left'], \
                                word['Geometry']['BoundingBox']['Left'] + word['Geometry']['BoundingBox']['Width']
                            items.append(
                                {'text': word['Text'], 'area': area, 'x_1': x_1, 'y_1': y_1, 'x_2': x_2, 'y_2': y_2})
        return items

    def __key_val_merge(self, item):
        """
        The method combines various attributes of keys and values
        """
        item_text = ' '.join([i['text'] for i in item])
        item_area = sum([i['area'] for i in item])
        item_x_1 = min([i['x_1'] for i in item])
        item_y_1 = min([i['y_1'] for i in item])
        item_x_2 = max([i['x_2'] for i in item])
        item_y_2 = max([i['y_2'] for i in item])
        return {'text': item_text, 'area': item_area, 'x_1': item_x_1, 'y_1': item_y_1, 'x_2': item_x_2,
                'y_2': item_y_2}

    def __get_kv_relationship(self, key_map, value_map, block_map):
        """
        The method finds keys and values from textract response
        """
        kvs = []
        for block_id, key_block in key_map.items():
            value_block = self.__find_value_block(key_block, value_map)
            key = self.__get_text(key_block, block_map)
            val = self.__get_text(value_block, block_map)
            if key and val:
                kvs.append({'key': self.__key_val_merge(key), 'val': self.__key_val_merge(val)})
        return kvs

    def parse_textract_forms(self, response):
        """
        The method finds Key-Value pairs from Textract response json
        """
        key_map, value_map, block_map = self.__get_kv_map(response)
        kvs = self.__get_kv_relationship(key_map, value_map, block_map)

        key_values = []
        for form in kvs:
            key = form['key']['text']
            val = form['val']['text']
            if key in val:
                val = val.replace(key, '')
                val = val.strip()
            x_1 = min(form['key']['x_1'], form['val']['x_1'])
            y_1 = min(form['key']['y_1'], form['val']['y_1'])
            x_2 = max(form['key']['x_2'], form['val']['x_2'])
            y_2 = max(form['key']['y_2'], form['val']['y_2'])
            key_values.append({'key': key, 'value': val, 'x_1': x_1, 'y_1': y_1, 'x_2': x_2, 'y_2': y_2})

        return key_values

    def get_text(self, logger, image_path):
        start_time = time.time()
        response = self.get_textract_response(image_path)
        page_text = ''
        for i in response['Blocks']:
            if i['BlockType'] == 'LINE':
                page_text = page_text + i['Text'] + ' '

        key_values = self.parse_textract_forms(response)
        key_value_text = ''
        for i in key_values:
            key_value_text += f"{i['key']}: {i['value']}, "

        page_text = key_value_text + page_text
        logger.info(f"Text extraction using Textract completed in {time.time() - start_time} seconds.")
        return page_text
