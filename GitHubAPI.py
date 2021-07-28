"""
This module GitHub's API Interface
"""

from requests import get


class HTTPStatuses(object):
    """
        Relevant HTTP Statuses
    """

    SUCCESS = 200
    FORBIDDEN = 403
    NOT_FOUND = 404


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

    SEARCH_STRING_FORMAT = "q=repo:{owner}/{repo_name}+type:issue+state:{state}+sort:created+created:>{since}"
    ISSUE_STATE_CHOICES = ("open", "closed")

    def __init__(self, token):
        self._token = token

    @property
    def auth_header(self):
        return {"Authorization": "token {}".format(self._token)}

    def get_readme(self, repo):
        """
        Fetches the readme.md file from the repo.

        :repo: the repo to fetch the file from.
        """

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

        issues_state = state if state.lower() in GitHubAPI.ISSUE_STATE_CHOICES else "open"
        search_string = GitHubAPI.SEARCH_STRING_FORMAT.format(
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
            :api_url: the api's url to query.
            :params: get parameters to add to the request.
            :return: Returns the textual response
        """

        response = get(api_url, params, headers=self.auth_header)

        if response.status_code == HTTPStatuses.FORBIDDEN:
            raise GitApiException(u"API Rate Limit Exceeded")
        if response.status_code == HTTPStatuses.NOT_FOUND:
            raise GitApiException(u"API Not Found Or Invalid Token")
        if response.status_code != HTTPStatuses.SUCCESS:
            raise GitApiException(
                u"Request Failed For {}".format(response.url))

        return response


class GitApiException(Exception):
    pass
