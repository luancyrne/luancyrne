"""Tests for GitHub API aggregation logic."""

from generator.github_api import GitHubAPI


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_fetch_stats_graphql_paginates_owned_repos(monkeypatch):
    api = GitHubAPI("galaxy-dev", token="token")
    calls = []
    pages = [
        {
            "data": {
                "user": {
                    "repositoriesContributedTo": {"totalCount": 12},
                    "pullRequests": {"totalCount": 7},
                    "issues": {"totalCount": 4},
                    "repositories": {
                        "totalCount": 3,
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor-1"},
                        "nodes": [{"stargazerCount": 5}, {"stargazerCount": 8}],
                    },
                    "contributionsCollection": {
                        "totalCommitContributions": 100,
                        "restrictedContributionsCount": 25,
                    },
                }
            }
        },
        {
            "data": {
                "user": {
                    "repositoriesContributedTo": {"totalCount": 12},
                    "pullRequests": {"totalCount": 7},
                    "issues": {"totalCount": 4},
                    "repositories": {
                        "totalCount": 3,
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": [{"stargazerCount": 3}],
                    },
                    "contributionsCollection": {
                        "totalCommitContributions": 100,
                        "restrictedContributionsCount": 25,
                    },
                }
            }
        },
    ]

    def fake_request(method, url, **kwargs):
        calls.append(kwargs["json"]["variables"]["repoCursor"])
        return FakeResponse(pages.pop(0))

    monkeypatch.setattr(api, "_request", fake_request)

    assert api._fetch_stats_graphql() == {
        "commits": 125,
        "stars": 16,
        "prs": 7,
        "issues": 4,
        "repos": 3,
    }
    assert calls == [None, "cursor-1"]


def test_fetch_languages_graphql_aggregates_visible_non_fork_repos(monkeypatch):
    api = GitHubAPI("galaxy-dev", token="token")
    pages = [
        {
            "data": {
                "user": {
                    "repositories": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor-1"},
                        "nodes": [
                            {
                                "isFork": False,
                                "languages": {
                                    "edges": [
                                        {"size": 100, "node": {"name": "Python"}},
                                        {"size": 50, "node": {"name": "TypeScript"}},
                                    ]
                                },
                            },
                            {
                                "isFork": True,
                                "languages": {
                                    "edges": [
                                        {"size": 999, "node": {"name": "Ruby"}},
                                    ]
                                },
                            },
                        ],
                    }
                }
            }
        },
        {
            "data": {
                "user": {
                    "repositories": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": [
                            {
                                "isFork": False,
                                "languages": {
                                    "edges": [
                                        {"size": 75, "node": {"name": "Python"}},
                                        {"size": 25, "node": {"name": "Go"}},
                                    ]
                                },
                            }
                        ],
                    }
                }
            }
        },
    ]

    def fake_request(method, url, **kwargs):
        return FakeResponse(pages.pop(0))

    monkeypatch.setattr(api, "_request", fake_request)

    assert api._fetch_languages_graphql() == {
        "Python": 175,
        "TypeScript": 50,
        "Go": 25,
    }
