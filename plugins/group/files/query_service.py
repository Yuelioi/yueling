from .qq_file_repo import qq_file_repo
from .models_domain import FileQueryInfo, QueryResult
import re
import unicodedata
import json
MAX_RESULT = 5

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.casefold()
    text = re.sub(r"[^0-9a-z\u4e00-\u9fa5]", "", text)
    return text


class QueryService:

    async def execute_query(self, bot, group_id: int, keyword: str) -> QueryResult:
        snapshot = await qq_file_repo.get_all_files_recursively(
            bot,
            group_id,
            include_root=True,
            include_folders=True
        )


        key = normalize(keyword)
        results = []

        for f in snapshot.files:
            if key in normalize(f.file_name):
                results.append(
                    FileQueryInfo(
                        file_name=f.file_name,
                        folder=f.folder_name or "根目录",
                        size=f.file_size
                    )
                )
                if len(results) >= MAX_RESULT:
                    break

        return QueryResult(files=results)


query_service = QueryService()
