from src.world import person
from src.seir import DiseaseState

#Test the amount of the  created Immune
def test_createInfectedPersons(R0_percent):
    assert R0_percent >= 0 
    cnt = 0
    for _ in range(0,100):
        tmp = person.Person(7)
        if tmp.last_state == DiseaseState.IMMUNE:
            cnt = cnt + 1
    tmp = cnt / 100
    #Assert that the amount of people that created in recovered state are 
    # within 5 percent of expected
    assert tmp > R0_percent - 0.05
    assert tmp < R0_percent + 0.05





