from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import ClassVar
from langchain_community.utilities import GoogleSerperAPIWrapper

class WebSearchInput(BaseModel):
    query: str = Field(..., description="用於查詢的關鍵字")

class WebSearchTool(BaseTool):
    args_schema: ClassVar[type] = WebSearchInput

    def __init__(self):
        super().__init__(
            name="Web Search",
            description="使用 Serper API 執行即時網路搜尋"
        )

    def _run(self, query: str) -> str:
        try:
            search = GoogleSerperAPIWrapper()
            return search.run(query)
        except Exception as e:
            return f"搜尋時發生錯誤：{e}"
