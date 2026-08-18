import json

from header_formatter.utils import empty_keywords, keywords_in_dict, regex_expressions

# for k, _dict in regex_expressions.items():
#     print(f"\n{k}")
#     print("=" * 50)
#     print("keyword,expression,example")
#     for kw, (exp, ex) in _dict.items():
#         print(f"{kw}," + exp + "," + ex)


# for k, _dict in keywords_in_dict.items():
#     print(f"\n{k}")
#     print("=" * 50)
#     print("keyword,dict")
#     for kw, val in _dict.items():
#         val = json.dumps({0: "Internal", 6: "External"})
#         print(f"{kw};", val)

# for k, _dict in empty_keywords.items():
#     print(f"\n{k}")
#     print("=" * 50)
#     print("keyword,values")
#     for kw, val in _dict.items():
#         val = json.dumps(val)
#         print(f"{kw}," + val)


json.loads('"OPD"')
