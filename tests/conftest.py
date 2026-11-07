import pandas as pd
import pytest

@pytest.fixture
def raw_games():
    # Only SYNTHETIC test data; never presented as real game sales.
    return pd.DataFrame([
        [1,"Game A","Wii",2006,"Sports","Nintendo",10.0,5.0,3.0,1.0,19.0],
        [2,"Game B","Wii",2006,"Sports","Nintendo",5.0,3.0,1.0,0.5,9.5],
        [3,"Game C","DS",2007,"Fighting","Nintendo",2.0,2.0,2.0,1.0,7.0],
        [4,"Game D","DS",2007,"Fighting","Nintendo",4.0,1.0,8.0,0.0,13.0],
        [5,"Game E","PS2",2007,"Simulation","Other Pub",1.0,2.0,4.0,1.0,8.0],
        [6,"Game F","PS2",2008,"Racing","Other Pub",3.0,2.0,1.0,0.0,6.0],
    ], columns=["Rank","Name","Platform","Year","Genre","Publisher","NA_Sales","EU_Sales","JP_Sales","Other_Sales","Global_Sales"])
