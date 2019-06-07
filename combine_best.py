from itertools import combinations

lst = [732,750,719,720,738,707,715]
count = 0
for r in range (3, len(lst)):
    comb = set(combinations(lst, r))
    count += len(comb)
    print(comb)
print(count)