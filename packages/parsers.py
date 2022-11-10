import wikipedia as wiki


def parse_wiki(query:str) -> list:
    wiki.set_lang("en")
    search_results = wiki.search(query, results=1)

    try:
        page = wiki.page(search_results, auto_suggest=False)
        return page.content, page.url

    except IndexError:
        return None

    except wiki.PageError:
        return None

    except wiki.DisambiguationError as e:
        page = wiki.page(e.options[0], auto_suggest=False)
        return page.content, page.url