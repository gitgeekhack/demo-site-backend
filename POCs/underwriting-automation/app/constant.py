from enum import Enum

CLIENT_MAX_SIZE = 4096 * 4096
SRC_INSURANCE_APPLICATION = 'insurance-application'
SRC_CRM_RECEIPT = 'crm-receipt'
SRC_ITC = 'itc'
SRC_DRIVING_LICENSE = 'driving-license'
SRC_BROKER_PACKAGE = 'broker-package'
SRC_MVR = 'mvr'
SRC_ARTISAN_USE_LETTER = 'artisan-use-letter'
SRC_VR = 'vr'
SRC_EFT = 'eft'
SRC_NON_OWNERS_LETTER = 'non-owners-letter'
SRC_REGISTRATION = 'registration'
SRC_STRIPE_RECEIPT = 'stripe-receipt'
SRC_PTP = 'promise-to-provide'

TRG_INS_APP = 'insurance_application'
TRG_CRM_RECEIPT = 'crm_receipt'
TRG_ITC = 'itc'
TRG_DRIVING_LICENSE = 'driving_license'
TRG_PUL = 'pleasure_use_letter'
TRG_MVR = 'mvr'
TRG_BROKER_PACKAGE = 'broker_package'
TRG_AUL = 'artisan_use_letter'
TRG_VR = 'vr'
TRG_EFT = 'eft'
TRG_NOL = 'non_owners_letter'
TRG_REGISTRATION = 'registration'
TRG_STRIPE_RECEIPT = 'stripe_receipt'
TRG_PTP = 'promise_to_provide'

ISO_DATE_FORMAT = '%Y-%m-%d'

TRG_AGREED_TO_PAY = 'agreed_to_pay_date'
TRG_PROMISE_TO_PROVIDE = 'promise_to_provide_date'


class Endpoints:
    PINGER = '/ping'
    DOWNLOADER = '/download/{file_name:.*}'

    class API:
        class V1:
            class CRMReceipt:
                EXTRACT = '/api/v1/crm-receipt/extract'

            class ITC:
                EXTRACT = '/api/v1/itc/extract'

            class DrivingLicense:
                EXTRACT = '/api/v1/driving-license/extract'

            class Application:
                VERIFY = '/api/v1/insurance-application/verify'
                EXTRACT = '/api/v1/insurance-application/extract'

            class MVR:
                EXTRACT = '/api/v1/mvr/extract'

            class BrokerPackage:
                EXTRACT = '/api/v1/broker-package/extract'

            class PleasureUseLetter:
                EXTRACT = '/api/v1/pleasure-use-letter/extract'

            class SamePersonStatement:
                EXTRACT = '/api/v1/same-person/extract'

            class PromiseToProvide:
                EXTRACT = '/api/v1/promise-to-provide/extract'

            class StripeReceipt:
                EXTRACT = '/api/v1/stripe-receipt/extract'

            class VR:
                EXTRACT = '/api/v1/vr/extract'

            class Registration:
                EXTRACT = '/api/v1/registration/extract'

            class EFT:
                EXTRACT = '/api/v1/eft/extract'

            class ArtisanUseLetter:
                EXTRACT = '/api/v1/artisan-use-letter/extract'

            class NonOwnersLetter:
                EXTRACT = '/api/v1/non-owners-letter/extract'


class InsuranceCompany(Enum):
    ALLIANCE_UNITED = 'alliance-united'

    @classmethod
    def items(cls):
        return list(map(lambda c: c.value, cls))


class CRMDocumentTemplate:
    class Key:
        PAYMENT_DATE = 'Invoice Date:'
        REFERENCE_NUMBER = 'Ref Num:'
        AMOUNTS_BILLED = 'Amounts Billed'
        AMOUNT_DUE = 'Amount Due'
        VR_FEE = 'VR FEE'
        NB_EFT_TO_COMPANY = 'NB EFT TO COMPANY'
        TOTAL = 'Total'
        POLICY_NUMBER = 'Policy Number'
        LINE_OF_BUSINESS = 'Line Of Business'
        AMOUNT_PAID = 'Amount Paid'
        TOTALS_SUMMARIES = 'Totals - Summaries'
        PAYMENT_METHOD = 'Payment Method: '
        PAYMENT_NOTES = 'Payment Notes'

    class Block:
        PAYMENT_DATE = 4
        NAME = 6
        ADDRESS = [7, 8]
        PAYMENT_NOTES = [-2, -1]
        PAYMENT_METHOD = [-3]


