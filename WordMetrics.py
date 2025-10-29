import numpy as np

# 참고: https://gitlab.com/-/snippets/1948157
# 일부 변형은 여기를 참조하세요: https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python

# 순수 파이썬
def edit_distance_python2(a, b):
    # 이 버전은 가환적이므로 최적화를 위해 |a|>=|b|를 강제합니다
    if len(a) < len(b):
        return edit_distance_python(b, a)
    if len(b) == 0:  # 빈 시퀀스를 더 빠르게 처리할 수 있습니다
        return len(a)
    # 실제로 두 행만 필요합니다: 현재 채워진 행과 이전 행
    distances = []
    distances.append([i for i in range(len(b)+1)])
    distances.append([0 for _ in range(len(b)+1)])
    # 첫 번째 행을 미리 채울 수 있습니다:
    costs = [0 for _ in range(3)]
    for i, a_token in enumerate(a, start=1):
        distances[1][0] += 1  # 첫 번째 열을 처리합니다.
        for j, b_token in enumerate(b, start=1):
            costs[0] = distances[1][j-1] + 1
            costs[1] = distances[0][j] + 1
            costs[2] = distances[0][j-1] + (0 if a_token == b_token else 1)
            distances[1][j] = min(costs)
        # 다음 행으로 이동:
        distances[0][:] = distances[1][:]
    return distances[1][len(b)]

# 출처: https://stackabuse.com/levenshtein-distance-and-text-similarity-in-python/
def edit_distance_python(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    # print (matrix)
    return (matrix[size_x - 1, size_y - 1])