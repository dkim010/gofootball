'''build-teams'''
import argparse
import random
from pprint import pprint


def load_file(filename):
    '''read members, leaders from a file'''
    leaders = set()
    members = set()
    with open(filename, encoding='utf8') as desc:
        leaders = {token.strip() for token in desc.readline().split(',')}
        for line in desc:
            member = line.strip()
            if member:
                members.add(member)
    members = members - leaders
    return members, leaders


def build_teams(members, leaders):
    '''build teams by random'''
    leaders = set(leaders)
    members = set(members) - leaders
    teams = {}
    share = len(members) // 3
    remainder = len(members) % 3
    # share
    for leader in leaders:
        teams[leader] = set(random.sample(members, share))
        members -= teams[leader]
    # remainder
    for _ in range(remainder):
        leader = random.sample(leaders, 1)[0]
        leaders.remove(leader)
        member = random.sample(members, 1)[0]
        members.remove(member)
        teams[leader].add(member)
    return teams


def main():
    '''entrypoint'''
    parser = argparse.ArgumentParser()
    parser.add_argument('--textfile', type=str, required=True)
    args = parser.parse_args()

    members, leaders = load_file(args.textfile)
    teams = build_teams(members, leaders)

    pprint(('members:', members))
    pprint('--------------------------')
    pprint(('leaders:', leaders))
    pprint('--------------------------')
    pprint(('teams:', teams))


if __name__ == '__main__':
    main()