class ITCDocumentTemplate:
    ATTRIBUTE_LABEL_LENGTH = 17
    NO_BREAK_SPACE = '\xa0'
    NO_BREAK_SPACE_REPLACEMENT = 'None'

    class RegexCollection:
        ZIPCODE_REGEX = r'\d{5}(-\d{4})?$'
        DIGIT_FROM_STRING_REGEX = r'[0-9]{1}'
        EXCLUDED_DRIVER = '[a-zA-Z]{2,15}\s{1}[a-zA-Z]{1,15}\s{1}[a-zA-Z]{0,15}\s{0,1}\d{1,2}[/]{1}\d{1,2}[/]{1}\d{4}\s{1}[A-Z]{1}\s{1}[A-Z]{1}\s{1}[A-Z]{1}\s{1}'
        EXCLUDED_DOB = '\d{1,2}[/]{1}\d{1,2}[/]{1}\d{4}'
        EXCLUDED_OTHER = '[A-Z]{1}\s{1}[A-Z]{1}\s{1}[A-Z]{1}\s{1}'
        VEHICLE_ID = '\s{1}\d{1}\s{1}'
        VEHICLE_VIN = '\w{17}\s{1}'
        VEHICLE_YEAR = '\d{4}'
        VEH_LIST = 'Veh\s{1}\d{1}'
        DRV_LIST = 'Drv\s{1}\d{1}'
        SINGLE_DIGIT = '[0-9]{1}'

    class Key:
        NAME = 'Name'
        DRIVER_SUSPENSIONS = 'Driver Suspensions/Reinstatements'
        EXCLUDED_DRIVERS = 'Excluded Driver(s)'
        RELATIONSHIP = 'Relationship'
        CITY_STATE_ZIP = 'City, State ZIP'
        COMPANY = 'Company'
        POLICY_TERM = 'Policy Term'
        POLICY_TIER = 'Policy Tier'
        DRIVER_INFORMATION = 'Driver Information'
        DRIVER_DOB = 'Driver DOB'
        FR_FILING = 'FR Filing'
        COMPREHENSIVE_DEDUCTIBLE = 'Comprehensive Deductible'
        COLLISION_DEDUCTIBLE = 'Collision Deductible'
        LIABILITY_BI = 'Liability BI'
        LIABILITY_PD = 'Liability PD'
        UNINSURED_BI = 'Uninsured BI'
        UNINSURED_PD = 'Unins PD/Coll Ded Waiver'
        VEHICLE_INFORMATION = 'Vehicle Information'
        VEHICLE_ATTRIBUTES = 'Vehicle Attributes'
        ANNUAL_MILES_DRIVEN = 'Annual Miles Driven'
        MONTHS_FOREIGN_LICENSE = 'Months Foreign License'
        MONTHS_MVR_US = 'Months MVR Experience U.S.'
        VEHICLE = 'Veh'
        DRIVER = 'Drv'
        ADDRESS = 'Address'
        PHONE = 'Phone'
        PRODUCER_CODE = 'Producer Code'
        ITC_TRANSACTION_ID = 'ITC Transaction ID'
        NONE = 'None'
        AMT_2 = 'Amt 2'
        DRIVER_ATTRIBUTES = 'Driver Attributes'
        INDUSTRY = 'Industry'

        VEH1 = 'Veh 1'
        LEAD_SOURCE = 'Lead Source'
        INSURED_INFO = 'Insured Information'
        COMPANY_QUESTIONS = 'Company Questions'
        QUOTE_NUMBER = 'Quote Number'
        QUOTE_DATE_TIME = 'Quote Date/Time'
        VEHICLE_INFO_LABELS = 'Veh VIN Make Model Year'
        TITLES = [VEHICLE, DRIVER, DRIVER_DOB, ITC_TRANSACTION_ID, DRIVER_INFORMATION, LIABILITY_BI, LIABILITY_PD,
                  UNINSURED_BI, UNINSURED_PD, RELATIONSHIP, MONTHS_FOREIGN_LICENSE, MONTHS_MVR_US, FR_FILING, COMPANY,
                  QUOTE_DATE_TIME, POLICY_TERM, POLICY_TIER, NAME, ADDRESS, CITY_STATE_ZIP, PRODUCER_CODE, PHONE,
                  QUOTE_NUMBER, VEHICLE_INFO_LABELS, VEHICLE_ATTRIBUTES, ANNUAL_MILES_DRIVEN, COLLISION_DEDUCTIBLE,
                  COMPREHENSIVE_DEDUCTIBLE, VEHICLE, DRIVER, ITC_TRANSACTION_ID]

    class ResponseKey:
        INSURED_INFORMATION = 'insured_information'
        AGENT_INFORMATION = 'agent_information'
        INSURANCE_COMPANY = 'insurance_company'
        DRIVER_INFORMATION = 'driver_information'
        VEHICLE_INFORMATION = 'vehicle_information'
        SIGNATURES = 'signature'


class Section:
    class Application:
        class AllianceUnited:
            THIRD_PARTY_DESIGNATION = 'Third Party Designation'
            DISCLOSURE_OF_ALL_HOUSEHOLD = 'Disclosure of All Household Members, Children Away From Home, Other Drivers, Registered Owners,'
            REJECTION_BI_COVERAGE = 'Rejection of Uninsured/Underinsured Motorist Bodily Injury Coverage'
            REJECTION_PD_COVERAGE = 'Rejection of Uninsured Motorist Property Damage Coverage'
            STATEMENT_OF_VEH_CONDITION_CERTIFICATE = 'Statement of Vehicle Condition Certification'
            ACKNOWLEDGEMENTS_BY_APPLICANT = 'Acknowledgements by Applicant'
            ACKNOWLEDGEMENT_PROGRAM_OFFERED = 'Acknowledgment of Programs Offered'
            NAMED_DRIVER_EXCLUSION = 'Named Driver Exclusion'
            CALIFORNIA_NO_FAULT_ACCIDENT_DECLARATION = 'CALIFORNIA NO-FAULT ACCIDENT DECLARATION'
            NOT_AN_INSURANCE_CONTRACT = 'This Is Not An Insurance Contract'
            CONSUMER_DISCLOSURE = 'AT FAULT CONSUMER DISCLOSURE'
            NON_OWNED_VEHICLE_COVERAGE_ENDORSEMENT = 'Named Non-Owned Vehicle Coverage Endorsement'
            CANCELLATION_REQUEST_POLICY = 'CANCELLATION REQUEST / POLICY RELEASE'


