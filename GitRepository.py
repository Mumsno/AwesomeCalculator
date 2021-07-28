from GitHubAPI import GitHubAPI, GitApiException
import re
import dateutil.parser
from dateutil.relativedelta import relativedelta
import logging
import datetime
import time

LINK_PATTERN = re.compile(
    u"\* \[(?P<friendly_name>.*)\]\(https://github\.com/(?P<owner_name>.*?)/(?P<repo_name>.*?)\) - (?P<description>.*)\.")
HALF_A_YEAR_AGO = datetime.datetime.today() - relativedelta(months=+6)
logger = logging.getLogger(__name__)


class RepositoryInfo(object):

    def __init__(self, repo):
        self.repo = repo
        self.stars_count = 0
        self.last_issue_date = None
        self.issues_count = 0
        self.license = None
        self.forks_count = 0

    def __str__(self):
        return u"""
        Stars Count: {stars_count}
        Last Issue: {last_issue_date}
        Opened Issues Count (Last 6 months): {issues_count}
        License Type: {license_type}
        Forks Count: {forks_count}
        """.format(stars_count=self.stars_count, last_issue_date=self.last_issue_date, issues_count=self.issues_count, license_type=self.license['key'], forks_count=self.forks_count)

    def __repr__(self):
        return self.__str__()

    def collect_repo_info(self):
        """
        Fetches repo info using the API and parses it
        """

        logger.debug("Collecting repo info for {}".format(self.repo))

        repo_info = self.repo.git_api.get_repo_info(self.repo)
        issues_info = self.repo.git_api.get_issues_data(
            self.repo, since=HALF_A_YEAR_AGO)

        self.stars_count = repo_info['stargazers_count']
        self.forks_count = repo_info['forks_count']
        self.license = repo_info['license']

        # Timestamp
        self.last_issue_date = time.mktime(dateutil.parser.isoparse(
            issues_info['items'][0]['created_at']).timetuple()) if issues_info['items'] else 0
        self.issues_count = issues_info['total_count']


class Repository(object):

    def __init__(self, friendly_name, owner, repo_name, description, git_api):
        self.owner = owner
        self.repo_name = repo_name
        self.friendly_name = friendly_name
        self.description = description
        self.git_api = git_api
        self.repo_info = RepositoryInfo(self)

    @ property
    def url(self):
        return "https://github.com/{owner}/{repo_name}".format(owner=self.owner, repo_name=self.repo_name)

    def __str__(self):
        return u"* [{friendly_name}] {url} - {description}.".format(friendly_name=self.friendly_name, url=self.url, description=self.description)

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {"description": self.description, "url": self.url, "stars": self.repo_info.stars_count, "last_issue_date": self.repo_info.last_issue_date, "issues_count": self.repo_info.issues_count, "license": self.repo_info.license, "forks_count": self.repo_info.forks_count}

    def get_sub_repos(self):
        """
        Retrieves sub-repos of this repo and parses them

        :return: returns a list of Repo objects
        """

        logger.info("Fetching sub-repos")
        repos_groups = self.__parse_markdown(
            self.git_api.get_readme(self))
        repos = []

        for group in repos_groups:
            repos.append(Repository(
                *group, git_api=self.git_api))

        logger.debug("Found {} Sub-Repos".format(len(repos)))
        return repos

    def __parse_markdown(self, text):
        """
        Parses a readme file and reutrns a list of sub-repos.

        :text: textual markdown content
        :return: a list of tuples in the following structure: (friendly_name, owner_name, repo_name)
        """

        groups = re.findall(LINK_PATTERN, text)
        if not groups:
            raise ReadmeParsingException(
                u"Could not parse readme of repo {}".format(self))

        return groups

    def collect_repo_info(self):
        self.repo_info.collect_repo_info()


class ReadmeParsingException(Exception):
    pass
