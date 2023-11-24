class ITC_Type2:
    def check_blocks(self, blocks, word_list, s, e):
        block_dict = {}
        for i in range(s, e):
            if blocks[i]['type'] == 0:
                temp = blocks[i]['lines'][0]['spans'][0]['text'].split(' ')[0]
                if temp in word_list:
                    block_dict[temp] = i
        return block_dict

    def get_insured_and_agent_info(self, blocks):
        insured_list = ['Name', 'Address', 'City,']
        insured_name = []
        agent_name = []
        address = []
        insured_dict = {}
        agent_dict = {}
        zip_code = []
        block_dict = self.check_blocks(blocks, insured_list, 0, 7)
        if blocks[block_dict['Name']]:
            end = [x for x in range(1, len(blocks[block_dict['Name']]['lines'])) if
                   blocks[block_dict['Name']]['lines'][x]['spans'][0]['text'] == 'Name']
            for x in range(1, end[0]):
                insured_name.append(blocks[block_dict['Name']]['lines'][x]['spans'][0]['text'])
            insured_name = ' '.join(map(str, insured_name)).strip()
            if len(blocks[block_dict['Name']]['lines']) < 8:
                for x in range(end[0] + 1, len(blocks[block_dict['Name']]['lines'])):
                    agent_name.append(blocks[block_dict['Name']]['lines'][x]['spans'][0]['text'])
            else:
                temp = [x for x in range(end[0] + 1, len(blocks[block_dict['Name']]['lines'])) if
                        blocks[block_dict['Name']]['lines'][x]['spans'][0]['text'] == 'Address']
                for x in range(end[0] + 1, temp[0]):
                    agent_name.append(blocks[block_dict['Name']]['lines'][x]['spans'][0]['text'])
                end = []
                end = [x for x in range(temp[0], len(blocks[block_dict['Name']]['lines'])) if
                       blocks[block_dict['Name']]['lines'][x]['spans'][0]['text'] == 'Address']
                for x in range(end[0] + 1, end[1]):
                    address.append(blocks[block_dict['Name']]['lines'][x]['spans'][0]['text'])

        if 'Address' in block_dict.keys():
            end = []
            temp = blocks[block_dict['Address']]['lines'][0]['spans'][0]['text'].split(' ')
            if len(temp) > 1:
                if temp[0] == 'Address':
                    address = temp[1:]
            end = [x for x in range(1, len(blocks[block_dict['Address']]['lines'])) if
                   blocks[block_dict['Address']]['lines'][x]['spans'][0]['text'] == 'Address']
            for x in range(1, end[0]):
                address.append(blocks[block_dict['Address']]['lines'][x]['spans'][0]['text'])
            end = []
            end = [x for x in range(1, len(blocks[block_dict['Address']]['lines'])) if
                   blocks[block_dict['Address']]['lines'][x]['spans'][0]['text'] == 'City,' or
                   blocks[block_dict['Address']]['lines'][x]['spans'][0]['text'] == 'City, State']

            if end:
                if len(end) == 2:
                    for x in range(end[0] + 1, end[1]):
                        block = blocks[block_dict['Address']]
                        line = block['lines'][x]
                        for j, span in enumerate(line['spans']):
                            zip_code.append(span['text'])
                    if 'State ZIP ' in zip_code:
                        zip_code.remove('State ZIP ')
                    if 'ZIP' in zip_code:
                        zip_code.remove('ZIP')
                else:
                    for x in range(end[0], len(blocks[block_dict['Address'] + 1]['lines'])):
                        zip_code.append(blocks[block_dict['Address'] + 1]['lines'][x]['spans'][0]['text'])
            else:
                if blocks[block_dict['Address'] + 1]['lines'][0]['spans'][0]['text'] == 'City,':
                    if len(blocks[block_dict['Address'] + 1]['lines']) == 2:
                        end = []
                        end = [x for x in range(1, len(blocks[block_dict['Address'] + 2]['lines'])) if
                               blocks[block_dict['Address'] + 2]['lines'][x]['spans'][0]['text'] == 'State ZIP']

                        for x in range(0, end[0] - 1):
                            zip_code.append(blocks[block_dict['Address'] + 2]['lines'][x]['spans'][0]['text'])
                        if 'State ZIP ' in zip_code:
                            zip_code.remove('State ZIP ')
        agent_list = ['Work', 'Phone', 'Work Number']
        block_dict = self.check_blocks(blocks, agent_list, 0, 12)
        end = [x for x in range(1, len(blocks[block_dict['Work']]['lines'])) if
               blocks[block_dict['Work']]['lines'][x]['spans'][0]['text'] == 'Producer' or
               blocks[block_dict['Work']]['lines'][x]['spans'][0]['text'] == 'Producer Code']

        agent_dict['Producer Code'] = blocks[block_dict['Work']]['lines'][end[0] + 2]['spans'][0]['text']
        address = ' '.join(map(str, address)).strip()
        agent_name = ' '.join(map(str, agent_name)).strip()

        insured_dict['Insured Name'] = insured_name
        insured_dict['Insured Address'] = address
        agent_dict['Agent Name'] = agent_name
        insured_dict['City, State ZIP'] = ' '.join(map(str, zip_code)).strip()
        return insured_dict, agent_dict

    def get_company_info(self, blocks):
        text_list = ['Company', 'Policy', 'Rates']
        company_dict = {}
        try:
            block_dict = self.check_blocks(blocks, text_list, 5, 15)
            company_dict['Company'] = blocks[block_dict['Company']]['lines'][1]['spans'][0]['text']
            if 'Policy' in block_dict.keys():
                company_dict['Policy Term'] = blocks[block_dict['Policy']]['lines'][1]['spans'][0]['text']
            else:
                end = [x for x in range(1, len(blocks[block_dict['Rates']]['lines'])) if
                       blocks[block_dict['Rates']]['lines'][x]['spans'][0]['text'] == 'Policy Term']
                company_dict['Policy Term'] = blocks[block_dict['Rates']]['lines'][end[0]]['spans'][0]['text']
        except():
            block_dict = self.check_blocks(blocks, text_list, 5, 10)
            company_dict['Company'] = blocks[block_dict['Company']]['lines'][1]['spans'][0]['text']
            end = [x for x in range(1, len(blocks[block_dict['Company']]['lines'])) if
                   blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'] == 'Policy Term']
            company_dict['Policy Term'] = blocks[block_dict['Company']]['lines'][end[0] + 1]['spans'][0]['text']
        return company_dict

    def get_driver_and_vehicle_info(self, blocks, doc):
        text_list = ['Company', 'ITC', 'Liability', 'Total', 'Veh']
        driver_info_list = []
        block_dict = self.check_blocks(blocks, text_list, 5, len(blocks))
        driver_information_dict = {}
        vehicle_info_dict = {}
        driver_info = []
        driver_dob = []
        fr_filing = []
        liability_bi = []
        liability_pd = []
        uninsured_bi = []
        uninsured_pd = []
        comprehensive_deductible = []
        collision_deductible = []
        if 'ITC' in block_dict.keys():
            for x in range(0, len(blocks[block_dict['ITC'] - 1]['lines'])):
                driver_info_list.append(blocks[block_dict['ITC'] - 1]['lines'][x]['spans'][0]['text'])
            m = int(len(driver_info_list) / 2)
            veh_list = driver_info_list[:m]
            drv_list = driver_info_list[m:]
            veh_list = [x for x in veh_list if "Veh" in x]
            drv_list = [x for x in drv_list if "Drv" in x]

            l = max(len(veh_list), len(drv_list))
            drv_info = []
            dob = []
            fr = []
            comp_deductible = []
            coll_deductible = []

            drv_info = [x for x in range(1, len(blocks[block_dict['ITC']]['lines'])) if
                        blocks[block_dict['ITC']]['lines'][x]['spans'][0]['text'] == 'Driver Information']
            if drv_info:
                dob = [x for x in range(drv_info[0], len(blocks[block_dict['ITC']]['lines'])) if
                       blocks[block_dict['ITC']]['lines'][x]['spans'][0]['text'] == 'Driver DOB']

                for x in range(drv_info[0] + 1, drv_info[0] + l + 1): driver_info.append(
                    blocks[block_dict['ITC']]['lines'][x]['spans'][0]['text'])

                for x in range(dob[0] + 1, dob[0] + l + 1): driver_dob.append(
                    blocks[block_dict['ITC']]['lines'][x]['spans'][0]['text'])

                fr = [x for x in range(drv_info[0], len(blocks[block_dict['ITC']]['lines'])) if
                      blocks[block_dict['ITC']]['lines'][x]['spans'][0]['text'] == 'FR Filing']

                for x in range(fr[0] + 1, fr[0] + l + 1): fr_filing.append(
                    blocks[block_dict['ITC']]['lines'][x]['spans'][0]['text'])

                comp_deductible = [x for x in range(fr[0], len(blocks[block_dict['ITC']]['lines'])) if
                                   blocks[block_dict['ITC']]['lines'][x]['spans'][0][
                                       'text'] == 'Comprehensive Deductible']
                if comp_deductible:
                    for x in range(comp_deductible[0] + 1, comp_deductible[0] + l + 1): comprehensive_deductible.append(
                        blocks[block_dict['ITC']]['lines'][x]['spans'][0]['text'])

                coll_deductible = [x for x in range(fr[0], len(blocks[block_dict['ITC']]['lines'])) if
                                   blocks[block_dict['ITC']]['lines'][x]['spans'][0]['text'] == 'Collision Deductible']
                if coll_deductible:
                    for x in range(coll_deductible[0] + 1, coll_deductible[0] + l + 1): collision_deductible.append(
                        blocks[block_dict['ITC']]['lines'][x]['spans'][0]['text'])

                liBI = [x for x in range(0, len(blocks[block_dict['Liability']]['lines'])) if
                        blocks[block_dict['Liability']]['lines'][x]['spans'][0]['text'] == 'Liability BI']
                liability_bi = blocks[block_dict['Liability']]['lines'][liBI[0] + 1]['spans'][0]['text']

                liPD = [x for x in range(0, len(blocks[block_dict['Liability']]['lines'])) if
                        blocks[block_dict['Liability']]['lines'][x]['spans'][0]['text'] == 'Liability PD']

                liability_pd = blocks[block_dict['Liability']]['lines'][liPD[0] + 1]['spans'][0]['text']


        elif 'Company' in block_dict.keys():
            start = [x for x in range(1, len(blocks[block_dict['Company']]['lines'])) if
                     blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'] == 'Lead Source']
            if start:
                end = [x for x in range(start[0], len(blocks[block_dict['Company']]['lines'])) if
                       blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'] == 'ITC Transaction ID']
            for x in range(start[0] + 2, end[0]): driver_info_list.append(
                blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'])
            m = int(len(driver_info_list) / 2)
            veh_list = driver_info_list[:m]
            drv_list = driver_info_list[m:]
            veh_list = [x for x in veh_list if "Veh" in x]
            drv_list = [x for x in drv_list if "Drv" in x]

            l = max(len(veh_list), len(drv_list))
            drv_info = []
            dob = []
            fr = []
            liBI = []
            liPD = []
            uni_bi = []
            uni_pd = []
            liability_pd = None
            drv_info = [x for x in range(1, len(blocks[block_dict['Company']]['lines'])) if
                        blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'] == 'Driver Information']
            if drv_info:
                dob = [x for x in range(drv_info[0], len(blocks[block_dict['Company']]['lines'])) if
                       blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'] == 'Driver DOB']

                for x in range(drv_info[0] + 1, drv_info[0] + l + 1): driver_info.append(
                    blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'])

                for x in range(dob[0] + 1, dob[0] + l + 1): driver_dob.append(
                    blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'])

                fr = [x for x in range(drv_info[0], len(blocks[block_dict['Company']]['lines'])) if
                      blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'] == 'FR Filing']

                for x in range(fr[0] + 1, fr[0] + l + 1): fr_filing.append(
                    blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'])

                comp_deductible = [x for x in range(drv_info[0], len(blocks[block_dict['Company']]['lines'])) if
                                   blocks[block_dict['Company']]['lines'][x]['spans'][0][
                                       'text'] == 'Comprehensive Deductible']
                if comp_deductible:
                    for x in range(comp_deductible[0] + 1, comp_deductible[0] + l + 1): comprehensive_deductible.append(
                        blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'])
                coll_deductible = [x for x in range(drv_info[0], len(blocks[block_dict['Company']]['lines'])) if
                                   blocks[block_dict['Company']]['lines'][x]['spans'][0][
                                       'text'] == 'Collision Deductible']
                if coll_deductible:
                    for x in range(coll_deductible[0] + 1, coll_deductible[0] + l + 1): collision_deductible.append(
                        blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'])

                liBI = [x for x in range(fr[0], len(blocks[block_dict['Company']]['lines'])) if
                        blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'] == 'Liability BI']
                liability_bi = blocks[block_dict['Company']]['lines'][liBI[0] + 1]['spans'][0]['text']

                liPD = [x for x in range(fr[0], len(blocks[block_dict['Company']]['lines'])) if
                        blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'] == 'Liability PD']

                liability_pd = blocks[block_dict['Company']]['lines'][liPD[0] + 1]['spans'][0]['text']

                uni_bi = [x for x in range(fr[0], len(blocks[block_dict['Company']]['lines'])) if
                          blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'] == 'Uninsured BI']
                if uni_bi:
                    uninsured_bi = blocks[block_dict['Company']]['lines'][uni_bi[0] + 1]['spans'][0]['text']

                uni_pd = [x for x in range(fr[0], len(blocks[block_dict['Company']]['lines'])) if
                          blocks[block_dict['Company']]['lines'][x]['spans'][0]['text'] == 'Unins PD/Coll Ded Waiver']
                if uni_pd:
                    uninsured_pd = blocks[block_dict['Company']]['lines'][uni_pd[0] + 1]['spans'][0]['text']
        driver_information_dict['Vehicles'] = veh_list
        driver_information_dict['Drivers'] = drv_list
        driver_information_dict['Driver Information'] = driver_info
        driver_information_dict['Driver DOB'] = driver_dob
        driver_information_dict['FR filing'] = fr_filing
        driver_information_dict['Liability BI'] = liability_bi
        driver_information_dict['Liability PD'] = liability_pd
        driver_information_dict['Comprehensive Deductible'] = comprehensive_deductible
        driver_information_dict['Collision Deductible'] = collision_deductible
        driver_information_dict['Uninsured BI'] = uninsured_bi
        driver_information_dict['Unins PD/Coll Ded Waiver'] = uninsured_pd
        veh = []
        vehicle_info = []
        if 'Total' in block_dict.keys():
            veh = [x for x in range(0, len(blocks[block_dict['Total']]['lines'])) if
                   blocks[block_dict['Total']]['lines'][x]['spans'][0]['text'] == 'Veh']
            veh_attribute = [x for x in range(0, len(blocks[block_dict['Total']]['lines'])) if
                             blocks[block_dict['Total']]['lines'][x]['spans'][0]['text'] == 'Vehicle Attributes']

            if veh and veh_attribute:
                for x in range(veh[0] + 5, veh_attribute[0]): vehicle_info.append(
                    blocks[block_dict['Total']]['lines'][x]['spans'][0]['text'])
            line = x
            veh_info = []
            for x in range(0, len(vehicle_info), 5):
                veh_info.append(vehicle_info[x:x + 5])

            annual_miles_driven = []
            v = max(len(veh_list), len(drv_list))
            page = doc[0]
            blocks = page.getText('dict')['blocks']
            annual_miles_driven = []
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
        if not vehicle_info:
            page = doc[1]
            block1 = page.getText('dict')['blocks']
            blocks = block1
            block_end = []
            block_start = []
            vehicle = []
            for i in range(0, len(blocks)):
                if blocks[i]['type'] == 0:
                    if len(blocks[i]['lines']) > 2:
                        temp = [x for x in range(0, len(blocks[i]['lines'])) if
                                blocks[i]['lines'][x]['spans'][0]['text'] == 'Vehicle Information']
                        if len(temp) > 0:
                            block_start = i
                            line1 = temp[0]
            for i in range(0, len(blocks)):
                if blocks[i]['type'] == 0:
                    if len(blocks[i]['lines']) > 2:
                        temp = [x for x in range(0, len(blocks[i]['lines'])) if
                                blocks[i]['lines'][x]['spans'][0]['text'] == 'Vehicle Attributes']
                        if len(temp) > 0:
                            block_end = i
                            line2 = temp[0]
            if not block_end:
                block_end = block_start + v
            for i in range(block_start + 1, block_end):
                temp = []
                for x in range(0, len(blocks[i]['lines'])):
                    temp.append(blocks[i]['lines'][x]['spans'][0]['text'])
                vehicle.append(temp)

            if vehicle:
                for temp_list in vehicle:
                    if len(temp_list[2]) > 1:
                        x = temp_list[1].split(' ')
                        temp_list[1:2] = x
                    vehicle_info.append(temp_list)

        vehicle_info_dict['Annual miles'] = annual_miles_driven
        vehicle_info_dict['Vehicle Info'] = vehicle_info
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

        return driver_information_dict, vehicle_info_dict, driver_attribute_dict

    def get_driver_violations(self, doc):
        driver_violations_dict = {}
        block_dict = {}
        line_dict = {}
        count = 0
        violations = []
        start = []
        end = []
        word_list = ['Driver Violations', 'Driver Suspensions/Reinstatements']
        for page in doc:
            if not count:
                blocks = page.getText('dict')['blocks']
                for i in range(0, len(blocks)):
                    if blocks[i]['type'] == 0:
                        if len(blocks[i]['lines']) > 2:
                            for x in range(0, len(blocks[i]['lines'])):
                                temp = blocks[i]['lines'][x]['spans'][0]['text']
                                if temp in word_list:
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
