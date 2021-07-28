"""
Represents a github repistory and sub-repistories.
"""

from dateutil.relativedelta import relativedelta

from GitHubAPI import GitHubAPI, GitApiException
from AwesomeExceptions import ReadmeParsingException

import re
import dateutil.parser
import logging
import datetime
import time

logger = logging.getLogger(__name__)


class RepositoryInfo(object):
    """
    In charge of fetching and parsing meta-data about the repository.
    """

    def __init__(self, repo):
        self._repo = repo
        self._stars_count = 0
        self._last_issue_date = None
        self._issues_count = 0
        self._license = None
        self._forks_count = 0

    def __str__(self):
        return u"""
        Stars Count: {stars_count}
        Last Issue: {last_issue_date}
        Opened Issues Count (Last 6 months): {issues_count}
        License Type: {license_type}
        Forks Count: {forks_count}
        """.format(stars_count=self._stars_count,
                   last_issue_date=self._last_issue_date,
                   issues_count=self._issues_count,
                   license_type=self._license['key'],
                   forks_count=self._forks_count)

    def __repr__(self):
        return self.__str__()

    def collect_repo_info(self):
        """
        Fetches repo info using the API and parses it
        """

        logger.debug("Collecting repo info for {}".format(self._repo))

        six_months_ago = datetime.datetime.today() - relativedelta(months=+6)
        repo_info = self._repo.git_api.get_repo_info(self._repo)
        issues_info = self._repo.git_api.get_issues_data(
            self._repo, since=six_months_ago)

        self._stars_count = repo_info['stargazers_count']
        self._forks_count = repo_info['forks_count']
        self._license = repo_info['license']

        self._last_issue_date = 0
        if issues_info['items']:
            last_issue_date = issues_info['items'][0]['created_at']
            # Convertion to timestamp
            self._last_issue_date = time.mktime(
                dateutil.parser.isoparse(last_issue_date).timetuple())

        self._issues_count = issues_info['total_count']


class Repository(object):
    """
    Represents a Git Repository, and in charge of parsing Awesome data and sub-repos.
    """

    LINK_PATTERN = u"\* \[(?P<friendly_name>.*)\]\(https://github\.com/(?P<owner_name>.*?)/(?P<repo_name>.*?)\) - (?P<description>.*)\."

    def __init__(self, friendly_name, owner, repo_name, description, git_api):
        self.owner = owner
        self.repo_name = repo_name
        self.description = description
        self.friendly_name = friendly_name
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
        return {"description": self.description,
                "url": self.url,
                "stars": self.repo_info._stars_count,
                "last_issue_date": self.repo_info._last_issue_date,
                "issues_count": self.repo_info._issues_count,
                "license": self.repo_info._license,
                "forks_count": self.repo_info._forks_count}

    def get_sub_repos(self):
        """
        Retrieves sub-repos of this repo and parses them

        :return: returns a list of Repo objects
        """

        repos = []

        logger.info("Fetching sub-repos")
        repos_groups = self.__parse_markdown(
            self.git_api.get_readme(self))

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

        groups = re.findall(re.compile(Repository.LINK_PATTERN), text)
        if not groups:
            raise ReadmeParsingException(
                u"Could not parse readme of repo {}".format(self))

        return groups

    def collect_repo_info(self):
        self.repo_info.collect_repo_info()
