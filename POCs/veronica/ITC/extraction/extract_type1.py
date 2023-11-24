class ITC_Type1:
    def check_blocks(self, blocks):
        for i in range(2, 5):
            if blocks[i]['lines'][0]['spans'][0]['text'] == 'Name':
                return i
        return 0

    def get_insured_info(self, blocks, block_number):
        insured_dict = {}
        i = block_number
        insured_dict['Insured Name'] = blocks[i]['lines'][1]['spans'][0]['text']
        insured_dict['Insured Address'] = blocks[i]['lines'][7]['spans'][0]['text']
        insured_dict['Insured Zip code'] = blocks[i]['lines'][13]['spans'][0]['text']
        return insured_dict

    def get_agent_info(self, blocks, block_number):
        agent_dict = {}
        i = block_number
        agent_dict['Agent Name'] = blocks[i]['lines'][5]['spans'][0]['text']
        if blocks[i]['lines'][16]['spans'][0]['text'] == 'City, State ZIP':
            text = blocks[i]['lines'][17]['spans'][0]['text']
        else:
            text = blocks[i]['lines'][16]['spans'][0]['text']
            text = text.split('City, State ZIP', 1)[1]
        agent_dict['Agent Zip code'] = text
        if blocks[i]['lines'][34]['spans'][0]['text'] == 'Producer Code':
            text = blocks[i]['lines'][35]['spans'][0]['text']
        else:
            text = blocks[i]['lines'][31]['spans'][0]['text']
            text = text.split('Producer Code', 1)[1]
        agent_dict["Producer Code"] = text.strip()
        return agent_dict

    def get_company_info(self, blocks, block_number):
        i = block_number
        company_dict = {}
        if blocks[i]['lines'][42]['spans'][0]['text'] == 'Company':
            text = blocks[i]['lines'][43]['spans'][0]['text']
        else:
            text = blocks[i]['lines'][38]['spans'][0]['text']
        company_dict["Company"] = text
        if blocks[i]['lines'][50]['spans'][0]['text'] == 'Policy Term':
            text = blocks[i]['lines'][51]['spans'][0]['text']
        else:
            text = blocks[i]['lines'][46]['spans'][0]['text']
        company_dict["Policy Term"] = text
        return company_dict

    def get_driver_and_vehicle_info(self, blocks, block_number, doc):
        driver_info_dict = {}
        temp_list = []
        i = block_number
        text = blocks[i]['lines'][59]['spans'][0]['text']
        if text.split(' ')[0] == 'Veh':
            for j in range(59, 71):
                temp_list.append(blocks[i]['lines'][j]['spans'][0]['text'])
        else:
            text = blocks[i]['lines'][54]['spans'][0]['text']
            if text.split(' ')[0] == 'Veh':
                for j in range(54, 66):
                    temp_list.append(blocks[i]['lines'][j]['spans'][0]['text'])

        veh_list = [x for x in temp_list if "Veh" in x]
        drv_list = [x for x in temp_list if "Drv" in x]
        driver_info_dict['Vehicles'] = veh_list
        driver_info_dict['Drivers'] = drv_list

        temp_list = [x for x in range(70, 100) if blocks[i]['lines'][x]['spans'][0]['text'] == 'Driver Information']
        temp_list.extend(
            [x for x in range(temp_list[0], 100) if blocks[i]['lines'][x]['spans'][0]['text'] == 'Driver DOB'])
        driver_info = []
        driver_dob = []
        fr_filing = []
        comp_deductible = []
        coll_deductible = []
        for x in range(temp_list[0] + 1, temp_list[0] + len(drv_list) + 1): driver_info.append(
            blocks[i]['lines'][x]['spans'][0]['text'])
        driver_info_dict['Info'] = driver_info

        for x in range(temp_list[1] + 1, temp_list[1] + len(drv_list) + 1): driver_dob.append(
            blocks[i]['lines'][x]['spans'][0]['text'])
        driver_info_dict['DOB'] = driver_dob

        temp_list.extend(
            [x for x in range(temp_list[1] + len(drv_list) + 1, 120) if
             blocks[i]['lines'][x]['spans'][0]['text'] == 'FR Filing'])
        for x in range(temp_list[2] + 1, temp_list[2] + len(drv_list) + 1): fr_filing.append(
            blocks[i]['lines'][x]['spans'][0]['text'])
        driver_info_dict['FR filling'] = fr_filing
        line_number = len(blocks[i]['lines'])

        text = [x for x in range(temp_list[0], line_number) if
                blocks[i]['lines'][x]['spans'][0]['text'] == 'Comprehensive Deductible']

        if text:
            for x in range(text[0] + 1, text[0] + len(veh_list) + 1): comp_deductible.append(
                blocks[i]['lines'][x]['spans'][0]['text'])
        driver_info_dict['Comprehensive Deductible'] = comp_deductible

        text = [x for x in range(temp_list[0], line_number) if
                blocks[i]['lines'][x]['spans'][0]['text'] == 'Collision Deductible']
        if text:
            for x in range(text[0] + 1, text[0] + len(veh_list) + 1): coll_deductible.append(
                blocks[i]['lines'][x]['spans'][0]['text'])

        driver_info_dict['Collision Deductible'] = coll_deductible
        text = []
        text = [x for x in range(temp_list[0], line_number) if
                blocks[i]['lines'][x]['spans'][0]['text'] == 'Liability BI']
        if text:
            driver_info_dict['Liability BI'] = blocks[i]['lines'][text[0] + 1]['spans'][0]['text']
        else:
            driver_info_dict['Liability BI'] = None

        text = []
        text = [x for x in range(temp_list[0], line_number) if
                blocks[i]['lines'][x]['spans'][0]['text'] == 'Liability PD']
        if text:
            driver_info_dict['Liability PD'] = blocks[i]['lines'][text[0] + 1]['spans'][0]['text']
        else:
            driver_info_dict['Liability PD'] = None

        text = []
        text = [x for x in range(temp_list[0], line_number) if
                blocks[i]['lines'][x]['spans'][0]['text'] == 'Uninsured BI']
        if text:
            driver_info_dict['Uninsured BI'] = blocks[i]['lines'][text[0] + 1]['spans'][0]['text']
        else:
            driver_info_dict['Uninsured BI'] = None

        text = []
        text = [x for x in range(temp_list[0], line_number) if
                blocks[i]['lines'][x]['spans'][0]['text'] == 'Unins PD/Coll Ded Waiver']
        if text:
            driver_info_dict['Unins PD/Coll Ded Waiver'] = blocks[i]['lines'][text[0] + 1]['spans'][0]['text']
        else:
            driver_info_dict['Unins PD/Coll Ded Waiver'] = None
        vehicle_info_dict = {}
        text = []
        line_number = len(blocks[i + 1]['lines'])
        text = [x for x in range(0, line_number) if
                blocks[i + 1]['lines'][x]['spans'][0]['text'] == 'Vehicle Information']
        for x in range(0, line_number):
            if blocks[i + 1]['lines'][x]['spans'][0]['text'] == 'Vehicle Attributes':
                text.append(x)
        vehicle_info = []
        if text:
            for x in range(text[0] + 6, text[1]): vehicle_info.append(blocks[i + 1]['lines'][x]['spans'][0]['text'])
            line = x
            veh_info = []
            for x in range(0, len(vehicle_info), 5):
                veh_info.append(vehicle_info[x:x + 5])
            vehicle_info_dict['Vehicle Info'] = veh_info
        else:
            vehicle_info_dict['Vehicle Info'] = None

        annual_miles_driven = []
        temp = [x for x in range(line, len(blocks[i + 1]['lines'])) if
                blocks[i + 1]['lines'][x]['spans'][0]['text'] == 'Annual Miles Driven']
        if temp:
            for x in range(temp[0] + 1, temp[0] + len(veh_list) + 1):
                annual_miles_driven.append(blocks[i + 1]['lines'][x]['spans'][0]['text'])

        if not annual_miles_driven:
            page = doc[1]
            block_num = 0
            line_num = 0
            blocks = page.getText('dict')['blocks']
            for i in range(0, len(blocks)):
                if blocks[i]['type'] == 0:
                    if len(blocks[i]['lines']) > 2:
                        temp = [x for x in range(0, len(blocks[i]['lines'])) if
                                blocks[i]['lines'][x]['spans'][0]['text'] == 'Annual Miles Driven']
                        if len(temp) > 0:
                            block_num = i
                            line_num = temp[0]
                            break
            for x in range(temp[0] + 1, temp[0] + len(veh_list) + 1):
                annual_miles_driven.append(blocks[block_num]['lines'][x]['spans'][0]['text'])
        vehicle_info_dict['Annual Miles'] = annual_miles_driven
        block_dict = {}
        driver_attribute_dict = {}
        months_foreign_license = []
        months_mvr_exp_us = []
        for page in doc:
            if not months_foreign_license or not months_mvr_exp_us:
                blocks = page.getText('dict')['blocks']
                for i in range(0, len(blocks)):
                    if blocks[i]['type'] == 0:
                        if len(blocks[i]['lines']) > 2:
                            temp = [x for x in range(0, len(blocks[i]['lines'])) if
                                    blocks[i]['lines'][x]['spans'][0]['text'] == 'Months Foreign License']
                            if len(temp) > 0:
                                block_dict['Months Foreign License'] = i
                                for x in range(temp[0] + 1, temp[0] + len(drv_list) + 1):
                                    months_foreign_license.append(
                                        blocks[block_dict['Months Foreign License']]['lines'][x]['spans'][0]['text'])

                            temp = [x for x in range(0, len(blocks[i]['lines'])) if
                                    blocks[i]['lines'][x]['spans'][0]['text'] == 'Months MVR Experience U.S.']
                            if len(temp) > 0:
                                block_dict['Months MVR Experience U.S.'] = i
                                for x in range(temp[0] + 1, temp[0] + len(drv_list) + 1):
                                    months_mvr_exp_us.append(
                                        blocks[block_dict['Months MVR Experience U.S.']]['lines'][x]['spans'][0][
                                            'text'])
                                break
        driver_attribute_dict['Months MVR Experience U.S.'] = months_mvr_exp_us
        driver_attribute_dict['Months Foreign License'] = months_foreign_license

        return driver_info_dict, vehicle_info_dict, driver_attribute_dict

    def get_driver_violations(self, doc):
        driver_violations_dict = {}
        block_dict = {}
        line_dict = {}
        count = 0
        violations = []
        start = []
        end = []
        list = ['Driver Violations', 'Driver Suspensions/Reinstatements']
        for page in doc:
            if not count:
                blocks = page.getText('dict')['blocks']
                for i in range(0, len(blocks)):
                    if blocks[i]['type'] == 0:
                        if len(blocks[i]['lines']) > 2:
                            for x in range(0, len(blocks[i]['lines'])):
                                temp = blocks[i]['lines'][x]['spans'][0]['text']
                                if temp in list:
                                    block_dict[temp] = i
                                    line_dict[temp] = x

                if 'Driver Suspensions/Reinstatements' in block_dict.keys():
                    for i in range(block_dict['Driver Violations'],
                                   block_dict['Driver Suspensions/Reinstatements'] + 1):
                        for x in range(len(blocks[i]['lines'])):
                            violations.append(blocks[i]['lines'][x]['spans'][0]['text'])
                    start = violations.index('Driver Violations')
                    end = violations.index('Driver Suspensions/Reinstatements')
                    violations = violations[start + 1:end]
                    break
        if violations:
            if violations[0] == 'None':
                count = 0
            else:
                v = [violations[x:x + 6] for x in range(0, len(violations), 7)]
                count = len(v) - 1
        driver_violations_dict['Driver Violations'] = count
        return driver_violations_dict

    def get_excluded_driver(self, doc):
        driver_dict = {}
        excluded_driver_dict = {}
        v = []
        count = 0
        temp_list = []

        for page in doc:
            if not count:
                blocks = page.getText('dict')['blocks']
                for i in range(0, len(blocks)):
                    if blocks[i]['type'] == 0 and len(blocks[i]['lines']) > 2:
                        for x in range(0, len(blocks[i]['lines'])):
                            temp = blocks[i]['lines'][x]['spans'][0]['text']
                            if temp == 'Excluded Driver(s)':
                                for j in range(x, len(blocks[i]['lines'])):
                                    temp_list.append(blocks[i]['lines'][j]['spans'][0]['text'])
                                break
        if temp_list:
            name = temp_list.index('Relationship')
            temp_list = temp_list[name + 1:]
            v = [temp_list[x:x + 5] for x in range(0, len(temp_list), 5)]
            if v:
                for i in range(0, len(v)):
                    temp_dict = {}
                    if len(v[i]) == 5:
                        count = count + 1
                        temp_dict['Name'] = v[i][0]
                        temp_dict['DOB'] = v[i][1]
                        excluded_driver_dict[count] = temp_dict

        driver_dict['Excluded Driver(s)'] = excluded_driver_dict
        return driver_dict
