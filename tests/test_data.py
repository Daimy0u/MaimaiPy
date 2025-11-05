import pytest
import asyncio
import pytest_asyncio

from app.data_types.maimaidx import MDXChartInternalMap
from app.datasource import OtogeDB, MDXDataSource
from app.record import RecordEntry

DELAY = 1
TIMEOUT = 10

async def await_ready(source: MDXDataSource):
    increment = 0
    while not source.ready and increment < TIMEOUT:
        increment += DELAY
        await asyncio.sleep(DELAY)
    if source.ready:
        return True
    else:
        raise ValueError(f"Failed to initialise data source within {TIMEOUT} seconds.")

@pytest.mark.asyncio
class TestSourceOtogeDB:
    @pytest_asyncio.fixture(autouse=True)
    async def fixture(self):
        self.source = OtogeDB()
        await await_ready(self.source)
        yield
        
    @pytest.mark.xfail(reason="Constant reference mismatch!")
    async def test_constants_from_reference(self):
        comparisons: MDXChartInternalMap = {
            ('Latent Kingdom','DX','MASTER'): 14.9,
            ('系ぎて','DX','ReMASTER'): 15.0,
            ('≠彡"/了→','DX','MASTER'): 14.4,
            ('Sweets×Sweets', 'STD', 'MASTER'): 11.4
        }
        for arg, ans in comparisons.items():
            assert self.source.get_constant(arg[0],arg[1],arg[2]) == ans
            
    @pytest.mark.xfail(reason="Constant shouldn't exist!")
    async def test_invalid_constants(self):
        comparisons: MDXChartInternalMap = {
            ('Latent Kingdom','STD','MASTER'): 0.0,
            ('系ぎて','STD','ReMASTER'): 0.0,
            ('≠彡"/了→','STD','MASTER'): 0.0,
            ('Sweets×Sweets', 'DX', 'MASTER'): 0.0
        }
        for arg, ans in comparisons.items():
            assert self.source.get_constant(arg[0],arg[1],arg[2]) == ans
    
    @pytest.mark.xfail(reason="Rating calculations are invalid!")
    async def test_chart_rating_calculation(self):
        comparisons: dict[RecordEntry,float]= {
            RecordEntry('DX','ReMASTER','100.5012%','15','系ぎて'):(15.0*100.5012*0.224),
            RecordEntry('DX','ReMASTER','100.4999%','14+','Latent Kingdom'):(14.9*100.4999*0.222),
            RecordEntry('DX','ReMASTER','100.0000%','14+','躯樹の墓守'):(14.9*100.0*0.216)
        }
        for record, rating in comparisons.items():
            assert record.rating == rating
            
            
        
    