class APPDocumentTemplate:
    class AllianceUnited:
        VALID_DOCUMENT_KEY = 'Alliance United Insurance Services, LLC'

        class RegexCollection:
            ZIPCODE_REGEX = r'\d{5}(-\d{4})?$'
            DATE_REGEX = r'\d{2}/\d{2}/\d{4}'
            VEHICLE_INFO_SYMBOL_REGEX_1 = r'\w{2}-\w{2}-\w{2}-\w{2}'
            VEHICLE_INFO_SYMBOL_REGEX_2 = r'\w{2}-\w{2}--'

        class Key:
            COMPREHENSIVE_DEDUCTIBLE = 'Comprehensive * ACV Less Deductible of'
            COLLISION_DEDUCTIBLE = 'Collison * ACV Less Deductible of'
            LIABILITY_TO_OTHERS = 'Liability to Others:'
            UMPD = 'Uninsured Motorist Property Damage [UMPD]'
            UMBI = 'Uninsured/Underinsured Motorist Bodily Injury [UMBI]'
            INSURED = 'Insured'
            DRIVERS = 'Drivers'
            DRIVING = 'Driving'
            BROKER = 'Broker'
            POLICY = 'Policy'
            NET = 'Net'
            APPLICATION_FOR = 'Application for '
            APPLICATION = 'Application'
            EFFECTIVE = 'EFFECTIVE'
            LOSS = 'Loss'
            VEHICLE = 'Vehicle'
            NON = 'NON'
            NAMED_INSURED = 'Named Insured'
            NO_COVERAGE = 'No Coverage'
            NA = 'n/a'
            EXCLU = 'EXCLU'
            CANCELLATION_REQUEST_POLICY_ATTACHED = 'CANCELLATION REQUEST (Policy attached)'
            FOR_AGENCY_COMPANY_USE = 'FOR AGENCY / COMPANY USE'

            class SignatureVerification:
                SECTIONS = Section.Application.AllianceUnited
                THIRD_PARTY_DESIGNATION_RESPONSE_KEY = 'third_party_designation'
                DISCLOSURE_OF_ALL_HOUSEHOLD_KEY = 'disclosure_of_all_household_members'
                REJECTION_BI_COVERAGE_KEY = 'rejection_of_bi_coverage'
                REJECTION_PD_COVERAGE_KEY = 'rejection_of_pd_coverage'
                STATEMENT_OF_VEH_CONDITION_CERTIFICATE_KEY = 'vehicle_condition_certification'
                ACKNOWLEDGEMENTS_BY_APPLICANT_KEY = 'acknowledgements_by_applicant'
                ACKNOWLEDGEMENT_PROGRAM_OFFERED_KEY = 'acknowledgement_of_programs_offered'
                NAMED_DRIVER_EXCLUSION_KEY = 'named_driver_exclusion'
                CALIFORNIA_NO_FAULT_ACCIDENT_DECLARATION_KEY = 'no_fault_accident_declaration'
                NOT_AN_INSURANCE_CONTRACT_KEY = 'not_insurance_contract'
                CONSUMER_DISCLOSURE_KEY = 'consumer_disclosure'
                NON_OWNED_VEHICLE_COVERAGE_ENDORSEMENT_KEY = 'non_owned_vehicle_coverage_endorsement'
                CANCELLATION_REQUEST_POLICY_KEY = 'cancellation_request'
                ALLOWED_SECTIONS = [SECTIONS.THIRD_PARTY_DESIGNATION, SECTIONS.DISCLOSURE_OF_ALL_HOUSEHOLD,
                                    SECTIONS.REJECTION_BI_COVERAGE, SECTIONS.REJECTION_PD_COVERAGE,
                                    SECTIONS.STATEMENT_OF_VEH_CONDITION_CERTIFICATE,
                                    SECTIONS.ACKNOWLEDGEMENTS_BY_APPLICANT, SECTIONS.ACKNOWLEDGEMENT_PROGRAM_OFFERED,
                                    SECTIONS.NAMED_DRIVER_EXCLUSION, SECTIONS.CALIFORNIA_NO_FAULT_ACCIDENT_DECLARATION,
                                    SECTIONS.NOT_AN_INSURANCE_CONTRACT, SECTIONS.CONSUMER_DISCLOSURE,
                                    SECTIONS.NON_OWNED_VEHICLE_COVERAGE_ENDORSEMENT]
                SECTIONS_RESPONSE_KEY = [THIRD_PARTY_DESIGNATION_RESPONSE_KEY, DISCLOSURE_OF_ALL_HOUSEHOLD_KEY,
                                         REJECTION_BI_COVERAGE_KEY, REJECTION_PD_COVERAGE_KEY,
                                         STATEMENT_OF_VEH_CONDITION_CERTIFICATE_KEY, ACKNOWLEDGEMENTS_BY_APPLICANT_KEY,
                                         ACKNOWLEDGEMENT_PROGRAM_OFFERED_KEY, NAMED_DRIVER_EXCLUSION_KEY,
                                         CALIFORNIA_NO_FAULT_ACCIDENT_DECLARATION_KEY, NOT_AN_INSURANCE_CONTRACT_KEY,
                                         CONSUMER_DISCLOSURE_KEY, NON_OWNED_VEHICLE_COVERAGE_ENDORSEMENT_KEY,
                                         CANCELLATION_REQUEST_POLICY_KEY]
                SIGNATURE_LABELS = ['Signature of Named Insured', 'Signature', 'Applicant’s Signature',
                                    'Member Signature', 'SIGNATURE OF NAMED INSURED']
                DATE_LABELS = ['Date', 'DATE']
                SIGN_VERIFICATION_STARTING_PAGE_NO = 4
                MULTIPLE_DATES_SECTION = [SECTIONS.NAMED_DRIVER_EXCLUSION,
                                          SECTIONS.CALIFORNIA_NO_FAULT_ACCIDENT_DECLARATION,
                                          SECTIONS.NOT_AN_INSURANCE_CONTRACT, SECTIONS.CONSUMER_DISCLOSURE]
                KEYS = {SECTIONS.THIRD_PARTY_DESIGNATION: THIRD_PARTY_DESIGNATION_RESPONSE_KEY,
                        SECTIONS.DISCLOSURE_OF_ALL_HOUSEHOLD: DISCLOSURE_OF_ALL_HOUSEHOLD_KEY,
                        SECTIONS.REJECTION_BI_COVERAGE: REJECTION_BI_COVERAGE_KEY,
                        SECTIONS.REJECTION_PD_COVERAGE: REJECTION_PD_COVERAGE_KEY,
                        SECTIONS.STATEMENT_OF_VEH_CONDITION_CERTIFICATE: STATEMENT_OF_VEH_CONDITION_CERTIFICATE_KEY,
                        SECTIONS.ACKNOWLEDGEMENTS_BY_APPLICANT: ACKNOWLEDGEMENTS_BY_APPLICANT_KEY,
                        SECTIONS.ACKNOWLEDGEMENT_PROGRAM_OFFERED: ACKNOWLEDGEMENT_PROGRAM_OFFERED_KEY,
                        SECTIONS.NAMED_DRIVER_EXCLUSION: NAMED_DRIVER_EXCLUSION_KEY,
                        SECTIONS.CALIFORNIA_NO_FAULT_ACCIDENT_DECLARATION: CALIFORNIA_NO_FAULT_ACCIDENT_DECLARATION_KEY,
                        SECTIONS.NOT_AN_INSURANCE_CONTRACT: NOT_AN_INSURANCE_CONTRACT_KEY,
                        SECTIONS.CONSUMER_DISCLOSURE: CONSUMER_DISCLOSURE_KEY,
                        SECTIONS.NON_OWNED_VEHICLE_COVERAGE_ENDORSEMENT: NON_OWNED_VEHICLE_COVERAGE_ENDORSEMENT_KEY,
                        SECTIONS.CANCELLATION_REQUEST_POLICY: CANCELLATION_REQUEST_POLICY_KEY}

        class Padding:
            class Signature:
                SECTIONS = Section.Application.AllianceUnited
                SECTION = {SECTIONS.THIRD_PARTY_DESIGNATION: (-0.03, -0.05, 0.17, 0.03),
                           SECTIONS.DISCLOSURE_OF_ALL_HOUSEHOLD: (-0.03, -0.05, 0.17, 0.03),
                           SECTIONS.REJECTION_BI_COVERAGE: (-0.03, -0.05, 0.17, 0.03),
                           SECTIONS.REJECTION_PD_COVERAGE: (-0.03, -0.05, 0.17, 0.03),
                           SECTIONS.STATEMENT_OF_VEH_CONDITION_CERTIFICATE: (-0.03, -0.06, 0.17, 0.005),
                           SECTIONS.ACKNOWLEDGEMENTS_BY_APPLICANT: (-0.03, -0.06, 0.17, 0.005),
                           SECTIONS.ACKNOWLEDGEMENT_PROGRAM_OFFERED: (-0.03, -0.05, 0.22, 0.005),
                           SECTIONS.NAMED_DRIVER_EXCLUSION: (-0.03, -0.06, 0.17, 0.005),
                           SECTIONS.CALIFORNIA_NO_FAULT_ACCIDENT_DECLARATION: (-0.10, -0.05, 0.10, 0.01),
                           SECTIONS.NOT_AN_INSURANCE_CONTRACT: (-0.09, -0.05, 0.13, 0.01),
                           SECTIONS.CONSUMER_DISCLOSURE: (-0.10, -0.05, 0.13, 0.01),
                           SECTIONS.NON_OWNED_VEHICLE_COVERAGE_ENDORSEMENT: (-0.015, -0.05, 0.18, 0.01),
                           SECTIONS.CANCELLATION_REQUEST_POLICY: (-0.025, -0.05, 0.065, 0.054)}

            class Date:
                SECTIONS = Section.Application.AllianceUnited
                SECTION = {SECTIONS.THIRD_PARTY_DESIGNATION: (-0.03, -0.04, 0.20, 0.03),
                           SECTIONS.DISCLOSURE_OF_ALL_HOUSEHOLD: (-0.03, -0.04, 0.20, 0.03),
                           SECTIONS.REJECTION_BI_COVERAGE: (-0.03, -0.04, 0.20, 0.03),
                           SECTIONS.REJECTION_PD_COVERAGE: (-0.03, -0.04, 0.20, 0.03),
                           SECTIONS.STATEMENT_OF_VEH_CONDITION_CERTIFICATE: (-0.03, -0.04, 0.20, 0.03),
                           SECTIONS.ACKNOWLEDGEMENTS_BY_APPLICANT: (-0.03, -0.04, 0.20, 0.03),
                           SECTIONS.ACKNOWLEDGEMENT_PROGRAM_OFFERED: (-0.03, -0.04, 0.24, 0.02),
                           SECTIONS.NAMED_DRIVER_EXCLUSION: (-0.03, -0.04, 0.20, 0.03),
                           SECTIONS.CALIFORNIA_NO_FAULT_ACCIDENT_DECLARATION: (-0.10, -0.05, 0.10, 0.01),
                           SECTIONS.NOT_AN_INSURANCE_CONTRACT: (-0.10, -0.05, 0.15, 0.01),
                           SECTIONS.CONSUMER_DISCLOSURE: (-0.10, -0.05, 0.11, 0.01),
                           SECTIONS.NON_OWNED_VEHICLE_COVERAGE_ENDORSEMENT: (-0.015, -0.05, 0.2, 0.01),
                           SECTIONS.CANCELLATION_REQUEST_POLICY: (-0.06, -0.05, 0.065, 0.054)}

        class Label:
            SIGNATURE = 'signature'
            DATE = 'date'


