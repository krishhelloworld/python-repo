
def info(Patient):
    print(green)
    print(Patient.name)
    print(Patient.gender.value)
    # OR
    # print(Patient.gender.name)
    print(Patient.address)
    print(Patient.verified_at)
    print(reset, end="")
    print("value inserted", end="\n\n\n")
