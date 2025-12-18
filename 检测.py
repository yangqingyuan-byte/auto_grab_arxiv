# check_arxiv_rate_limit.py
import arxiv
import requests

def check_arxiv(max_results=1):
    try:
        search = arxiv.Search(
            query="all:time",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        client = arxiv.Client()
        first = next(client.results(search), None)
        if first:
            print("✅ arXiv 可正常访问，示例论文标题：", first.title)
        else:
            print("⚠️ 没拿到结果，可能被限流或网络异常")
    except requests.exceptions.HTTPError as e:
        # 常见 403/429
        print("❌ HTTP 错误，可能被限流：", e)
    except Exception as e:
        print("❌ 其它错误：", e)

if __name__ == "__main__":
    check_arxiv()