class VerificationTemplate:
    SORT_SIMILARITY_RATIO = 100
    SET_SIMILARITY_RATIO = 100
    SR_FILING = 'SR-22'
    LINE_OF_BUSINESS = {'Auto Insurance': 'Personal Auto'}  # mapping line of business in application to crm-receipt

    class Relationship:
        INSURED = ['Named Insured', 'Self']
        PARENT_CHILD = ['Mother', 'Father', 'Son', 'Daughter']
        SIGNIFICANT_OTHER = ['Significant Other', 'Spouse', 'Domestic Partner']
        OTHER_ALLOWED = ['Brother', 'Sister', 'Relative', 'Non-Relative', 'Aunt', 'Uncle', 'Granddaughter',
                         'Grandfather', 'Grandmother', 'Grandson', 'In-Law', 'Nephew', 'Niece', 'Other', 'EXCLU']

    class ResponseKey:
        PAYMENT_DATE = 'payment_date'
        DOWN_PAYMENT = 'down_payment'
        VR_FEE = 'vr_fee'
        BROKER_FEE = 'broker_fee'
        REFERENCE_NUMBER = 'reference_number'
        AMOUNT_PAID = 'amount_paid'
        PAYMENT_METHOD = 'payment_method'


class MVRDocumentTemplate:
    NAME = 'Name:'
    SEX = 'Sex:'
    WEIGHT = 'Weight:'
    AGE = 'Age:'
    DOB = 'DOB:'
    LICENSE = 'License:'
    LICENSE_AND_PERMIT = 'License and Permit Information'
    STATUS = 'Status:'
    NONE = 'NONE'
    VIOLATIONS = 'Violations/Convictions'
    SUSPENSIONS = 'Suspensions/Revocations'

    class Block:
        MINIMUM_LENGTH = 5

    class LicenseType:
        PERSONAL = 'PERSONAL'
        COMMERCIAL = 'COMMERCIAL'
        IDENTIFICATION = 'IDENTIFICATION'

    class RegexCollection:
        LICENSE = '(?<=License:\s)([\w\s]+)?(?=\n)'
        STATUS = '(?<=Status:\s)([\w\s]+)?(?=\n)'
        DATE_REGEX = r'\d{1,2}/\d{1,2}/\d{2,4}'


