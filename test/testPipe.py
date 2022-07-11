import sys


def main():
    data = sys.argv[1:]
    if not sys.stdin.isatty():
        data.append(sys.stdin.read())
        print("1")
    return data


if __name__ == '__main__':
    data = main()
    print(' '.join(data))