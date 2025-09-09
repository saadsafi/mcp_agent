from enum import Enum
from typing import List, Tuple
import sys

def dedent(multiline:str) -> str:
    return "\n".join( [line.strip() for line in multiline.strip().splitlines()] )

class MyPrompts(Enum):
    PARIS_TIME = "What is the time now in Paris?"
    LDN_TO_HK = "What is the time difference now between London and Hong Kong?"

    ADD_MULT = "what's (3 + 5) x 12?"
    SQRT_NEG = "what is the square root of -173.5?"
    GT_OF_NUMS = "which number is greater of these numbers: 9.11 and 9.8?"

    SQL_REGIONS = "inspect the table public.region in our postgres database, then run a SQL query to list the regions in that table."
    SQL_WEST_REGIONS =  "inspect table public.us_states in our postgres database, then run a SQL query to list the states in the western side of the USA."

    PYTHON_MATH_EXE = """execute this python code:
    import math
    sq = math.sqrt( math.fabs(-173.5) )
    print(sq)
    """
    PYTHON_INTERNET_USAGE = """You are given a csv file (/mnt/data/internet_usage.csv), 
    it has a first column (string typed) named 'Country' with unique values, followed by years from '2000' up to '2020' which contain 'float' values of Internet usage in each 'Country' over these years.
    Write a Python code to do the following:
    1. Open the csv file using Pandas.
    2. Replace with zero any value that is N/A.
    3. Find the top 10 countries sorted by the average growth in their internet usage.
    4. Plot the resultant top 10 countries, x is years, y is the internet usage.
    5. Save (or overwrite) the plot to an image file in the same directory as the csv file.

    Finally, noting that all required packages are already installed, go ahead and execute the Python code.
    """

    MATH_JOHN_AGE = """
    John is one of 4 children. The first sister is 4 years old.
    Next year, the second sister will be twice as old as the first sister.
    The third sister is two years older than the second sister.
    The third sister is half the age of her older brother. How old is John?

    """
    #LOGIC_THREE_THIEVS
    #LOGIC_MARTIN_SYSTERS
    #LOGIC_

    @classmethod
    def get_prompts(cls, args:List[str], dedent_value=True) -> List[Tuple[str,str]]:
        if not args:
            args = ['all']

        all_prompts = {
            'time': [ MyPrompts.PARIS_TIME, MyPrompts.LDN_TO_HK ],
            'calc':  [ MyPrompts.ADD_MULT, MyPrompts.SQRT_NEG, MyPrompts.GT_OF_NUMS ],
            'sql':  [ MyPrompts.SQL_REGIONS, MyPrompts.SQL_WEST_REGIONS ],
            'code': [ MyPrompts.PYTHON_MATH_EXE, MyPrompts.PYTHON_INTERNET_USAGE ],
            'all':  [ p for p in MyPrompts ]
        }

        prompts = [ (p.name, dedent(p.value) if dedent_value else p.value) 
                   for arg in args if arg in all_prompts 
                   for p in all_prompts[str(arg)]
                  ]
        return prompts
    

if __name__ == "__main__":
    #args = sys.argv[1:] if sys.argv[1:] else ['all']
    # args = sys.argv[1:]
    # prompts = MyPrompts.get_prompts(args)
    # for p in prompts:
    #     print(p[0])
    print( dedent(MyPrompts.MATH_JOHN_AGE.value) )