class BrokerPackageTemplate:
    VALID_BROKER_PACKAGE_TEMPLATE = 'I hereby request Veronica’s Insurance Services (“Broker”) assist me with applying for insurance'
    VALID_TYPE_2 = "VERONICA'S BROKER AGREEMENT"
    SPANISH_MONTHS = {'enero': 'january', 'febrero': 'february', 'marzo': 'march', 'abril': 'april', 'mayo': 'may',
                      'junio': 'june', 'julio': 'july', 'agosto': 'august', 'septiembre': 'september',
                      'octubre': 'october', 'noviembre': 'november', 'diciembre': 'december'}

    class ResponseKey:
        DISCLOSURES = 'disclosures'
        COVERAGES = 'coverages'
        DRIVING_RECORD = 'disclosure_of_driving_record'
        EXCLUSION_UNINSURED_BI = 'uninsured_bi_or_pd_coverage'
        EXCLUSION_COMP_COLL_COVERAGE = 'comprehensive_and_collision_coverage'
        EXCLUSION_BUSINESS_USE = 'business_or_commercial_use'
        EXCLUSION_NAMED_DRIVER_LIMITATION = 'named_drivers_limitation'
        CLIENT_INITIALS = 'client_initials'
        CONDITION_AND_ACKNOWLEDGMENT_AGREEMENT = 'condition_and_acknowledgement_agreement'
        CLIENT_SIGNATURE = 'client_signature'
        STANDARD_BROKER_FEE_DISCLOSURE_FORM = 'standard_broker_fee_disclosure'
        TEXT_MESSAGING_CONSENT_AGREEMENT = 'text_messaging_consent_agreement'
        BROKER_FEE_AGREEMENT = 'broker_fee_agreement'

    class Type1:
        INITIALS = 'Initials: ____ '
        COVERAGES = 'COVERAGES '
        DRIVING_RECORD = 'DISCLOSURE OF DRIVING RECORD '
        EXCLUSION_UNINSURED_BI = 'EXCLUSION: UNINSURED/UNDERINSURED MOTORIST BODILY INJURY/PROPERTY DAMAGE COVERAGE'
        EXCLUSION_COMP_COLL_COVERAGE = 'EXCLUSION: COMPREHENSIVE AND COLLISION COVERAGE'
        EXCLUSION_BUSINESS_USE = 'EXCLUSION: BUSINESS/COMMERCIAL USE'
        EXCLUSION_NAMED_DRIVER_LIMITATION = 'EXCLUSION: NAMED DRIVER(S) LIMITATION – DRIVER(S) EXCLUDED'
        DISCLOSURE_FORM = 'STANDARD BROKER FEE DISCLOSURE FORM '
        MESSAGING_CONSENT_SIGNATURE = 'Applicant/Insured Signature  '
        CLIENT_INITIALS = '(Client Initials ___).'
        CONDITION_AND_ACKNOWLEDGMENT_AGREEMENT = '“I have read and understand the above and understand and read English.” (____ Initials)'
        CLIENT_SIGNATURE = 'Client’s Signature '
        SECTION_BOX_PADDING = {CLIENT_INITIALS: (0.0, -0.03, 0.03, 0.01),
                               CONDITION_AND_ACKNOWLEDGMENT_AGREEMENT: (0.36, -0.045, 0.05, 0.02),
                               CLIENT_SIGNATURE: (-0.01, -0.04, 0.23, 0.01), 'disclosure': (-0.25, -0.03, 0.03, 0.03),
                               MESSAGING_CONSENT_SIGNATURE: (-0.03, -0.045, 0.2, 0.02)}
        SECTION_LABELS = [DRIVING_RECORD, COVERAGES, EXCLUSION_UNINSURED_BI, EXCLUSION_COMP_COLL_COVERAGE,
                          EXCLUSION_BUSINESS_USE, EXCLUSION_NAMED_DRIVER_LIMITATION, DISCLOSURE_FORM, INITIALS,
                          MESSAGING_CONSENT_SIGNATURE, CLIENT_INITIALS, CONDITION_AND_ACKNOWLEDGMENT_AGREEMENT,
                          CLIENT_SIGNATURE]

        class Block:
            MINIMUM_LENGTH = 700
            SIGNED_DAY = 754
            SIGNED_MONTH = 755
            SIGNED_YEAR = 10
            BROKER_FEE = 756
            NAME_LOWER_BOUND = 71

    class Type2:
        COVERAGES = 'COVERAGES'
        DRIVING_RECORD = 'DISCLOSURE OF DRIVING RECORD'
        EXCLUSION_UNINSURED_BI = 'EXCLUSION: UNINSURED/UNDERINSURED MOTORIST BODILY INJURY/PROPERTY DAMAGE'
        EXCLUSION_COMP_COLL_COVERAGE = 'EXCLUSION: COMPREHENSIVE AND COLLISION COVERAGE'
        EXCLUSION_BUSINESS_USE = 'EXCLUSION: BUSINESS/COMMERCIAL USE'
        EXCLUSION_NAMED_DRIVER_LIMITATION = 'EXCLUSION: NAMED DRIVER(S) LIMITATION – DRIVER(S) EXCLUDED'
        DISCLOSURE_FORM = 'STANDARD BROKER FEE DISCLOSURE FORM'
        BROKER_FEE_AGREEMENT = 'BROKER FEE AGREEMENT'
        STANDARD_BROKER_FEE_DISCLOSURE_FORM = 'STANDARD BROKER FEE DISCLOSURE FORM'
        CONDITION_AND_ACKNOWLEDGMENT_AGREEMENT = '“I have read and understand the above and understand and read English.”'
        I_AGREE = 'I agree'
        TEXT_MESSAGING_CONSENT_AGREEMENT = 'TEXT MESSAGING CONSENT AGREEMENT'
        SECTION_LABELS = [COVERAGES, DRIVING_RECORD, EXCLUSION_UNINSURED_BI, EXCLUSION_COMP_COLL_COVERAGE,
                          EXCLUSION_BUSINESS_USE, EXCLUSION_NAMED_DRIVER_LIMITATION, BROKER_FEE_AGREEMENT,
                          TEXT_MESSAGING_CONSENT_AGREEMENT, STANDARD_BROKER_FEE_DISCLOSURE_FORM,
                          CONDITION_AND_ACKNOWLEDGMENT_AGREEMENT, I_AGREE]

        class RegexCollection:
            SIGNED_DATE = r'As of this(.*?)the undersigned'
            BROKER_FEE = r'broker fee is \$([\s]*[\d]+.[\d]{2})'
            INSURED_NAME = r"Full Client's Name (.*?) Broker Full Name"


