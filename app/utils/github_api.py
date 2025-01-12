from github import Github
from aiocache import cached
from aiocache.serializers import PickleSerializer
from json import loads


github = Github()


@cached(ttl=7200, serializer=PickleSerializer())
async def get_info_war(
        repo_link: str,
        repo_path: str
):
    repo = github.get_repo(repo_link)
    commits = repo.get_commits(path=repo_path)
    if commits.totalCount <= 0:
        return [False, "Не знайдено файлів"]

    latest_commit = commits[0]

    files_changed = latest_commit.files

    last_file_path = files_changed[0].filename
    file_content = repo.get_contents(last_file_path)
    file_text = loads(file_content.decoded_content.decode("utf-8"))
    return [True, file_text]
