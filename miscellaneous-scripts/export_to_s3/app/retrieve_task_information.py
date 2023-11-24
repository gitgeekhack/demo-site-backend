import requests
import os
import traceback
import sys
from app.constant import CvatUrls, CVAT_PROTO, CVAT_DOMAIN, CVAT_MAIL, CVAT_PASS, CVAT_USER
from app.cvat_utils import login
from app.business_rule_exception import UnableToLoginException, UnableToGetEnvironmentVariableException, \
    TaskNotFoundException, InvalidTokenException


class RetrieveTaskDetails:
    def __init__(self):
        try:
            self.CVAT_USER = CVAT_USER
            self.CVAT_MAIL = CVAT_MAIL
            self.CVAT_PASS = CVAT_PASS
            self.CVAT_DOMAIN = CVAT_DOMAIN
            self.CVAT_PROTO = CVAT_PROTO
            self.token = login()
            if None in (
                    self.CVAT_PROTO, self.CVAT_DOMAIN, self.CVAT_PASS, self.CVAT_MAIL, self.CVAT_USER):
                raise UnableToGetEnvironmentVariableException
        except UnableToLoginException as e:
            print('%s -> %s' % (e, traceback.format_exc()))
            self.token = None
        except UnableToGetEnvironmentVariableException as e:
            print('%s -> %s' % (e, traceback.format_exc()))

    def get_sublabels(self, label, sublabels):
        for attr in label['attributes']:
            sublabels[attr['id']] = {}
            sublabels[attr['id']]['type'] = attr['input_type']
            sublabels[attr['id']]['name'] = attr['name']

    def get_project_labels(self, proj_info, projects, labels, sublabels):
        projects[proj_info['id']] = proj_info['name']

        for label in proj_info['labels']:
            labels[label['id']] = label['name']
            self.get_sublabels(label, sublabels)

    def get_project_details(self):
        """
            Get label, sublabel and project details
            Returns:
                labels <dict>: label id mapping with its corresponding name
                sublabels <dict>: sublabel id mapping with its corresponding name and type
                projects <dict>: project id mapping with its corresponding name
        """
        labels, sublabels, projects = {}, {}, {}

        url = CvatUrls.CVAT_PROJECT_URL.format(self.CVAT_PROTO, self.CVAT_DOMAIN)
        response = requests.get(url, headers={'Authorization': f'Token {self.token}'})
        result = response.json()
        if response.status_code != 200:
            raise InvalidTokenException
        for proj_info in result['results']:
            self.get_project_labels(proj_info, projects, labels, sublabels)

        return labels, sublabels, projects

    def get_task(self, task_id):
        """
            Get general details of cvat task
            Parameters:
                task_id <int>: id of a task
            Returns:
                <dict>: general details of a task
        """
        url = CvatUrls.CVAT_TASK_URL_API.format(self.CVAT_PROTO, self.CVAT_DOMAIN, task_id)
        response = requests.get(url, headers={'Authorization': f'Token {self.token}'})
        if response.status_code != 200:
            raise TaskNotFoundException
        return response.json()

    def get_annotation_details(self, task_id, labels, sublabels):
        """
            Get annotation details of cvat task
            Parameters:
                task_id <int>: id of a task
                labels <dict>: label id mapping with its corresponding name
                sublabels <dict>: sublabel id mapping with its corresponding name and type
            Returns:
                <dict>: annotation details of a task
        """

        url = CvatUrls.CVAT_ANNOTATION_URL.format(self.CVAT_PROTO, self.CVAT_DOMAIN, task_id)
        res = requests.get(url, headers={'Authorization': f'Token {self.token}'})
        data = res.json()
        annotation_info = []
        for shape in data['shapes']:
            label_info = {'LabelName': labels[shape['label_id']], 'AnnotationType': shape['type'],
                          'PageNo': shape['frame'] + 1, 'SubLabels': [] if shape['attributes'] else None}
            if shape['type'] in {'rectangle', 'polyline'}:
                label_info['Annotations'] = {'X0': shape['points'][0],
                                             'Y0': shape['points'][1],
                                             'X1': shape['points'][2],
                                             'Y1': shape['points'][3]}
            if shape['attributes']:
                for attr in shape['attributes']:
                    label_info['SubLabels'].append(
                        {'Name': sublabels[attr['spec_id']]['name'], 'Value': attr['value'],
                         'Type': sublabels[attr['spec_id']]['type']})

            annotation_info.append(label_info)

        return annotation_info

    def format_output_response(self, task_id, task_data, annotation_data, projects):
        """
            Prepare output dict of task details
            Parameters:
                task_id <int>: CVAT task id
                task_data <dict>: general details of a task
                annotation_data <dict>: annotation details of a task
                projects <dict>: project id mapping with its corresponding name
            Returns:
                <dict>: formatted dictionary containing all details of a task
        """
        data = {}
        data['TaskID'] = task_id
        data['TaskName'] = task_data['name']
        data['TaskUrl'] = CvatUrls.CVAT_TASK_URL.format(self.CVAT_PROTO, self.CVAT_DOMAIN, task_data['id'])
        data['Project'] = projects[task_data['project_id']]
        if task_data['segments']:
            data['Assignee'] = task_data['assignee']['username'] if \
                task_data['assignee'] else None
            data['Reviewer'] = task_data['segments'][0]['jobs'][0]['reviewer']['username'] if \
                task_data['segments'][0]['jobs'][0]['reviewer'] else None
        data['Status'] = task_data['status']
        data['Labels'] = annotation_data if annotation_data else None

        return data

    def get_task_details(self, task_id):
        """
            Get task details using task id
            Parameters:
                task_id <int>: id of a cvat task
            Returns:
                <dict>: All details of a cvat task
        """
        try:
            labels, sublabels, projects = self.get_project_details()
            task_data = self.get_task(task_id)
            annotation_data = self.get_annotation_details(task_id, labels, sublabels)
            output = self.format_output_response(task_id, task_data, annotation_data, projects)
        except TaskNotFoundException as e:
            print('%s -> %s' % (e, traceback.format_exc()))
            return None
        except InvalidTokenException as e:
            print('%s -> %s' % (e, traceback.format_exc()))
            return None
        except Exception as e:
            print('%s -> %s' % (e, traceback.format_exc()))
            return None
        return output