class PleasureUseLetterTemplate:
    TEMPLATE_DELIMINATOR = '________________________'
    COMPANY_NAME = ['alliance united']
    PADDING = (-0.01, -0.05, 0.075, 0.01)
    PLEASURE_USE_LETTER = 'PLEASURE USE LETTER'
    INSURED_SIGNATURE = 'Insured signature'

    class RegexCollection:
        POLICY_NUMBER = '[\w\d]'
        VEHICLE_INFORMATION = '((\d{4}\s{1}\w{0,15}\s{1}[\w*/-]{0,15})((\s{0,1}\w{17})|))'


class SamePersonTemplate:
    SIGNATURE_SEARCH_KEY = 'Signature / Firma___________________________________ .'
    SIGNATURE_PADDING = (-0.03, -0.045, 0.2, 0.02)
    CHECK_VALID_DOCUMENT_KEY = 'I declare that ______________________is the same person as____________________________. '


class StripeReceiptTemplate:
    KEY_VALUE_DIFF = 3

    class Key:
        RECEIPT = 'Receipt #'
        AMOUNT_PAID = 'AMOUNT PAID'
        DATE_PAID = 'DATE PAID'
        PAYMENT_NOTES = 'PAYMENT METHOD'
        CHECK_VALID_DOCUMENT = RECEIPT

    class RegexCollection:
        PAYMENT_NOTES = '^[0-9]{4}$'
        CURRENCY = '^\$(\d{1,3}(\,\d{3})*|(\d+))(\.\d{2})?$'

    class ResponseKey:
        RECEIPT_NUMBER = 'receipt_number'
        PAYMENT_DATE = 'payment_date'
        AMOUNT_PAID = 'amount_paid'
        PAYMENT_NOTES = 'payment_notes'


class VRDocumentTemplate:
    VIN = 'Vin # :'
    PLATE = 'Plate # :'
    YEAR = 'Model Year # :'
    MODEL = 'Model :'
    MAKE = 'Make # :'
    STYLE = 'Style :'
    REG_OWNER = 'Reg. Owner:'
    CHECK_VALID_DOCUMENT = 'Vehicle Record'
    LEGAL_OWNER = 'Legal Owner:'
    TITLES = [VIN, PLATE, YEAR, MAKE, MODEL, STYLE, REG_OWNER, LEGAL_OWNER]

    class RegexCollection:
        LEASED_VEH_OWNER = "LSR(.*?)LSE"


class PromiseToProvideTemplate:
    class ResponseKey:
        SIGNATURES = 'signature'
        AGREED_BY_SIGN = 'agreed_to_be'
        ACKNOWLEDGMENT_SIGN = 'condition_and_acknowledgement_agreement'
        APPLIED_COVERAGE_DATE = 'applied_coverage_effective_date'
        PTP_BY_DATE = 'promise_to_provide_by_date'
        PTP_AGREEMENT_DATE = 'promise_to_provide_agreement_date'

    class Sections:
        CHECK_VALID_DOCUMENT_KEY = 'PROMISE TO PROVIDE AGREEMENT'
        AGREED_BY_KEY = 'AGREED TO BY:'
        PROMISE_TO_PROVIDE_KEY = 'I hereby promise to provide'
        APPLIED_COVERAGE_KEY = 'I have applied'
        ACKNOWLEDGMENT_INITIALS_KEY = 'Initials'
        TITLES = [APPLIED_COVERAGE_KEY, PROMISE_TO_PROVIDE_KEY, AGREED_BY_KEY]
        SECTION_BOX_PADDING = {AGREED_BY_KEY: (-0.01, -0.035, 0.21, 0.020),
                               ACKNOWLEDGMENT_INITIALS_KEY: (0.12, -0.025, 0.01, 0.01)}

    class RegexCollection:
        DATE = r"[\d]{1,4}[-\\/.][\d]{1,2}[-\\/.][\d]{2,4}"


