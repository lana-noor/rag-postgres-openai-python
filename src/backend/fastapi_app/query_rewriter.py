import json
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionToolParam,
)

def build_search_function() -> list[ChatCompletionToolParam]:
    return [
        {
            "type": "function",
            "function": {
                "name": "search_database",
                "description": "Search PostgreSQL database for relevant documents based on user query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_query": {
                            "type": "string",
                            "description": "Query string to use for full text search, e.g. 'financial policies for Q3 2024'",
                        },
                        "category_filter": {
                            "type": "object",
                            "description": "Filter search results based on document category",
                            "properties": {
                                "comparison_operator": {
                                    "type": "string",
                                    "description": "Operator to compare the column value, either '=' or '!='",
                                },
                                "value": {
                                    "type": "string",
                                    "description": "Value to compare against, e.g. 'financial statement'",
                                },
                            },
                        },
                        "date_filter": {
                            "type": "object",
                            "description": "Filter search results based on document date",
                            "properties": {
                                "comparison_operator": {
                                    "type": "string",
                                    "description": "Operator to compare the column value, either '>', '<', '>=', '<=', '='",
                                },
                                "value": {
                                    "type": "string",
                                    "description": "Date to compare against, in the format 'YYYY-MM-DD', e.g. '2024-09-30'",
                                },
                            },
                        },
                    },
                    "required": ["search_query"],
                },
            },
        }
    ]

def extract_search_arguments(original_user_query: str, chat_completion: ChatCompletion):
    response_message = chat_completion.choices[0].message
    search_query = None
    filters = []
    if response_message.tool_calls:
        for tool in response_message.tool_calls:
            if tool.type != "function":
                continue
            function = tool.function
            if function.name == "search_database":
                arg = json.loads(function.arguments)
                search_query = arg.get("search_query", original_user_query)
                if "category_filter" in arg and arg["category_filter"]:
                    category_filter = arg["category_filter"]
                    filters.append(
                        {
                            "column": "document_category",
                            "comparison_operator": category_filter["comparison_operator"],
                            "value": category_filter["value"],
                        }
                    )
                if "date_filter" in arg and arg["date_filter"]:
                    date_filter = arg["date_filter"]
                    filters.append(
                        {
                            "column": "document_date",
                            "comparison_operator": date_filter["comparison_operator"],
                            "value": date_filter["value"],
                        }
                    )
    elif query_text := response_message.content:
        search_query = query_text.strip()
    return search_query, filters
