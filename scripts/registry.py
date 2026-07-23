from scripts.command import (
    models,
    providers,
    provider,
    use,
    current,
    doctor,
    history,
)

from scripts.benchmark import benchmark
from scripts.recommend import recommend
from scripts.compare import compare
from scripts.preference import preference
from scripts.advisor import advisor
from scripts.rank import rank
from scripts.chat import chat


def benchmark_command(args):

    if "--quick" in args:
        benchmark(runs=1, warmup=False)

    elif "--stress" in args:
        benchmark(runs=10, warmup=True)

    else:
        benchmark()


def compare_command(args):

    if args:
        compare(args)
    else:
        compare([])


def recommend_command(args):

    if args:
        recommend(args[0])
    else:
        recommend()


def provider_command(args):

    if args:
        provider(args[0])
    else:
        provider()


def use_command(args):

    if not args:
        print("Usage: nova use <model>")
        return

    use(args[0])


def preference_command(args):

    if not args:
        preference()
    else:
        preference(args[0])


def advisor_command(args):
    advisor(args)


def rank_command(args):
    rank(args)




COMMANDS = {
    "models": lambda args: models(),
    "providers": lambda args: providers(),
    "provider": provider_command,
    "use": use_command,
    "current": lambda args: current(),
    "doctor": lambda args: doctor(),
    "benchmark": benchmark_command,
    "history": lambda args: history(),
    "recommend": recommend_command,
    "compare": compare_command,
    "preference": preference_command,
    "advisor": advisor_command,
    "rank": rank_command,
    "chat": chat,

}