class EFT:
    class ResponseKey:
        INSURED_NAME = 'insured_name'
        POLICY_NUMBER = 'policy_number'
        SIGNATURES = 'signature'
        INSURED_SIGNATURE = 'insured_signature'
        CARD_HOLDER_SIGNATURE = 'card_holder_signature'

    class Sections:
        EFT_DOCUMENT = 'AUTHORIZATION FOR INSURED’S ELECTRONIC FUNDS TRANSFER'
        INSURED_NAME_START_KEY = "Credit Card Number:"
        INSURED_NAME_END_KEY = "Card Holder's Name:"
        POLICY_NUMBER_START_KEY = 'Policy  Number:'
        POLICY_NUMBER_END_KEY = 'Credit Card Type:'
        VISA = 'Visa'
        MASTER_CARD = 'MASTER CARD'
        PAGE_NO = 0
        INSURED_SIGNATURE = "Insured's Signature"
        CARD_HOLDER_SIGNATURE = "Card Holder's Signature"
        DATE = 'Date'
        XXXX = 'XXXX'
        SECTION_BOX_PADDING = {INSURED_SIGNATURE: (-0.11, -0.07, 0.14, 0.0050),
                               CARD_HOLDER_SIGNATURE: (-0.09, -0.07, 0.12, 0.005), DATE: (-0.12, -0.07, 0.12, 0.005)}

    class RegexCollection:
        END_WITH = '(.*\\w) %s'
        IN_BETWEEN = '%s(.*)%s'


class ArtisanUseLetterTemplate:
    class Sections:
        VALID_DOCUMENT_KEY = 'ARTISAN USE LETTER'
        VALID_DOCUMENT_KEY_BI_LINGUAL = 'ARTISAN USAGE RESTRICTIONS'
        CUSTOMER_NAME = 'Customer name'
        CUSTOMER_NAME_BI_LINGUAL = 'Insured/ Asegurado:'
        POLICY_NUMBER = 'Policy Number'
        VEHICLE = 'Vehicle'
        VEHICLE_BI_LINGUAL = 'Vehicle/'
        SIGNATURE_BI_LINGUAL = 'Signature'
        SIGNATURE = 'INSURED SIGNATURE'
        TITLES = [CUSTOMER_NAME_BI_LINGUAL, POLICY_NUMBER, VEHICLE_BI_LINGUAL, SIGNATURE_BI_LINGUAL]
        SECTION_BOX_PADDING = {SIGNATURE_BI_LINGUAL: (0.11, -0.035, -0.22, 0.01), SIGNATURE: (0.0, -0.04, 0.1, 0.02)}

    class ResponseKey:
        ARTISAN_USE_LETTER = 'artisan_use_letter'
        INSURED_NAME = 'insured_name'
        POLICY_NUMBER = 'policy_number'
        VEHICLES = 'vehicles'
        SIGNATURES = 'signature'

    class RegexCollection:
        POLICY_NUMBER = '[\w\d]'
        VEHICLE_INFORMATION = '((\d{4}\s{1}\w{0,15}\s{1}[\w*/-]{0,15})((\s{0,1}\w{17})|))'


class LicenseStatus(Enum):
    VALID = 'valid'
    REVOKED = 'revoked'
    EXPIRED = 'expired'
    SUSPENDED = 'suspended'
    LIMITED = 'limited'
    SUSPENDED_LIMITED = 'suspended limited'

    @classmethod
    def items(cls):
        return list(map(lambda c: c.value, cls))


class Gender(Enum):
    FEMALE = 'female'
    MALE = 'male'

    @classmethod
    def items(cls):
        return list(map(lambda c: c.value, cls))


class AllowedFileType:
    PDF = 'pdf'
    IMAGE = ['jpg', 'png', 'jpeg']
    ZIP = 'zip'

    class Prefix:
        APPLICATION = 'APP'
        CRM = 'CRM'
        ITC = 'ITC'
        DRIVING_LICENSE = 'DL'
        MVR = 'MVR'
        BROKER_PKG = 'BRPKG'
        PLEASURE_USE_LETTER = 'PUL'
        REGISTRATION = 'REG'
        ARTISAN_USE_LETTER = 'AUL'
        NON_OWNERS_LETTER = 'NOL'
        EFT = 'EFT'
        VR = 'VR'
        STRIPE_RECEIPT = 'STRP'
        PROMISE_TO_PROVIDE = 'PTP'


class ExceptionMessage:
    INVALID_INSURANCE_COMPANY_NAME = 'Inputted application is of invalid insurance company'
    INVALID_FILE_EXCEPTION_MESSAGE = 'Inputted file is invalid'
    FAILED_TO_DOWNLOAD_FILE_FROM_URL_EXCEPTION_MESSAGE = 'Unable to download file from url'
    INVALID_PDF_STRUCTURE_TYPE = 'file has invalid pdf structure'
    UNABLE_TO_GET_ENVIRONMENT_VARIABLE = 'Unable to get environment variable'
    FILE_NOT_FOUND = 'file not found in temporary folder'
    MISSING_DOCUMENTS = 'one or more documents missing'
    UNABLE_TO_EXTRACT_NAME = 'Unable to extract name'
    UNABLE_TO_EXTRACT_EOD_SECTION = 'Unable to extract end of the document'
    UNABLE_TO_EXTRACT_DATE = 'Unable to Extract Date'
    UNABLE_TO_EXTRACT_DATAPOINT = 'Request ID: [{}] -> Unable to extract {}'


class ErrorCode:
    FILE_NOT_FOUND = 'file_not_found'
    INVALID_DOCUMENT = 'invalid_document'
    MISSING_DOCUMENT = 'missing_document'
    INVALID_URL = 'invalid_document_url'
    INVALID_PDF_STRUCTURE = 'invalid_pdf_document_structure'


class ErrorMessage:
    FILE_NOT_FOUND = 'file not found in temporary folder'
    INVALID_INSURANCE_COMPANY_APPLICATION = 'Input application document is invalid'
    INVALID_DOCUMENT = 'Input document is invalid'
    INVALID_URL = 'Input document URL is invalid'
    MISSING_DOCUMENT = 'Missing required input document'
    MISSING_DOCUMENTS_FOR_VERIFICATION = 'Missing one of more required documents'
    SERVER_ERROR = 'Internal server error'
    INVALID_PDF_STRUCTURE = 'Input document is of invalid pdf structure'


class DrivingLicense:
    class ObjectDetection:
        DL_OBJECT_DETECTION_MODEL_PATH = './app/model/drivering_license/dl_objectdetection.pt'
        YOLOV5 = 'ultralytics/yolov5:v6.0'
        MODEL_CONFIDENCE = 0.49
        OBJECT_LABELS = {0: 'address', 1: 'date_of_birth', 2: 'gender', 3: 'license_number', 4: 'name'}

    class RegexCollection:
        DATE_REGEX = '(\d{2})[/.-](\d{2})[/.-](\d{4})$'


