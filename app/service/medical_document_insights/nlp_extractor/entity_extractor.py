import boto3

from app.service.helper.segment import segmentation


def post_processing(segment):
    """
    Parse required entities from comprehend medical output per page
    :param segment: page or segement of page
    :return: entities per page
    """
    entity_result = {'diagnosis': [], 'treatment': []}
    for entity in segment['Entities']:
        if entity['Category'] == 'MEDICAL_CONDITION':
            traits = [trait['Name'] for trait in entity['Traits']]
            if 'DIAGNOSIS' in traits and 'HYPOTHETICAL' not in traits and 'NEGATION' not in traits and 'LOW_CONFIDENCE' not in traits:
                # if entity['Traits'][traits.index('DIAGNOSIS')]['Score'] >= 0.9:
                if entity['Text'].capitalize() not in entity_result['diagnosis']:
                    entity_result['diagnosis'].append((entity['Text']).capitalize())
        elif entity['Category'] == 'TEST_TREATMENT_PROCEDURE' and entity[
            'Type'] == 'TREATMENT_NAME' or entity['Type'] == 'PROCEDURE_NAME':  #and entity['Score'] >= 0.9
            traits = [trait['Name'] for trait in entity['Traits']]
            if 'NEGATION' not in traits or 'HYPOTHETICAL' not in traits:
                if entity['Text'].capitalize() not in entity_result['treatment']:
                    entity_result['treatment'].append((entity['Text']).capitalize())
    return entity_result


class ComprehendMedicalExtractor:
    """
    Extract pagewise entities of diagnosis and treatment
    """

    def __init__(self):
        self.client = boto3.client('comprehendmedical')

    def api_call(self, text):
        """
        Call comprehend medical api
        :param text: Medical text
        :return: response of api
        """
        response = self.client.detect_entities_v2(
            Text=text
        )
        return response

    def detect_entities(self, text):
        """
        Detect entities per page
        :param text:
        :return: entities per page
        """
        if len(text) > 20000:
            segments = segmentation(text)
            entities_so_far = {'diagnosis': [], 'treatment': []}

            for segment in segments:
                result = self.api_call(segment)
                entities = post_processing(result)
                entities_so_far['diagnosis'] = list(set(entities['diagnosis'] + entities_so_far['diagnosis']))
                entities_so_far['treatment'] = list(set(entities['treatment'] + entities_so_far['treatment']))
            return entities_so_far

        else:
            result = self.api_call(text)
            entities = post_processing(result)
            return entities

    def pagewise_entity_extractor(self, text):
        pagewise_entities = dict()
        for key, value in text.items():
            entities = self.detect_entities(value)
            pagewise_entities[key] = entities
        return pagewise_entities
