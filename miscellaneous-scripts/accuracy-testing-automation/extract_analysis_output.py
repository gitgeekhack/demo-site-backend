import os
import json
import pandas as pd
import accuracy_statistics


class MakeCsv:
    def __extract(self, name):
        file = open(name)
        data = json.load(file)
        file.close()

        dic = {'name': [],
               'date_of_birth': [],
               'height': [],
               'weight': [],
               'doctor_name': [],
               'date': [],
               'date_of_injury': [],
               'medical_history': [],
               'diagnoses': [],
               'treatments': [],
               'prognoses': [],
               }

        for patient_details in data['categorized_document']['patient'].keys():
            if patient_details in dic.keys():
                if data['categorized_document']['patient'][patient_details]:
                    if 'unit' in data['categorized_document']['patient'][patient_details].keys():
                        dic[patient_details].append(
                            str(data['categorized_document']['patient'][patient_details]['value']) +
                            ' ' + data['categorized_document']['patient'][patient_details]['unit'])
                    else:
                        dic[patient_details].append(data['categorized_document']['patient'][patient_details]['value'])
                else:
                    dic[patient_details].append('')

        for encounter in data['categorized_document']['encounters']:
            if encounter['doctor_name']:
                dic['doctor_name'].append(encounter['doctor_name']['value'])
            if encounter['date']:
                dic['date'].append(encounter['date']['value'])
            for section in encounter['sections']:
                for context in section['contexts']:
                    for entity in context['entities']:
                        if 'type' in entity.keys():
                            dic[entity['type']].append(
                                entity['entity'].replace('\n', ''))
                        else:
                            dic[section['section']].append(section['section'])

        return dic

    def extract(self, filepaths):

        final_dic = {'request_id': [],
                     'document_name': [],
                     'name': [],
                     'date_of_birth': [],
                     'height': [],
                     'weight': [],
                     'doctor_name': [],
                     'date': [],
                     'date_of_injury': [],
                     'medical_history': [],
                     'diagnoses': [],
                     'treatments': [],
                     'prognoses': [],
                     }

        for index in range(len(filepaths)):
            filepath = filepaths[index]
            dic = self.__extract(filepath)

            file = open(filepath.replace('entity-extraction.json', 'pre-chatgpt-entities.json'))
            entity = json.load(file)
            file.close()

            for key in final_dic.keys():
                if key == 'request_id':
                    req_id = filepaths[index].replace(os.getcwd(), '')
                    red_id = req_id.split('/')[2]
                    final_dic[key].append(red_id)
                    final_dic[key].append('PRE - GPT ' + red_id)
                elif key == 'document_name':
                    pass
                else:
                    final_dic[key].append('\n'.join(dic[key]))
                    if key in ['medical_history', 'diagnoses', 'treatments']:
                        final_dic[key].append('\n'.join(entity[key]))
                    else:
                        final_dic[key].append('')

        doc_list = pd.read_csv('res.csv')
        req = doc_list['request_ids'].to_list()
        dn = doc_list['doc_name'].to_list()
        for i in range(len(final_dic['request_id'])):
            if 'PRE - GPT' in final_dic['request_id'][i]:
                index = req.index(final_dic['request_id'][i].replace('PRE - GPT ', ''))
                final_dic['document_name'].append('PRE - GPT ' + dn[index])
            else:
                index = req.index(final_dic['request_id'][i])
                final_dic['document_name'].append(dn[index])

        res = pd.DataFrame.from_dict(final_dic)
        res.rename(columns={'name': 'patient_name', 'date': 'encounter_date'}, inplace=True)
        accuracy_statistics.compare(res)