class Registration:
    class ObjectDetection:
        REG_OBJECT_DETECTION_MODEL_PATH = './app/model/registration/reg_objectdetection.pt'
        YOLOV5 = 'ultralytics/yolov5:v6.0'
        MODEL_CONFIDENCE = 0.49
        # names: ['validity', 'make', 'year', 'name', 'vin', 'history']
        OBJECT_LABELS = {0: 'validity', 1: 'make', 2: 'year', 3: 'name', 4: 'vin', 5: 'history'}
        VEHICLE_DETAILS = ['year', 'make', 'vin', 'history', 'model']


class OCRConfig:
    class DrivingLicense:
        NAME = '-l eng --oem 1 --psm 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ ,\n" load_system_dawg=false load_freq_dawg=false'
        LICENSE_NO = '-l eng --oem 1 --psm 7 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*- " load_system_dawg=false load_freq_dawg=false'
        ADDRESS = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ,\n-" load_system_dawg=false load_freq_dawg=false'
        DATE = '-l eng --oem 1 --psm 3 -c tessedit_char_whitelist="0123456789/- " load_system_dawg=false load_freq_dawg=false'
        GENDER = '-l eng --oem 1 --psm 7 -c tessedit_char_whitelist="MF" load_system_dawg=false load_freq_dawg=false'

    class Registration:
        YEAR = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="0123456789 \n" load_system_dawg=false load_freq_dawg=false'
        MAKE = '-l eng --oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ \n" load_system_dawg=false load_freq_dawg=false'
        MODEL = '-l eng --oem 1 --psm 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -," load_system_dawg=false load_freq_dawg=false'
        VIN = '-l eng --oem 1 --psm 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" load_system_dawg=false load_freq_dawg=false'
        NAME = '-l eng --oem 1 --psm 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ ,\n" load_system_dawg=false load_freq_dawg=false'
        HISTORY = '-l eng --oem 1 --psm 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ " load_system_dawg=false load_freq_dawg=false'
        DATE = '-l eng --oem 1 --psm 3 -c tessedit_char_whitelist="0123456789/- " load_system_dawg=false load_freq_dawg=false'


class Signature:
    IMG_SIZE = 150
    SIGNATURE_VERIFIER_MODEL_PATH = './app/model/signature_verification/signature_verification.h5'
    FORECAST_THRESHOLD = 0


class PDF:
    TEXT = 0
    BBOX = 1
    PAGE_NUMBER = 2


class Date:
    class RegexCollection:
        YYYY_MM_DD = r'([0-9]{4}[-]([0-9]{0,2})[-][0-9]{0,2})'
        MM_DD_YYYY = r'([0-9]{0,2}[\/-]([0-9]{0,2})[\/-][0-9]{0,4})'

    class Format:
        YMD = '%Y-%m-%d'
        MDY_DASH = '%m-%d-%Y'
        MDY_SLASH = '%m/%d/%Y'


class MultipleNames:
    OR_KEY = ' OR '  # requires spaces


class Parser:
    class Regx:
        NAME = r'([A-Z]{3,14}[\s]{0,1}([A-Z]{3,14})[\s]{0,1}([A-Z]{0,14}))(([\s]{0,1}[,]{0,1}[\s]{0,1}([A-Z]{0,4}))|)'
        DATE = r'([0-9]{0,2}[\/-]([0-9]{0,2})[\/-][0-9]{0,4})'
        LICENSE_NUMBER = r'([0-9A-Z]{1})[\S]([0-9A-Z\-*]*[0-9A-Z\-*\s]*)'
        ADDRESS = r'([0-9]{2,5}\w+[\s]{0,1})([A-Z\s0-9\-,]*[0-9]{3})'
        GENDER = r'^[MF]{1}'
        VIN = r'([A-Z0-9]){17}'
        MAKE = r'([A-Z]){3,4}'
        YEAR = r'([0-9]){4}'
        VEHICLE_HISTORY = r'SALVAGED'
        REG_VALIDITY = r'([0-9]{0,2}[\/]([0-9]{0,2})[\/][0-9]{0,4})'
        REG_NAME = r'([A-Z]{3,14}[\s]{0,1}([A-Z]{3,14})[\s]{0,1}([A-Z]{0,14}))(([\s]{0,1}[,]{1}[\s]{0,1}([A-Z]{0,4}))|)?(?=\n)'


class NonOwnersLetter:
    class ResponseKey:
        INSURED_NAME = 'insured_name'
        POLICY_NUMBER = 'policy_number'
        COMPANY_NAME = 'company_name'
        SIGNATURE = 'signature'
        NON_OWNERS_LETTER = 'non_owners_letter'

    class Sections:
        INSURED = 'Insured:'
        COMPANY_NAME = 'Company Name:'
        POLICY_NUMBER = 'Policy Number:'
        ALLOWED_KEY = [INSURED, COMPANY_NAME, POLICY_NUMBER]
        ALLOWED_COMPANY_NAME = ['alliance united']
        VALID_KEY = 'NON OWNERS  RESTRICTIONS'
        SIGNATURE_SEARCH_KEY = 'Signature:_________________________________________    Date:__________________________'
        PADDING = (-0.01, -0.05, 0.01, 0.005)
        PAGE_NO = 0
        SORT_SIMILARITY_RATIO = 100


class Keys:
    KEYS_DIC = {"driving_license": None, "itc": None, "crm_receipt": None, "application": None,
                "motor_vehicle_record": None, "broker_package": None, "pleasure_use_letter": None,
                "artisan_use_letter": None, "eft": None, "non_owners_letter": None, "stripe_receipt": None,
                "registration": None, "vehicle_record": None, "promise_to_provide": None}
    IMAGE_KEYS = ['driving_license', 'registration']
    REQUIRED_KEYS = ['driving_license', 'itc', 'crm_receipt', 'application', 'motor_vehicle_record', 'broker_package']
