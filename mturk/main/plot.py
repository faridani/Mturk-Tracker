import itertools


def repair(data, is_anomaly, fixer=None, depth=1):
    """Return iterator to repaired list of given data

    If any data is considered broken, remove it from the iterated list.

    `is_anomaly` should be function that takes 2 arguments. First - the object
    that is being analyzed and second arugment - list of object that should
    help to consider if the first one is anomaly. `is_anomaly` should return
    True if the first argument is anomaly, else False.

    `depth`* 2 is the amount of items that should be passed to `is_anomaly`
    function as second argument

    This will never return `depth` and last `depth` number of  items from the
    given list, but you shouldn't care for large amount of data anyway.
    """

    iterators = []
    for i in range(depth * 2 + 1):
        iterators.append(itertools.islice(data, i, None))
    items_iter = itertools.izip(*iterators)

    for items in items_iter:
        mid = items[depth]
        other = items[:depth] + items[depth + 1:]
        if is_anomaly(mid, other):
            if fixer is not None:
                yield fixer(mid, other)
        else:
            yield mid
