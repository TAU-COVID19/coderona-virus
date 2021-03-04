from src.simulation.event import EmptyTrigger,EmptyEffect,Event

def test_InitEvent():
    trigger = EmptyTrigger()
    EffectList = [EmptyEffect()]
    e = Event(trigger,EffectList)
    e.apply(None)

