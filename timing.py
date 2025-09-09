import time
from functools import wraps
from rich import print


## run python -m rich.emoji | grep clock to get all emojis for clocks
# from https://gist.github.com/Integralist/77d73b2380e4645b564c28c53fae71fb
def timeit(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            elapsed_time = time.perf_counter() - start_time
            hours, minutes, seconds = int(elapsed_time/60/60 % 60), int(elapsed_time/60 % 60), int(elapsed_time%60)
            time_in_secs = f"{hours:02}:{minutes:02}:{seconds:02}"  # {elapsed_time:.4f}

            clock_emoji = ":timer_clock:"*3
            if len(args) >= 2:
                myenum = args[1][:40].replace('\n', ' ') + '..'
                #print(":alarm_clock: " * 15 )
                print(f"{clock_emoji}  [bold red]{myenum}[/bold red] response took [bold]{elapsed_time:.4f}[/bold] sec {clock_emoji}\n")
            else: # func.__name__ == 'main'
                print(f'\n{clock_emoji}  Total elapsed time (`{func.__name__}`): {time_in_secs} {clock_emoji}')
    return wrapper

