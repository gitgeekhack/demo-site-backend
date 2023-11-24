class ITC_Type3:
    def check_blocks(self, blocks, word_list, end=50):
        block_dict = {}
        for i in range(0, end):
            if blocks[i]['type'] == 0:
                if blocks[i]['lines'][0]['spans'][0]['text'] in word_list:
                    block_dict[blocks[i]['lines'][0]['spans'][0]['text']] = i
        return block_dict

    def get_insured_and_agent_info(self, blocks, block_dict):
        insured_dict = {}
        agent_dict = {}
        insured_name = []
        agent_Name = []
        end = [x for x in range(1, len(blocks[block_dict['Name']]['lines'])) if
               blocks[block_dict['Name']]['lines'][x]['spans'][0]['text'] == 'Name']
        for x in range(1, end[0]):
            insured_name.append(blocks[block_dict['Name']]['lines'][x]['spans'][0]['text'])

        for x in range(end[0] + 1, len(blocks[block_dict['Name']]['lines'])):
            agent_Name.append(blocks[block_dict['Name']]['lines'][x]['spans'][0]['text'])

        insured_dict['Insured Name'] = ' '.join(map(str, insured_name)).strip()
        agent_dict['Agent Name'] = ' '.join(map(str, agent_Name)).strip()
        Address = []
        end = [x for x in range(1, len(blocks[block_dict['Address']]['lines'])) if
               blocks[block_dict['Address']]['lines'][x]['spans'][0]['text'] == 'Address']

        for x in range(1, end[0]): Address.append(blocks[block_dict['Address']]['lines'][x]['spans'][0]['text'])
        insured_dict['Insured Address'] = ' '.join(map(str, Address)).strip()

        start = block_dict['Address']
        end = block_dict.get("Phone") or block_dict.get("Phone Number") or block_dict.get("Phone Number ( ) -")
        text_list = []
        for i in range(start + 1, end):
            for j in range(0, len(blocks[i]['lines'])):
                text_list.append(blocks[i]['lines'][j]['spans'][0]['text'])
        x = ' '.join(map(str, text_list)).strip()
        text_list = x.replace('City, State ZIP', '').split('\xa0 \xa0')
        insured_dict['Insured Zip code'] = text_list[0].strip()
        agent_dict['Agent Zip code'] = text_list[1].strip()
        producer_block = block_dict.get("Work") or block_dict.get("Work Number")
        producer = []
        for x in range(0, len(blocks[producer_block]['lines'])): producer.append(
            blocks[producer_block]['lines'][x]['spans'][0]['text'])
        text_list = ' '.join(map(str, producer)).strip().replace('Producer Code', '').split('\xa0 \xa0')
        agent_dict['Producer code'] = text_list[1].strip()
        return insured_dict, agent_dict

    def get_company_info(self, blocks, block_dict):
        company_dict = {'Company': blocks[block_dict['Company']]['lines'][1]['spans'][0]['text'],
                        'Policy Term': blocks[block_dict['Policy Term']]['lines'][1]['spans'][0]['text']}
        return company_dict

    def get_driver_and_vehicle_info(self, blocks, block_dict, doc):
        driver_info_dict = {}
        vehicle_info_dict = {}
        start = block_dict.get("Quote By")
        veh_list = []
        drv_list = []
        driver_info = []
        driver_dob = []
        fr_filing = []
        comp_deductible = []
        coll_deductible = []
        liability_bi = ''
        liability_pd = None
        uni_bi = ''
        uni_pd = None
        for x in range(0, len(blocks[start + 1]['lines'])): veh_list.append(
            blocks[start + 1]['lines'][x]['spans'][0]['text'])
        veh_list = [x for x in veh_list if "Veh" in x]
        driver_info_dict['Vehicles'] = veh_list

        for x in range(0, len(blocks[start + 2]['lines'])): drv_list.append(
            blocks[start + 2]['lines'][x]['spans'][0]['text'])
        drv_list = [x for x in drv_list if "Drv" in x]
        driver_info_dict['Drivers'] = drv_list

        l = max(len(drv_list), len(veh_list))
        for x in range(1, l + 1): driver_info.append(
            blocks[block_dict['Driver Information']]['lines'][x]['spans'][0]['text'])
        driver_info_dict['Driver Information'] = driver_info

        for x in range(1, l + 1): driver_dob.append(blocks[block_dict['Driver DOB']]['lines'][x]['spans'][0]['text'])
        driver_info_dict['Driver DOB'] = driver_dob

        for x in range(1, l + 1): fr_filing.append(blocks[block_dict['FR Filing']]['lines'][x]['spans'][0]['text'])
        driver_info_dict['FR Filing'] = fr_filing
        v = len(veh_list)
        if 'Comprehensive Deductible' in block_dict.keys():
            for x in range(1, l + 1): comp_deductible.append(
                blocks[block_dict['Comprehensive Deductible']]['lines'][x]['spans'][0]['text'])
        driver_info_dict['Comprehensive Deductible'] = comp_deductible

        if 'Collision Deductible' in block_dict.keys():
            for x in range(1, l + 1): coll_deductible.append(
                blocks[block_dict['Collision Deductible']]['lines'][x]['spans'][0]['text'])
        driver_info_dict['Collision Deductible'] = coll_deductible

        if 'Liability BI' in block_dict.keys():
            liability_bi = blocks[block_dict['Liability BI']]['lines'][1]['spans'][0]['text']
        driver_info_dict['Liability BI'] = str(liability_bi)

        if 'Liability PD' in block_dict.keys():
            liability_pd = int(blocks[block_dict['Liability PD']]['lines'][1]['spans'][0]['text'])
        driver_info_dict['Liability PD'] = liability_pd

        if 'Uninsured BI' in block_dict.keys():
            uni_bi = blocks[block_dict['Uninsured BI']]['lines'][1]['spans'][0]['text']
            temp = blocks[block_dict['Uninsured BI'] + 1]['lines'][0]['spans'][0]['text'].split(' ')
            if 'Unins PD/Coll Ded Waiver' in block_dict.keys():
                uni_pd = blocks[block_dict['Unins PD/Coll Ded Waiver']]['lines'][2]['spans'][0]['text']
            elif 'Unins PD/Coll Ded' in block_dict.keys():
                uni_pd = blocks[block_dict['Unins PD/Coll Ded']]['lines'][2]['spans'][0]['text']

            elif len(temp) == 5:
                uni_pd = temp[-1]
        driver_info_dict['Uninsured BI'] = uni_bi
        driver_info_dict['Unins PD/Coll Ded Wavier'] = uni_pd
        annual_miles_driven = []

        block_num = 0
        line_num = 0
        v = max(len(veh_list), len(drv_list))
        vehicle = []
        vehicle_information = []
        if blocks[block_num + 1]['type'] == 0:
            if 'Vehicle Information' in block_dict.keys():
                block_num = block_dict['Vehicle Information']

                for i in range(block_num + 2, block_num + len(veh_list) + 2):
                    list = []
                    for j in range(0, len(blocks[i]['lines'])):
                        list.append(blocks[i]['lines'][j]['spans'][0]['text'])
                    vehicle.append(list)
                if vehicle:
                    for list in vehicle:
                        if len(list[2]) > 1:
                            x = list[1].split(' ')
                            list[1:2] = x
                        vehicle_information.append(list)
            else:
                word_list = ['Veh']
                end = len(blocks)
                block_dict = self.check_blocks(blocks, word_list, end)
                if 'Veh' in block_dict.keys():
                    for i in range(block_dict['Veh'] + 1, block_dict['Veh'] + len(veh_list) + 1):
                        temp_list = []
                        for j in range(0, len(blocks[i]['lines'])):
                            temp_list.append(blocks[i]['lines'][j]['spans'][0]['text'])
                        vehicle.append(temp_list)
                    if vehicle:
                        for temp_list in vehicle:
                            if len(temp_list[2]) > 1:
                                x = temp_list[1].split(' ')
                                temp_list[1:2] = x
                            vehicle_information.append(temp_list)
        page = doc[0]
        blocks = page.getText('dict')['blocks']
        for i in range(0, len(blocks)):
            if blocks[i]['type'] == 0:
                if len(blocks[i]['lines']) > 2:
                    temp = [x for x in range(0, len(blocks[i]['lines'])) if
                            blocks[i]['lines'][x]['spans'][0]['text'] == 'Annual Miles Driven']
                    if len(temp) > 0:
                        block_num = i
                        line_num = temp[0]
                        for x in range(temp[0] + 1, temp[0] + v + 1):
                            annual_miles_driven.append(blocks[block_num]['lines'][x]['spans'][0]['text'])
                        break
        if not annual_miles_driven:
            page = doc[1]
            blocks = page.getText('dict')['blocks']
            for i in range(0, len(blocks)):
                if blocks[i]['type'] == 0:
                    if len(blocks[i]['lines']) > 2:
                        temp = [x for x in range(0, len(blocks[i]['lines'])) if
                                blocks[i]['lines'][x]['spans'][0]['text'] == 'Annual Miles Driven']
                        if len(temp) > 0:
                            block_num = i
                            line_num = temp[0]
                            for x in range(temp[0] + 1, temp[0] + v + 1):
                                annual_miles_driven.append(blocks[block_num]['lines'][x]['spans'][0]['text'])
                            break
            word_list = ['Vehicle Information', 'Vehicle Attributes', 'Veh']
            end = len(blocks)
            block_dict = self.check_blocks(blocks, word_list, end)
            if block_dict:
                if 'Veh' in block_dict.keys() and 'Vehicle Attributes' in block_dict.keys():
                    veh = block_dict['Veh']
                    end = block_dict['Vehicle Attributes']
                    vehicle = []
                    for i in range(veh + 1, end):
                        temp_list = []
                        for j in range(0, len(blocks[i]['lines'])):
                            temp_list.append(blocks[i]['lines'][j]['spans'][0]['text'])
                        vehicle.append(temp_list)
                    if vehicle:
                        for temp_list in vehicle:
                            if len(temp_list[2]) > 1:
                                x = temp_list[1].split(' ')
                                temp_list[1:2] = x
                            vehicle_information.append(temp_list)

                elif 'Vehicle Attributes' in block_dict.keys():
                    end = block_dict['Vehicle Attributes']
                    for i in range(end - v + 1, end):
                        temp_list = []
                        for j in range(0, len(blocks[i]['lines'])):
                            temp_list.append(blocks[i]['lines'][j]['spans'][0]['text'])
                        vehicle.append(temp_list)
                    if vehicle:
                        for temp_list in vehicle:
                            if len(temp_list[2]) > 1:
                                x = temp_list[1].split(' ')
                                temp_list[1:2] = x
                            vehicle_information.append(temp_list)

        vehicle_info_dict['Annual Miles Driven'] = annual_miles_driven
        vehicle_info_dict['Vehicle Information'] = vehicle_information

        driver_attribute_dict = {}
        months_mvr_exp_us = []
        months_foreign_license = []
        word_list = ['Months MVR Experience U.S.', 'Months Foreign License']
        for page in doc:
            if not months_mvr_exp_us or not months_foreign_license:
                blocks = page.getText('dict')['blocks']
                block_dict = self.check_blocks(blocks, word_list, end=len(blocks))
                if 'Months MVR Experience U.S.' in block_dict.keys() or 'Months Foreign License' in block_dict.keys():
                    if 'Months MVR Experience U.S.' in block_dict.keys():
                        for x in range(1, len(drv_list) + 1):
                            months_mvr_exp_us.append(
                                blocks[block_dict['Months MVR Experience U.S.']]['lines'][x]['spans'][0]['text'])
                    if 'Months Foreign License' in block_dict.keys():
                        for x in range(1, len(drv_list) + 1):
                            months_foreign_license.append(
                                blocks[block_dict['Months Foreign License']]['lines'][x]['spans'][0]['text'])

        driver_attribute_dict['Months MVR Experience U.S.'] = months_mvr_exp_us
        driver_attribute_dict['Months Foreign License'] = months_foreign_license

        return driver_info_dict, vehicle_info_dict, driver_attribute_dict

    def get_driver_violations(self, doc):
        driver_violations_dict = {}
        count = 0
        list = ['Driver Violations', 'Driver Suspensions/Reinstatements']
        for page in doc:
            if not count:
                blocks = page.getText('dict')['blocks']
                block_dict = self.check_blocks(blocks, list, end=len(blocks))
                if 'Driver Violations' in block_dict.keys():
                    if blocks[block_dict['Driver Violations'] + 1]['lines'][0]['spans'][0]['text'] == 'None':
                        count = 0
                    else:
                        if blocks[block_dict['Driver Suspensions/Reinstatements']]:
                            for i in range(block_dict['Driver Violations'] + 2,
                                           block_dict['Driver Suspensions/Reinstatements']):
                                count = count + 1

        driver_violations_dict['Driver Violations'] = count
        return driver_violations_dict

    def get_excluded_driver(self, doc):
        driver_dict = {}
        excluded_driver_dict = {}
        v = []
        count = 0
        temp_list = []
        block_dict = {}
        word_list = ['Excluded Driver(s)']
        for page in doc:
            if not block_dict:
                blocks = page.getText('dict')['blocks']
                block_dict = self.check_blocks(blocks, word_list, end=len(blocks))
            if block_dict:
                break

        if block_dict:
            for i in range(block_dict['Excluded Driver(s)'] + 2, len(blocks) - 1):

                if blocks[i]['type'] == 0:
                    for x in range(0, len(blocks[i]['lines'])):
                        temp_list.append(blocks[i]['lines'][x]['spans'][0]['text'])
            if temp_list:
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
