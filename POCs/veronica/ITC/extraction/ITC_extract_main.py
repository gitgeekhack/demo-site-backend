import fitz
from extract_type1 import ITC_Type1
from extract_type2 import ITC_Type2
from extract_type3 import ITC_Type3
from extract_type4 import ITC_Type4
import time

start = time.time()
path = 'D:/Office/veronica-self/ITC/out/address big box_type4/out_ITC_Alex Zuniga.pdf.pdf'

doc = fitz.open(path)
page = doc[0]
blocks = page.getText("dict")['blocks']

length_blocks = len(blocks)


def read_from_dictionary(dictionary):
    for key, value in dictionary.items():
        if not value:
            value = None
        if isinstance(value, list):
            value = [i for i in value if i != '\xa0']
        print(key, ": ", value)


if 5 < length_blocks < 9:
    type1 = ITC_Type1()
    i = type1.check_blocks(blocks)
    print("\n----INSURED INFO-----")
    insured_info = type1.get_insured_info(blocks, i)
    read_from_dictionary(insured_info)
    print("\n----AGENT INFO-----")
    agent_info = type1.get_agent_info(blocks, i)
    read_from_dictionary(agent_info)
    print("\n----COMPANY INFO----")
    company_info = type1.get_company_info(blocks, i)
    read_from_dictionary(company_info)
    driver_info, vehicle_info, driver_attribute = type1.get_driver_and_vehicle_info(blocks, i, doc)
    print("\n----Driver INFO----")
    read_from_dictionary(driver_info)
    print("\n----Vehicle INFO----")
    read_from_dictionary(vehicle_info)
    print("\n----Driver Attribute----")
    read_from_dictionary(driver_attribute)
    driver_violations = type1.get_driver_violations(doc)
    print("\n----Driver Violations----")
    read_from_dictionary(driver_violations)
    print("\n----Excluded Driver(s)----")
    excluded_driver = type1.get_excluded_driver(doc)
    read_from_dictionary(excluded_driver)
    print("------------------------------------------------------------")
elif length_blocks == 17:
    type2 = ITC_Type2()
    blocks = page.getText("dict")['blocks']
    insured_info, agent_info = type2.get_insured_and_agent_info(blocks)
    print("\n----Insured INFO-----")
    read_from_dictionary(insured_info)
    print("\n----Agent INFO----")
    read_from_dictionary(agent_info)
    print("\n----Company INFO----")
    company_info = type2.get_company_info(blocks)
    read_from_dictionary(company_info)
    driver_info, vehicle_info, driver_attribute = type2.get_driver_and_vehicle_info(blocks, doc)
    print("\n----Driver INFO----")
    read_from_dictionary(driver_info)
    print("\n----Vehicle INFO----")
    read_from_dictionary(vehicle_info)
    print("\n----Driver Attribute----")
    read_from_dictionary(driver_attribute)
    driver_violations = type2.get_driver_violations(doc)
    print("\n----Driver Violations----")
    read_from_dictionary(driver_violations)
    print("\n----Excluded Driver(s)----")
    excluded_driver = type2.get_excluded_driver(doc)
    read_from_dictionary(excluded_driver)
    print("------------------------------------------------------------")
elif 11 <= length_blocks < 25:
    type4 = ITC_Type4()
    blocks = page.getText("dict")['blocks']
    insured_info, agent_info = type4.get_insured_and_agent_info(blocks)
    print("\n----Insured INFO-----")
    read_from_dictionary(insured_info)
    print("\n----Agent INFO----")
    read_from_dictionary(agent_info)
    print("\n----Company INFO----")
    company_info = type4.get_company_info(blocks)
    read_from_dictionary(company_info)
    driver_info, vehicle_info, driver_attribute = type4.get_driver_and_vehicle_info(blocks, doc)
    print("\n----Driver INFO----")
    read_from_dictionary(driver_info)
    print("\n----Vehicle INFO----")
    read_from_dictionary(vehicle_info)
    print("\n----Driver Attribute----")
    read_from_dictionary(driver_attribute)
    driver_violations = type4.get_driver_violations(doc)
    print("\n----Driver Violations----")
    read_from_dictionary(driver_violations)
    print("\n----Excluded Driver(s)----")
    excluded_driver = type4.get_excluded_driver(doc)
    read_from_dictionary(excluded_driver)
    print("------------------------------------------------------------")
elif length_blocks >= 40:
    type3 = ITC_Type3()
    blocks = page.getText("dict")['blocks']
    word_list = ['Name', 'Address', 'Phone Number', 'Phone', 'Phone Number ( ) -', 'Work', 'Work Number', 'Company',
                 'Policy Term', 'Quote By', 'Driver Information', 'Driver DOB', 'FR Filing',
                 'Comprehensive Deductible',
                 'Collision Deductible', 'Liability BI', 'Liability PD', 'Uninsured BI', 'Unins PD/Coll Ded',
                 'Unins PD/Coll Ded Waiver']
    block_dict = type3.check_blocks(blocks, word_list)
    print("----Insured INFO-----")
    insured_info, agent_info = type3.get_insured_and_agent_info(blocks, block_dict)

    read_from_dictionary(insured_info)
    print("\n----Agent INFO-----")
    read_from_dictionary(agent_info)
    print("\n----Company INFO-----")
    company_info = type3.get_company_info(blocks, block_dict)
    read_from_dictionary(company_info)
    driver_info, vehicle_info, driver_attribute = type3.get_driver_and_vehicle_info(blocks, block_dict, doc)
    print("\n----Driver INFO----")
    read_from_dictionary(driver_info)
    print("\n----Vehicle INFO----")
    read_from_dictionary(vehicle_info)
    print("\n----Driver Attribute----")
    read_from_dictionary(driver_attribute)
    driver_violations = type3.get_driver_violations(doc)
    print("\n----Driver Violations----")
    read_from_dictionary(driver_violations)
    print("\n----Excluded Driver(s)----")
    excluded_driver = type3.get_excluded_driver(doc)
    read_from_dictionary(excluded_driver)
    print("------------------------------------------------------------")
else:
    print("ERROR: INCORRECT PDF TYPE")

end = time.time()

print(f"Runtime of the program is {end - start}")
