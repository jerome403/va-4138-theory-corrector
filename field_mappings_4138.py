"""
AcroField mapping for VA Form 21-4138 (Statement in Support of Claim).

Vendored copy of the 21-4138 entry from the companion `va-form-filler`
project so this tool fills the real PDF on its own, without depending on
the Form Filler being present or running. If `va-form-filler` renames a
PDF AcroField, update it here too (see CLAUDE.md "field drift" note).
"""

FORM_21_4138 = {
    "form_file": "vba-21-4138-are.pdf",
    "form_name": "VA Form 21-4138",
    "form_title": "Statement in Support of Claim",
    "fields": {
        # Veteran Identification
        "first_name": "Veterans_Beneficiary_First_Name[0]",
        "last_name": "Last_Name[0]",
        "middle_initial": "Middle_Initial1[0]",
        "ssn_first": "SocialSecurityNumber_FirstThreeNumbers[0]",
        "ssn_middle": "SocialSecurityNumber_SecondTwoNumbers[0]",
        "ssn_last": "SocialSecurityNumber_LastFourNumbers[0]",
        "va_file_number": "VA_File_Number_If_Applicable[0]",
        "dob_month": "Veterans_DOB_Month[0]",
        "dob_day": "DOB_Day[0]",
        "dob_year": "DOB_Year[0]",
        "service_number": "Veterans_Service_Number_If_Applicable[0]",
        # Veteran Contact
        "phone_area": "TelephoneNumber_FirstThreeNumbers[0]",
        "phone_middle": "TelephoneNumber_SecondThreeNumbers[0]",
        "phone_last": "TelephoneNumber_LastFourNumbers[0]",
        "phone_intl": "International_Phone_Number[0]",
        "email": "EMAIL_ADDRESS[0]",
        "email_line2": "EMAIL_ADDRESS[1]",
        # Veteran Address
        "address_street": "MailingAddress_NumberAndStreet[0]",
        "address_apt": "MailingAddress_ApartmentOrUnitNumber[0]",
        "address_city": "MailingAddress_City[0]",
        "address_state": "MailingAddress_StateOrProvince[0]",
        "address_zip": "MailingAddress_ZIPOrPostalCode_FirstFiveNumbers[0]",
        "address_zip4": "MailingAddress_ZIPOrPostalCode_LastFourNumbers[0]",
        "address_country": "MailingAddress_Country[0]",
        # Remarks (page 1 box + page 2 continuation)
        "remarks": "REMARKS[0]",
        "remarks_continued": "REMARKS[1]",
        # Date signed
        "date_signed_month": "Date_Signed_Month[0]",
        "date_signed_day": "Date_Signed_Day[0]",
        "date_signed_year": "Date_Signed_Year[0]",
    },
    "checkboxes": {},
}
