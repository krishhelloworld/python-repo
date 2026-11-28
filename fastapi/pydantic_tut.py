from pydantic import BaseModel,EmailStr,AnyUrl,Field,field_validator,model_validator,computed_field
from typing import Dict,List,Optional,Annotated


class Patient(BaseModel):

    name: Annotated[str , Field(
       max_length=50,
       title='Name of the patient',
       description='Give the name of the patient in less than 50 words',
       examples=['Nitish','Amit'])]
    age: int
    email: EmailStr
    dashboard_url: Optional[AnyUrl]=None
    weight: float = Field(gt=0,lt=120)
    height: float = Field(gt=0,lt=120)
    married: bool
    print(patient1)
    allergies: Annotated[Optional[List[str]],Field(default=None,max_length=5)]
    contact_details: Dict[str,str]
    address:

    @field_validator('email')
    @classmethod
    def email_validator(cls,value)->EmailStr:
        valid_domains=['hdfc.com','icic.com']
        ##ex of email= nowkrish2702@gmail.com
        ##split the email after the @
        domain = value.split('@')[-1]
        if domain not in valid_domains:
            raise ValueError('not a valid domain')

        return value

    """
    to class member to check the data when they depend on each other
    """
    @model_validator(mode='after')
    def validate_emergency_contact(cls,model)->bool:
        if model.age > 60 and len(contact_details)==0:
            raise ValueError('This patient must have atleast 1 contact')

        return True

    # to compute a member using other input member from the data
    @computed_field
    @property
    def bmi(self)-> float:
        bmi= round(self.weight/( self.height**2 ),2)
        return bmi



# def insert_patient_data(name,age)://without using the class
#     print(name)
#     print(age)
#     print('inserted')
#gt->greater than, lt->less than ,

def insert_patient_data(patient: Patient):
    print(patient.name)
    print(patient.age)
    print(patient.email)
    print(patient.married)
    print(patient.weight)
    print(patient.height)
    print(patient.bmi)
    print(patient.allergies)
    print(patient.contact_details)
    print('value inserted')


patient_info= {'name':'nitish','age':30,'email':'nowkrish2702@hdfc.com','dashboard_url':'https://health.monitor.com/','weight':50,'height':1.72,'married':False,'allergies':['malaria','fever'],'contact_details':{'ramesh':'987654321'}}
patient1= Patient(**patient_info)
insert_patient_data(patient1)
