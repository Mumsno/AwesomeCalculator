from re import search
import requests
from requests import api


class GitAPIEndpoints(object):
    """
    All Github API's endpoints
    """

    REPO_INFO = "https://api.github.com/repos/{owner_name}/{repo_name}"
    README = "https://raw.githubusercontent.com/{owner_name}/{repo_name}/master/README.md"
    ISSUES_INFO = "https://api.github.com/search/issues"


class GitHubAPI(object):
    """
    In charge of making API requests to github's api
    """

    def __init__(self, token):
        self.token = token

    @property
    def auth_header(self):
        return {"Authorization": "token {}".format(self.token)}

    def get_readme(self, repo):
        api_url = GitAPIEndpoints.README.format(
            owner_name=repo.owner, repo_name=repo.repo_name)
        return self.__get(api_url).text

    def get_repo_info(self, repo):
        """
        Fetches General information about the repo 

        :repo: the repo object to query.
        """

        api_url = GitAPIEndpoints.REPO_INFO.format(
            owner_name=repo.owner, repo_name=repo.repo_name)
        try:
            return self.__get(api_url).json()
        except ValueError as e:
            raise GitApiException(
                "Couldn't parse repo info for {}, received invalid json object".format(repo))

    def get_issues_data(self, repo, since, state="open"):
        """
        fetches issues data

        :repo: the repo object to query.
        :since: a datetime object representing the date to fetch data since.
        :state: issue's state to query, choices are: "all", "closed", "opened". default is "all".
        """

        issues_state = state if state.lower() in ("open", "closed") else "open"
        search_string = "q=repo:{owner}/{repo_name}+type:issue+state:{state}+sort:created+created:>{since}".format(
            owner=repo.owner, repo_name=repo.repo_name, state=issues_state, since=since.strftime("%Y-%m-%d"))
        api_url = GitAPIEndpoints.ISSUES_INFO.format(
            owner_name=repo.owner, repo_name=repo.repo_name)

        try:
            return self.__get(api_url, search_string).json()
        except ValueError as e:
            raise GitApiException(
                "Couldn't parse Issues info for {}, received invalid json object".format(repo))

    def __get(self, api_url, params={}):
        """
            ReadMe API Request

            :return: Returns the textual response
        """

        response = requests.get(api_url, params, headers=self.auth_header)

        if response.status_code == 403:
            raise GitApiException(u"API Rate Limit Exceeded")
        if response.status_code != 200:
            raise GitApiException(
                u"Request Failed For {}".format(response.url))

        return response


class GitApiException(Exception):
    pass
