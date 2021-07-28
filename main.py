from re import sub
from GitHubAPI import GitHubAPI
from AwesomeRating import RatingCalculator
from GitRepository import Repository
import argparse
import logging
from pprint import pprint


def get_user_input():
    """
        Reads input from the user  
        :return: ArgumentParser object
    """

    parser = argparse.ArgumentParser(
        description='This script is used to determine how awesome are awesome pages!')
    parser.add_argument('owner_name', type=str,
                        help="The awesome page's owner name",)
    parser.add_argument('repo_name', type=str,
                        help="The awesome repository's name")
    parser.add_argument('token', type=str,
                        help="Github's authentication token")
    parser.add_argument('--debug', action="store_true")
    parser.add_argument(
        '--limit', help="Limit sub-repos queries for debug or validation purposes", default=0, type=int)
    return parser.parse_args()


def main():

    args = get_user_input()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    api = GitHubAPI(args.token)

    logging.info("Fetching Awesome Repo Data")
    main_repo = Repository(
        args.repo_name, args.owner_name, args.repo_name, "", api)

    sub_repos = main_repo.get_sub_repos()

    serialized_sub_repos = []
    for index, sub_repo in enumerate(sub_repos):
        sub_repo.collect_repo_info()
        serialized_sub_repos.append(sub_repo.to_dict())
        if (args.limit > 0) and (index + 1 >= args.limit):
            break

    rating_calculator = RatingCalculator(serialized_sub_repos)
    rating_calculator.calculate_awesomeness()

    pprint(rating_calculator.serialize())


if __name__ == '__main__':
    main()
